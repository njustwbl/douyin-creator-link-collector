"""CareerAgent 一键安装、依赖更新与启动脚本。

只使用 Python 标准库，因此在项目虚拟环境尚未创建时也能运行。
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import venv
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
REQUIREMENTS = ROOT / "requirements.txt"
REQUIREMENTS_MARKER = VENV_DIR / ".requirements.sha256"
PLAYWRIGHT_MARKER = VENV_DIR / ".playwright_chromium_installed"
BOOTSTRAP_LOG = ROOT / "data" / "logs" / "bootstrap.log"


def venv_python() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def write_bootstrap_log(message: str) -> None:
    BOOTSTRAP_LOG.parent.mkdir(parents=True, exist_ok=True)
    with BOOTSTRAP_LOG.open("a", encoding="utf-8") as file:
        file.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")


def run(args: list[str]) -> None:
    write_bootstrap_log("RUN " + " ".join(args))
    process = subprocess.Popen(
        args,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
        write_bootstrap_log(line.rstrip())
    return_code = process.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, args)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ensure_requirements_file() -> None:
    if not REQUIREMENTS.is_file():
        raise FileNotFoundError(
            f"Missing dependency file: {REQUIREMENTS}\n"
            "Please download and extract the complete release package again."
        )


def ensure_virtual_environment() -> Path:
    python = venv_python()
    if python.is_file():
        print("[1/4] Runtime environment already exists.")
        return python

    print("[1/4] Creating runtime environment...")
    venv.EnvBuilder(with_pip=True, clear=False).create(VENV_DIR)
    python = venv_python()
    if not python.is_file():
        raise RuntimeError("Virtual environment creation failed.")
    return python


def ensure_dependencies(python: Path) -> None:
    expected_hash = file_sha256(REQUIREMENTS)
    installed_hash = (
        REQUIREMENTS_MARKER.read_text(encoding="utf-8").strip()
        if REQUIREMENTS_MARKER.is_file()
        else ""
    )

    if expected_hash == installed_hash:
        print("[2/4] Project dependencies are up to date.")
        return

    print("[2/4] Installing or updating project dependencies...")
    run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS)])
    REQUIREMENTS_MARKER.write_text(expected_hash, encoding="utf-8")


def ensure_playwright_browser(python: Path) -> None:
    if PLAYWRIGHT_MARKER.is_file():
        print("[3/4] Chromium is already installed.")
        return

    print("[3/4] Installing Chromium for Playwright...")
    run([str(python), "-m", "playwright", "install", "chromium"])
    PLAYWRIGHT_MARKER.write_text("installed\n", encoding="utf-8")


def launch(python: Path) -> None:
    print("[4/4] Starting CareerAgent Collector...")
    print("The management page will open automatically in your browser.")
    run([str(python), "-m", "app.launcher"])


def main() -> int:
    write_bootstrap_log("CareerAgent bootstrap started")
    try:
        ensure_requirements_file()
        python = ensure_virtual_environment()
        ensure_dependencies(python)
        ensure_playwright_browser(python)
        launch(python)
        write_bootstrap_log("CareerAgent stopped normally")
        return 0
    except KeyboardInterrupt:
        print("\nStopped by user.")
        write_bootstrap_log("Stopped by user")
        return 130
    except subprocess.CalledProcessError as exc:
        print(f"\nA command failed with exit code {exc.returncode}.")
        write_bootstrap_log(f"Command failed with exit code {exc.returncode}: {exc.cmd}")
        return exc.returncode or 1
    except Exception as exc:
        print(f"\nStartup failed: {exc}")
        write_bootstrap_log(f"Startup failed: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
