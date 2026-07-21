"""安全恢复 CareerAgent 托管的 Docker PostgreSQL 数据库。"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from backup_postgres import backup
from careeragent_location import ensure_location_configuration
from database_bootstrap import _read_env_file, ensure_database_runtime

from alembic.config import Config
from alembic.script import ScriptDirectory

ROOT = Path(__file__).resolve().parent


def _choose_dump(default_dir: Path) -> Path | None:
    if os.name == "nt":
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            selected = filedialog.askopenfilename(
                title="选择要恢复的 CareerAgent PostgreSQL 备份",
                initialdir=str(default_dir),
                filetypes=[("PostgreSQL custom dump", "*.dump"), ("All files", "*.*")],
            )
            root.destroy()
            return Path(selected) if selected else None
        except Exception as exc:
            print(f"Windows 文件选择器不可用，将改用最新备份文件：{type(exc).__name__}: {exc}")
    dumps = sorted(default_dir.glob("*.dump"), key=lambda item: item.stat().st_mtime, reverse=True)
    return dumps[0] if dumps else None


def _quote_identifier(value: str) -> str:
    return '"' + str(value).replace('"', '""') + '"'


def _quote_literal(value: str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def _alembic_head() -> str:
    config = Config(str(ROOT / "alembic.ini"))
    script = ScriptDirectory.from_config(config)
    return str(script.get_current_head() or "")


def _database_url(user: str, password: str, database: str, port: int) -> str:
    return (
        "postgresql+asyncpg://"
        f"{quote(user, safe='')}:{quote(password, safe='')}@127.0.0.1:{int(port)}/"
        f"{quote(database, safe='')}"
    )


def _run(command: list[str], *, env: dict[str, str], input_file: Path | None = None) -> subprocess.CompletedProcess:
    if input_file is None:
        return subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, check=False)
    with input_file.open("rb") as stream:
        return subprocess.run(command, cwd=ROOT, env=env, stdin=stream, capture_output=True, check=False)


def _psql(docker: str, container: str, user: str, database: str, password: str, sql: str, *, database_override: str | None = None) -> str:
    target = database_override or database
    completed = _run(
        [
            docker,
            "exec",
            "-e",
            f"PGPASSWORD={password}",
            container,
            "psql",
            "-U",
            user,
            "-d",
            target,
            "-v",
            "ON_ERROR_STOP=1",
            "-At",
            "-c",
            sql,
        ],
        env=os.environ.copy(),
    )
    if completed.returncode:
        detail = (completed.stderr or completed.stdout or b"").decode("utf-8", errors="replace") if isinstance(completed.stderr, bytes) else (completed.stderr or completed.stdout or "")
        raise RuntimeError(detail.strip() or "psql command failed")
    output = completed.stdout.decode("utf-8", errors="replace") if isinstance(completed.stdout, bytes) else completed.stdout
    return (output or "").strip()


def _verify_dump(docker: str, container: str, dump_path: Path, env: dict[str, str]) -> None:
    completed = _run(
        [docker, "exec", "-i", container, "pg_restore", "--list"],
        env=env,
        input_file=dump_path,
    )
    if completed.returncode:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"备份文件无法被 pg_restore 读取：{detail or 'unknown error'}")
    listing = completed.stdout.decode("utf-8", errors="replace")
    if "TABLE" not in listing or "alembic_version" not in listing:
        raise RuntimeError("备份文件缺少业务表或 alembic_version，已拒绝恢复。")


def _create_database(
    docker: str, container: str, user: str, admin_database: str, password: str, database: str
) -> None:
    _psql(
        docker,
        container,
        user,
        admin_database,
        password,
        f"CREATE DATABASE {_quote_identifier(database)} OWNER {_quote_identifier(user)};",
        database_override="postgres",
    )


def _drop_database(
    docker: str, container: str, user: str, admin_database: str, password: str, database: str
) -> None:
    _psql(
        docker,
        container,
        user,
        admin_database,
        password,
        (
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            f"WHERE datname={_quote_literal(database)} AND pid <> pg_backend_pid();"
        ),
        database_override="postgres",
    )
    _psql(
        docker,
        container,
        user,
        admin_database,
        password,
        f"DROP DATABASE IF EXISTS {_quote_identifier(database)};",
        database_override="postgres",
    )


def _restore_dump(
    docker: str,
    container: str,
    user: str,
    password: str,
    database: str,
    dump_path: Path,
    env: dict[str, str],
) -> None:
    completed = _run(
        [
            docker,
            "exec",
            "-i",
            "-e",
            f"PGPASSWORD={password}",
            container,
            "pg_restore",
            "-U",
            user,
            "-d",
            database,
            "--no-owner",
            "--no-privileges",
            "--exit-on-error",
        ],
        env=env,
        input_file=dump_path,
    )
    if completed.returncode:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"PostgreSQL 恢复失败：{detail or 'unknown error'}")


def _upgrade_database(user: str, password: str, database: str, port: int, env: dict[str, str]) -> None:
    migration_env = env.copy()
    migration_env["DATABASE_URL"] = _database_url(user, password, database, port)
    completed = _run(
        [sys.executable, "-m", "alembic", "-c", str(ROOT / "alembic.ini"), "upgrade", "head"],
        env=migration_env,
    )
    if completed.returncode:
        detail = completed.stderr or completed.stdout or "unknown error"
        raise RuntimeError(f"恢复后的数据库迁移失败：{str(detail).strip()}")


def _counts(docker: str, container: str, user: str, database: str, password: str) -> dict[str, int | str]:
    queries = {
        "alembic_revision": "SELECT COALESCE((SELECT version_num FROM alembic_version LIMIT 1), '');",
        "intelligence_documents": "SELECT COUNT(*) FROM intelligence_documents;",
        "knowledge_preparations": "SELECT COUNT(*) FROM knowledge_preparations;",
        "embedding_profiles": "SELECT COUNT(*) FROM embedding_index_profiles;",
        "claims": "SELECT COUNT(*) FROM intelligence_claims;",
        "claim_clusters": "SELECT COUNT(*) FROM intelligence_claim_clusters;",
        "canonical_events": "SELECT COUNT(*) FROM intelligence_canonical_events;",
        "reports": "SELECT COUNT(*) FROM intelligence_reports;",
    }
    result: dict[str, int | str] = {}
    for key, sql in queries.items():
        try:
            value = _psql(docker, container, user, database, password, sql)
            result[key] = value if key == "alembic_revision" else int(value or 0)
        except Exception:
            result[key] = "unavailable"
    return result


def restore(dump_path: Path, *, yes: bool = False) -> dict[str, object]:
    location = ensure_location_configuration(ROOT, interactive=True)
    runtime = ensure_database_runtime(location.app_home_path)
    if runtime.mode != "postgres" or not runtime.managed_by_docker or runtime.config_path is None:
        raise RuntimeError("当前不是 CareerAgent 托管的 Docker PostgreSQL，无法使用此恢复脚本。")
    docker = shutil.which("docker")
    if not docker:
        raise RuntimeError("未检测到 Docker 命令。")
    dump_path = dump_path.expanduser().resolve()
    if not dump_path.is_file():
        raise RuntimeError(f"备份文件不存在：{dump_path}")

    values = _read_env_file(runtime.config_path)
    container = values["CAREERAGENT_POSTGRES_CONTAINER"]
    user = values["CAREERAGENT_POSTGRES_USER"]
    password = values["CAREERAGENT_POSTGRES_PASSWORD"]
    database = values["CAREERAGENT_POSTGRES_DB"]
    port = int(values["CAREERAGENT_POSTGRES_PORT"])
    env = os.environ.copy()
    expected_head = _alembic_head()

    _verify_dump(docker, container, dump_path, env)

    # 先恢复到临时数据库并执行全部迁移。只有预检通过，才允许覆盖正式数据库。
    temporary_database = f"careeragent_restore_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    preflight_counts: dict[str, int | str] = {}
    try:
        _drop_database(docker, container, user, database, password, temporary_database)
        _create_database(docker, container, user, database, password, temporary_database)
        _restore_dump(docker, container, user, password, temporary_database, dump_path, env)
        _upgrade_database(user, password, temporary_database, port, env)
        preflight_counts = _counts(docker, container, user, temporary_database, password)
        if preflight_counts.get("alembic_revision") != expected_head:
            raise RuntimeError(
                "临时恢复数据库的 Alembic revision 校验失败："
                f"实际={preflight_counts.get('alembic_revision')}，要求={expected_head}"
            )
        unavailable = [key for key, value in preflight_counts.items() if value == "unavailable"]
        if unavailable:
            raise RuntimeError(f"临时恢复数据库缺少关键表：{', '.join(unavailable)}")
    finally:
        try:
            _drop_database(docker, container, user, database, password, temporary_database)
        except Exception as exc:
            print(f"清理临时恢复数据库失败，请稍后手工检查：{type(exc).__name__}: {exc}")

    before_counts = _counts(docker, container, user, database, password)
    safety_backup = backup()

    if not yes:
        print("\n备份文件已通过临时数据库恢复与迁移校验。")
        print("即将用以下备份覆盖当前数据库：")
        print(f"  {dump_path}")
        print(f"恢复前安全备份：{safety_backup['path']}")
        answer = input("确认已关闭 CareerAgent 主程序并继续恢复？请输入 RESTORE：").strip()
        if answer != "RESTORE":
            raise RuntimeError("用户取消恢复。")

    try:
        _drop_database(docker, container, user, database, password, database)
        _create_database(docker, container, user, database, password, database)
        _restore_dump(docker, container, user, password, database, dump_path, env)
        _upgrade_database(user, password, database, port, env)
        after_counts = _counts(docker, container, user, database, password)
        if after_counts.get("alembic_revision") != expected_head:
            raise RuntimeError(
                "正式数据库恢复后的 Alembic revision 校验失败："
                f"实际={after_counts.get('alembic_revision')}，要求={expected_head}"
            )
        unavailable = [key for key, value in after_counts.items() if value == "unavailable"]
        if unavailable:
            raise RuntimeError(f"正式数据库恢复后缺少关键表：{', '.join(unavailable)}")
    except Exception as exc:
        raise RuntimeError(
            "正式数据库恢复未通过最终校验。请使用恢复前安全备份恢复。"
            f"\n安全备份：{safety_backup['path']}\n原因：{exc}"
        ) from exc

    report = {
        "ok": True,
        "restored_from": str(dump_path),
        "restored_bytes": dump_path.stat().st_size,
        "safety_backup": safety_backup["path"],
        "expected_alembic_revision": expected_head,
        "preflight": preflight_counts,
        "before": before_counts,
        "after": after_counts,
        "completed_at": datetime.now().isoformat(timespec="seconds"),
    }
    report_dir = location.app_home_path / "backups" / "restore_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["report_path"] = str(report_path)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore CareerAgent PostgreSQL backup")
    parser.add_argument("--file", default="", help="Path to .dump file")
    parser.add_argument("--yes", action="store_true", help="Skip RESTORE confirmation")
    args = parser.parse_args()
    try:
        location = ensure_location_configuration(ROOT, interactive=True)
        default_dir = location.app_home_path / "backups" / "postgres"
        selected = Path(args.file) if args.file else _choose_dump(default_dir)
        if selected is None:
            raise RuntimeError(f"没有选择备份文件；默认目录：{default_dir}")
        print(json.dumps(restore(selected, yes=args.yes), ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
