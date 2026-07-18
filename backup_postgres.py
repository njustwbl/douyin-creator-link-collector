"""备份 CareerAgent 托管的 PostgreSQL 数据库为 pg_dump custom 文件。"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from careeragent_location import ensure_location_configuration
from database_bootstrap import _read_env_file, ensure_database_runtime

ROOT = Path(__file__).resolve().parent


def backup() -> dict[str, str | int | bool]:
    location = ensure_location_configuration(ROOT, interactive=True)
    runtime = ensure_database_runtime(location.app_home_path)
    if runtime.mode != "postgres" or not runtime.managed_by_docker or runtime.config_path is None:
        raise RuntimeError("当前不是 CareerAgent 托管的 Docker PostgreSQL，无法使用此备份脚本。")
    docker = shutil.which("docker")
    if not docker:
        raise RuntimeError("未检测到 Docker 命令。")
    values = _read_env_file(runtime.config_path)
    container = values["CAREERAGENT_POSTGRES_CONTAINER"]
    user = values["CAREERAGENT_POSTGRES_USER"]
    password = values["CAREERAGENT_POSTGRES_PASSWORD"]
    database = values["CAREERAGENT_POSTGRES_DB"]
    backup_dir = location.app_home_path / "backups" / "postgres"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = backup_dir / f"careeragent_{timestamp}.dump"
    with output.open("wb") as file:
        completed = subprocess.run(
            [
                docker,
                "exec",
                "-e",
                f"PGPASSWORD={password}",
                container,
                "pg_dump",
                "-U",
                user,
                "-d",
                database,
                "--format=custom",
                "--no-owner",
                "--no-privileges",
            ],
            cwd=ROOT,
            stdout=file,
            stderr=subprocess.PIPE,
            env=os.environ.copy(),
            check=False,
        )
    if completed.returncode:
        output.unlink(missing_ok=True)
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"PostgreSQL 备份失败：{detail or 'unknown error'}")
    return {"ok": True, "path": str(output), "bytes": output.stat().st_size}


def main() -> int:
    try:
        print(json.dumps(backup(), ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
