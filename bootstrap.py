"""CareerAgent 一键环境管理、依赖更新与启动脚本。

v0.5.4 起，启动器会根据硬件自动选择 PyTorch CPU/CUDA 版本：
- 检测到可用 NVIDIA 驱动：优先安装官方 cu128 PyTorch wheel；
- 没有 NVIDIA GPU：安装官方 CPU wheel；
- GPU 安装或自检失败：允许自动退回 CPU，保证程序仍可运行。

脚本只依赖 Python 标准库，因此虚拟环境尚未创建时也可以执行。
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import venv
from datetime import datetime
from pathlib import Path
from typing import Any

from careeragent_location import ensure_location_configuration, format_bytes, free_space_bytes

ROOT = Path(__file__).resolve().parent

# 在任何数 GB 依赖下载之前先让用户确认存储位置。位置配置保存在一个很小的
# system location.json 中，运行环境和模型本身则写入用户选择的磁盘。
try:
    LOCATION = ensure_location_configuration(ROOT, interactive=__name__ == "__main__")
except KeyboardInterrupt:
    print("Storage setup was cancelled. No large files were downloaded.")
    raise SystemExit(130)
APP_HOME = LOCATION.app_home_path
EXPORT_DIR = LOCATION.export_dir_path
os.environ["CAREER_AGENT_HOME"] = str(APP_HOME)
os.environ["CAREER_AGENT_EXPORT_DIR"] = str(EXPORT_DIR)

LOCAL_VENV_DIR = ROOT / ".venv"
# 配置完成后，新版始终把大体积运行环境放到所选数据目录。只有显式开启兼容
# 开关时才继续使用旧项目根目录中的 .venv。
USE_LEGACY_LOCAL_VENV = os.environ.get("CAREERAGENT_USE_LEGACY_LOCAL_VENV", "").strip().lower() in {
    "1", "true", "yes", "on"
}
VENV_DIR = (
    LOCAL_VENV_DIR
    if USE_LEGACY_LOCAL_VENV and LOCAL_VENV_DIR.exists()
    else APP_HOME / "runtime" / "venv"
)
REQUIREMENTS = ROOT / "requirements.txt"
ASR_REQUIREMENTS = ROOT / "requirements-asr.txt"
REQUIREMENTS_MARKER = VENV_DIR / ".requirements.sha256"
ASR_REQUIREMENTS_MARKER = VENV_DIR / ".requirements-asr.sha256"
TORCH_RUNTIME_MARKER = VENV_DIR / ".torch-runtime.json"
PLAYWRIGHT_MARKER = VENV_DIR / ".playwright_chromium_installed"
BOOTSTRAP_LOG = APP_HOME / "logs" / "bootstrap.log"
COMPUTE_REPORT = APP_HOME / "runtime" / "compute_environment.json"

DEFAULT_CUDA_INDEX = "https://download.pytorch.org/whl/cu128"
DEFAULT_CPU_INDEX = "https://download.pytorch.org/whl/cpu"



def print_storage_plan() -> None:
    free = free_space_bytes(APP_HOME)
    print("=" * 68)
    print("CareerAgent storage plan")
    print(f"  Runtime / CUDA / Python: {VENV_DIR}")
    print(f"  Models:                 {APP_HOME / 'models'}")
    print(f"  Database / login data:  {APP_HOME}")
    print(f"  Temporary media cache:  {APP_HOME / 'cache' / 'media'}")
    print(f"  Word / TXT exports:     {EXPORT_DIR}")
    print(f"  Available disk space:   {format_bytes(free)}")
    print("  Estimated on-demand use: runtime 4-7 GB, models 1-5 GB, cache up to 2 GB")
    print("=" * 68)
    write_bootstrap_log(
        f"Storage plan app_home={APP_HOME} export_dir={EXPORT_DIR} venv={VENV_DIR} free={free}"
    )


def venv_python() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def write_bootstrap_log(message: str) -> None:
    BOOTSTRAP_LOG.parent.mkdir(parents=True, exist_ok=True)
    with BOOTSTRAP_LOG.open("a", encoding="utf-8") as file:
        file.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")


def run(
    args: list[str],
    *,
    check: bool = True,
    capture: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    write_bootstrap_log("RUN " + " ".join(args))
    if capture:
        completed = subprocess.run(
            args,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        if completed.stdout:
            write_bootstrap_log(completed.stdout.rstrip())
        if completed.stderr:
            write_bootstrap_log(completed.stderr.rstrip())
        if check and completed.returncode:
            raise subprocess.CalledProcessError(
                completed.returncode,
                args,
                output=completed.stdout,
                stderr=completed.stderr,
            )
        return completed

    process = subprocess.Popen(
        args,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    assert process.stdout is not None
    output: list[str] = []
    for line in process.stdout:
        print(line, end="")
        output.append(line)
        write_bootstrap_log(line.rstrip())
    return_code = process.wait()
    if check and return_code:
        raise subprocess.CalledProcessError(return_code, args, output="".join(output))
    return subprocess.CompletedProcess(args, return_code, "".join(output), "")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_env_file() -> dict[str, str]:
    values: dict[str, str] = {}
    path = ROOT / ".env"
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip().upper()] = value.strip().strip('"').strip("'")
    return values


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name) or read_env_file().get(name.upper(), default)


def env_bool(name: str, default: bool) -> bool:
    raw = env_value(name, "true" if default else "false").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def ensure_requirements_files() -> None:
    missing = [path for path in (REQUIREMENTS, ASR_REQUIREMENTS) if not path.is_file()]
    if missing:
        joined = "\n".join(str(path) for path in missing)
        raise FileNotFoundError(
            f"Missing dependency file(s):\n{joined}\n"
            "Please download and extract the complete release package again."
        )


def ensure_virtual_environment() -> Path:
    python = venv_python()
    if python.is_file():
        print("[1/7] Runtime environment already exists.")
        return python

    print(f"[1/7] Creating runtime environment at {VENV_DIR}...")
    VENV_DIR.parent.mkdir(parents=True, exist_ok=True)
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
        print("[2/7] Project dependencies are up to date.")
        return

    print("[2/7] Installing or updating project dependencies...")
    run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS)])
    REQUIREMENTS_MARKER.write_text(expected_hash, encoding="utf-8")


def detect_nvidia_gpu() -> dict[str, Any]:
    command = shutil.which("nvidia-smi")
    if not command:
        return {"available": False, "reason": "nvidia-smi not found"}
    completed = run(
        [
            command,
            "--query-gpu=name,driver_version,memory.total",
            "--format=csv,noheader,nounits",
        ],
        check=False,
        capture=True,
    )
    first = next((line.strip() for line in completed.stdout.splitlines() if line.strip()), "")
    if completed.returncode or not first:
        return {"available": False, "reason": "nvidia-smi returned no GPU"}
    parts = [part.strip() for part in first.split(",")]
    return {
        "available": True,
        "name": parts[0] if parts else "NVIDIA GPU",
        "driver_version": parts[1] if len(parts) > 1 else "",
        "memory_mb": int(float(parts[2])) if len(parts) > 2 and parts[2] else None,
    }


def inspect_torch(python: Path) -> dict[str, Any]:
    script = r"""
