"""CareerAgent PostgreSQL + pgvector 本地运行环境管理。

本模块只依赖 Python 标准库，供 bootstrap.py 在虚拟环境尚未完成前调用。
默认正式模式使用 Docker Desktop 启动 PostgreSQL + pgvector；显式设置
CAREERAGENT_DATABASE_MODE=sqlite 可继续使用轻量 SQLite。
"""
from __future__ import annotations

import json
import os
import secrets
import shutil
import string
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent
COMPOSE_FILE = ROOT / "docker-compose.yml"


@dataclass(frozen=True, slots=True)
class DatabaseRuntime:
    mode: str
    database_url: str
    environment: dict[str, str]
    managed_by_docker: bool = False
    config_path: Path | None = None


def _read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip().upper()] = value.strip().strip('"').strip("'")
    return values


def _env_value(name: str, default: str = "") -> str:
    return os.environ.get(name) or _read_env_file(ROOT / ".env").get(name.upper(), default)


def _random_password(length: int = 32) -> str:
    # URL、dotenv 和 Compose 都安全的字符集合，避免额外转义问题。
    alphabet = string.ascii_letters + string.digits + "_-"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _write_runtime_env(path: Path, values: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(f"{key}={value}" for key, value in values.items()) + "\n"
    path.write_text(payload, encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def _run(args: list[str], *, env: dict[str, str], check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        args,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and completed.returncode:
        detail = (completed.stderr or completed.stdout or "unknown error").strip()
        raise RuntimeError(f"命令执行失败：{' '.join(args)}\n{detail}")
    return completed


def _docker_command() -> str:
    command = shutil.which("docker")
    if not command:
        raise RuntimeError(
            "未检测到 Docker Desktop。请先安装并启动 Docker Desktop，"
            "或者在 .env 中设置 CAREERAGENT_DATABASE_MODE=sqlite 使用轻量模式。"
        )
    return command


def _compose_args(docker: str, config_path: Path) -> list[str]:
    return [docker, "compose", "--env-file", str(config_path), "-f", str(COMPOSE_FILE)]


def _ensure_docker_ready(docker: str, env: dict[str, str]) -> None:
    completed = _run([docker, "info"], env=env, check=False)
    if completed.returncode:
        raise RuntimeError(
            "Docker Desktop 已安装但尚未启动，或当前账户无法连接 Docker。"
            "请启动 Docker Desktop，等待状态显示 Running 后重试。"
        )
    completed = _run([docker, "compose", "version"], env=env, check=False)
    if completed.returncode:
        raise RuntimeError("当前 Docker 缺少 Compose v2，请更新 Docker Desktop。")


def normalize_async_database_url(url: str) -> str:
    """把常见 PostgreSQL URL 统一成 SQLAlchemy asyncpg URL。"""
    raw = str(url or "").strip()
    lower = raw.lower()
    prefixes = (
        "postgresql+psycopg2://",
        "postgresql+psycopg://",
        "postgresql://",
        "postgres://",
    )
    for prefix in prefixes:
        if lower.startswith(prefix):
            return "postgresql+asyncpg://" + raw[len(prefix):]
    return raw


def _postgres_url(user: str, password: str, database: str, port: int) -> str:
    return (
        "postgresql+asyncpg://"
        f"{quote_plus(user)}:{quote_plus(password)}@127.0.0.1:{port}/{quote_plus(database)}"
    )


def ensure_database_runtime(app_home: Path) -> DatabaseRuntime:
    explicit_url = _env_value("DATABASE_URL", "").strip()
    requested_mode = _env_value("CAREERAGENT_DATABASE_MODE", "postgres").strip().lower()

    if explicit_url:
        mode = "sqlite" if explicit_url.lower().startswith("sqlite") else "postgres"
        normalized_url = explicit_url if mode == "sqlite" else normalize_async_database_url(explicit_url)
        env = dict(os.environ)
        env["DATABASE_URL"] = normalized_url
        env["CAREERAGENT_DATABASE_MODE"] = mode
        return DatabaseRuntime(mode=mode, database_url=normalized_url, environment=env)

    if requested_mode in {"sqlite", "lightweight", "lite"}:
        # 不写 DATABASE_URL，让应用继续按用户选择的数据目录生成 SQLite URL。
        env = dict(os.environ)
        env["CAREERAGENT_DATABASE_MODE"] = "sqlite"
        return DatabaseRuntime(mode="sqlite", database_url="", environment=env)

    if requested_mode not in {"postgres", "postgresql", "standard"}:
        raise RuntimeError(
            "CAREERAGENT_DATABASE_MODE 只支持 postgres 或 sqlite，"
            f"当前值为 {requested_mode!r}。"
        )
    if not COMPOSE_FILE.is_file():
        raise RuntimeError(f"缺少数据库编排文件：{COMPOSE_FILE}")

    runtime_dir = app_home / "runtime"
    config_path = runtime_dir / "postgres.env"
    existing = _read_env_file(config_path)
    data_dir = app_home / "database" / "postgres"
    data_dir.mkdir(parents=True, exist_ok=True)

    values = {
        "CAREERAGENT_POSTGRES_USER": existing.get("CAREERAGENT_POSTGRES_USER", "careeragent"),
        "CAREERAGENT_POSTGRES_PASSWORD": existing.get(
            "CAREERAGENT_POSTGRES_PASSWORD", _random_password()
        ),
        "CAREERAGENT_POSTGRES_DB": existing.get("CAREERAGENT_POSTGRES_DB", "careeragent"),
        "CAREERAGENT_POSTGRES_PORT": existing.get("CAREERAGENT_POSTGRES_PORT", "54329"),
        "CAREERAGENT_POSTGRES_CONTAINER": existing.get(
            "CAREERAGENT_POSTGRES_CONTAINER", "careeragent-postgres"
        ),
        "CAREERAGENT_POSTGRES_DATA_DIR": data_dir.resolve().as_posix(),
    }
    _write_runtime_env(config_path, values)

    docker = _docker_command()
    env = dict(os.environ)
    env.update(values)
    _ensure_docker_ready(docker, env)
    compose = _compose_args(docker, config_path)
    print("      正在启动 PostgreSQL + pgvector...")
    _run([*compose, "up", "-d"], env=env)

    container = values["CAREERAGENT_POSTGRES_CONTAINER"]
    user = values["CAREERAGENT_POSTGRES_USER"]
    database = values["CAREERAGENT_POSTGRES_DB"]
    deadline = time.monotonic() + 120
    last_detail = ""
    while time.monotonic() < deadline:
        completed = _run(
            [docker, "exec", container, "pg_isready", "-U", user, "-d", database],
            env=env,
            check=False,
        )
        if completed.returncode == 0:
            break
        last_detail = (completed.stderr or completed.stdout or "").strip()
        time.sleep(2)
    else:
        logs = _run([*compose, "logs", "--tail", "80", "postgres"], env=env, check=False)
        detail = (logs.stdout or logs.stderr or last_detail).strip()
        raise RuntimeError(f"PostgreSQL 在 120 秒内未就绪。\n{detail}")

    port = int(values["CAREERAGENT_POSTGRES_PORT"])
    url = _postgres_url(user, values["CAREERAGENT_POSTGRES_PASSWORD"], database, port)
    env["DATABASE_URL"] = url
    env["CAREERAGENT_DATABASE_MODE"] = "postgres"
    env["CAREERAGENT_POSTGRES_CONFIG"] = str(config_path)
    return DatabaseRuntime(
        mode="postgres",
        database_url=url,
        environment=env,
        managed_by_docker=True,
        config_path=config_path,
    )


def database_status(app_home: Path) -> dict[str, object]:
    try:
        runtime = ensure_database_runtime(app_home)
        return {
            "ok": True,
            "mode": runtime.mode,
            "managed_by_docker": runtime.managed_by_docker,
            "database_url": runtime.database_url.split("@")[-1] if runtime.database_url else "sqlite",
        }
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    from careeragent_location import ensure_location_configuration

    location = ensure_location_configuration(ROOT, interactive=True)
    status = database_status(location.app_home_path)
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0 if status.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
