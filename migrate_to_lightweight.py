"""把旧版项目内 data 迁移到用户 AppData。

运行前必须关闭 CareerAgent。脚本只移动数据目录，不移动现有 .venv；如需让代码
文件夹也不再包含数 GB Python/CUDA 环境，可在迁移后删除 .venv 并重新启动，
启动器会在 AppData 中创建共享运行环境。
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data"
TARGET = (
    Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "CareerAgent"
    if os.name == "nt"
    else Path.home() / ".careeragent"
).resolve()


def merge_move(source: Path, target: Path) -> None:
    if not source.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_file():
        if target.exists():
            backup = target.with_suffix(target.suffix + ".before_migration")
            if not backup.exists():
                shutil.copy2(target, backup)
            target.unlink()
        shutil.move(str(source), str(target))
        return
    target.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        merge_move(child, target / child.name)
    try:
        source.rmdir()
    except OSError:
        pass


def update_env() -> None:
    path = ROOT / ".env"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines() if path.exists() else []
    values = {
        "CAREER_AGENT_HOME": str(TARGET),
        "DATABASE_URL": f"sqlite+aiosqlite:///{(TARGET / 'database' / 'career_agent.db').as_posix()}",
        "DOUYIN_BROWSER_PROFILE_DIR": str(TARGET / "browser" / "douyin"),
        "DOUYIN_SESSION_SNAPSHOT_PATH": str(TARGET / "browser" / "douyin_session.json"),
        "LOG_DIR": str(TARGET / "logs"),
        "TRANSCRIPTION_MEDIA_DIR": str(TARGET / "cache" / "media"),
        "ASR_MODEL_CACHE_DIR": str(TARGET / "models"),
    }
    output: list[str] = []
    replaced: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            output.append(line)
            continue
        key = stripped.split("=", 1)[0].strip().upper()
        if key in values:
            output.append(f"{key}={values[key]}")
            replaced.add(key)
        else:
            output.append(line)
    if output and output[-1].strip():
        output.append("")
    output.append("# v0.6.1 lightweight storage")
    for key, value in values.items():
        if key not in replaced:
            output.append(f"{key}={value}")
    path.write_text("\n".join(output) + "\n", encoding="utf-8")


def main() -> int:
    print(f"Source: {SOURCE}")
    print(f"Target: {TARGET}")
    if not SOURCE.exists():
        print("No legacy data directory was found. Only the .env path will be updated.")
    TARGET.mkdir(parents=True, exist_ok=True)
    mapping = [
        (SOURCE / "career_agent.db", TARGET / "database" / "career_agent.db"),
        (SOURCE / "browser", TARGET / "browser"),
        (SOURCE / "models", TARGET / "models"),
        (SOURCE / "media", TARGET / "cache" / "media"),
        (SOURCE / "logs", TARGET / "logs"),
        (SOURCE / "diagnostics", TARGET / "diagnostics"),
        (SOURCE / "runtime", TARGET / "runtime"),
    ]
    for source, target in mapping:
        if source.exists():
            print(f"Moving {source.name} ...")
            merge_move(source, target)
    update_env()
    print("Migration completed.")
    print("Your database, login state and models are now outside the source-code directory.")
    print("Optional: delete the local .venv and restart once to rebuild the runtime in AppData.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