import json
try:
    import torch
    import torchaudio
    result = {
        "installed": True,
        "version": str(torch.__version__),
        "torchaudio_version": str(torchaudio.__version__),
        "compiled_cuda": str(torch.version.cuda or ""),
        "cuda_available": bool(torch.cuda.is_available()),
        "device_name": str(torch.cuda.get_device_name(0)) if torch.cuda.is_available() else "",
    }
except Exception as exc:
    result = {"installed": False, "error": f"{type(exc).__name__}: {exc}"}
print(json.dumps(result, ensure_ascii=False))
"""
    completed = run([str(python), "-c", script], check=False, capture=True)
    try:
        line = next(line for line in reversed(completed.stdout.splitlines()) if line.strip())
        return json.loads(line)
    except Exception:
        return {
            "installed": False,
            "error": (completed.stderr or completed.stdout or "torch inspection failed").strip(),
        }


def desired_accelerator(nvidia: dict[str, Any]) -> str:
    requested = env_value("CAREERAGENT_ACCELERATOR", "auto").strip().lower()
    if requested not in {"auto", "cpu", "cuda"}:
        requested = "auto"
    if requested == "cpu":
        return "cpu"
    if requested == "cuda":
        return "cuda"
    return "cuda" if nvidia.get("available") else "cpu"


def torch_satisfies(status: dict[str, Any], desired: str) -> bool:
    if not status.get("installed") or not status.get("torchaudio_version"):
        return False
    if desired == "cuda":
        return bool(status.get("cuda_available") and status.get("compiled_cuda"))
    # CUDA 版 PyTorch 也可以运行 CPU，因此显式 CPU 模式不强制卸载可用 CUDA 包。
    return True


def install_torch(python: Path, target: str) -> dict[str, Any]:
    index_url = (
        env_value("PYTORCH_CUDA_INDEX_URL", DEFAULT_CUDA_INDEX)
        if target == "cuda"
        else env_value("PYTORCH_CPU_INDEX_URL", DEFAULT_CPU_INDEX)
    )
    print(f"      Installing PyTorch target: {target} ({index_url})")
    run(
        [
            str(python),
            "-m",
            "pip",
            "uninstall",
            "-y",
            "torch",
            "torchaudio",
            "torchvision",
        ],
        check=False,
    )
    run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "torch",
            "torchaudio",
            "--index-url",
            index_url,
        ]
    )
    return inspect_torch(python)


def ensure_torch_runtime(python: Path) -> dict[str, Any]:
    print("[3/7] Detecting compute device and PyTorch runtime...")
    nvidia = detect_nvidia_gpu()
    desired = desired_accelerator(nvidia)
    current = inspect_torch(python)
    allow_cpu_fallback = env_bool("CAREERAGENT_ALLOW_CPU_FALLBACK", True)

    if nvidia.get("available"):
        print(
            f"      NVIDIA GPU: {nvidia.get('name')} | driver {nvidia.get('driver_version')} | "
            f"VRAM {nvidia.get('memory_mb') or '?'} MB"
        )
    else:
        print("      NVIDIA GPU was not detected; CPU mode will be used.")

    if torch_satisfies(current, desired):
        mode = "CUDA" if current.get("cuda_available") else "CPU"
        print(f"      PyTorch is ready: {current.get('version')} | {mode}")
        result = {"desired": desired, "actual": mode.lower(), "nvidia": nvidia, "torch": current}
        TORCH_RUNTIME_MARKER.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result

    try:
        installed = install_torch(python, desired)
    except Exception as exc:
        if desired != "cuda" or not allow_cpu_fallback:
            raise
        print("      WARNING: CUDA PyTorch installation failed; falling back to CPU.")
        write_bootstrap_log(f"CUDA PyTorch install failed: {type(exc).__name__}: {exc}")
        installed = install_torch(python, "cpu")
        desired = "cpu"

    if desired == "cuda" and not installed.get("cuda_available"):
        detail = installed.get("error") or json.dumps(installed, ensure_ascii=False)
        if not allow_cpu_fallback:
            raise RuntimeError(f"CUDA PyTorch self-test failed: {detail}")
        print("      WARNING: CUDA PyTorch self-test failed; installing CPU runtime instead.")
        write_bootstrap_log(f"CUDA PyTorch self-test failed: {detail}")
        installed = install_torch(python, "cpu")
        desired = "cpu"

    if not installed.get("installed"):
        raise RuntimeError(f"PyTorch installation failed: {installed.get('error', 'unknown error')}")

    actual = "cuda" if installed.get("cuda_available") else "cpu"
    print(f"      PyTorch ready: {installed.get('version')} | {actual.upper()}")
    result = {"desired": desired, "actual": actual, "nvidia": nvidia, "torch": installed}
    TORCH_RUNTIME_MARKER.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def ensure_asr_dependencies(python: Path) -> None:
    expected_hash = file_sha256(ASR_REQUIREMENTS)
    installed_hash = (
        ASR_REQUIREMENTS_MARKER.read_text(encoding="utf-8").strip()
        if ASR_REQUIREMENTS_MARKER.is_file()
        else ""
    )
    if expected_hash == installed_hash:
        print("[4/7] ASR and OCR dependencies are up to date.")
        return

    print("[4/7] Installing local ASR and OCR dependencies...")
    print("      First installation is large and may take several minutes.")
    try:
        run([str(python), "-m", "pip", "install", "-r", str(ASR_REQUIREMENTS)])
    except subprocess.CalledProcessError as exc:
        print("      WARNING: ASR/OCR dependencies were not installed completely.")
        print("      Collection features can still start; content processing will show a clear error.")
        write_bootstrap_log(f"ASR/OCR dependency installation failed: {exc.cmd}")
        return
    ASR_REQUIREMENTS_MARKER.write_text(expected_hash, encoding="utf-8")


def ensure_playwright_browser(python: Path) -> None:
    if PLAYWRIGHT_MARKER.is_file():
        print("[5/7] Chromium is already installed.")
        return

    print("[5/7] Installing Chromium for Playwright...")
    run([str(python), "-m", "playwright", "install", "chromium"])
    PLAYWRIGHT_MARKER.write_text("installed\n", encoding="utf-8")


def write_compute_report(python: Path) -> None:
    print("[6/7] Verifying compute environment...")
    completed = run(
        [str(python), "-m", "app.core.compute"],
        check=False,
        capture=True,
    )
    COMPUTE_REPORT.parent.mkdir(parents=True, exist_ok=True)
    output = completed.stdout.strip()
    if output:
        COMPUTE_REPORT.write_text(output + "\n", encoding="utf-8")
        try:
            report = json.loads(output)
            engines = report.get("engines", {})
            print(
                "      SenseVoice: {sense} | Paraformer: {para} | Whisper: {whisper}".format(
                    sense=engines.get("sensevoice", {}).get("device", "unknown"),
                    para=engines.get("paraformer", {}).get("device", "unknown"),
                    whisper=engines.get("whisper", {}).get("device", "unknown"),
                )
            )
            for issue in report.get("issues", []):
                print(f"      WARNING: {issue}")
        except Exception:
            print("      WARNING: Compute report could not be parsed; see bootstrap.log.")
    else:
        print("      WARNING: Compute environment verification produced no output.")


def launch(python: Path) -> None:
    print("[7/7] Starting CareerAgent...")
    print("The management page will open automatically in your browser.")
    run([str(python), "-m", "app.launcher"])


def main() -> int:
    write_bootstrap_log("CareerAgent bootstrap started")
    try:
        print_storage_plan()
        ensure_requirements_files()
        python = ensure_virtual_environment()
        ensure_dependencies(python)
        ensure_torch_runtime(python)
        ensure_asr_dependencies(python)
        ensure_playwright_browser(python)
        write_compute_report(python)
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
