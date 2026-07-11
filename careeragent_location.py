"""CareerAgent 持久化目录选择与位置配置。

该模块只依赖 Python 标准库，可在虚拟环境尚未创建时由 bootstrap.py 调用。
位置配置本身很小，固定保存在系统本地应用配置目录；真正占空间的运行环境、
模型、数据库、缓存和导出结果可以由用户放在任意磁盘。
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

CONFIG_VERSION = 1
CONFIG_FILENAME = "location.json"


@dataclass(slots=True)
class LocationConfig:
    app_home: str
    export_dir: str
    configured_at: str
    configured_by: str = "setup_wizard"
    large_download_notice_accepted: bool = True
    version: int = CONFIG_VERSION

    @property
    def app_home_path(self) -> Path:
        return Path(self.app_home).expanduser().resolve()

    @property
    def export_dir_path(self) -> Path:
        return Path(self.export_dir).expanduser().resolve()


def system_config_root() -> Path:
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "CareerAgent" / "config"
    return Path.home() / ".careeragent" / "config"


def location_config_path() -> Path:
    return system_config_root() / CONFIG_FILENAME


def read_location_config(path: Path | None = None) -> LocationConfig | None:
    target = path or location_config_path()
    if not target.is_file():
        return None
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
        app_home = str(payload.get("app_home") or "").strip()
        export_dir = str(payload.get("export_dir") or "").strip()
        if not app_home:
            return None
        if not export_dir:
            export_dir = str(Path(app_home) / "exports")
        return LocationConfig(
            app_home=app_home,
            export_dir=export_dir,
            configured_at=str(payload.get("configured_at") or ""),
            configured_by=str(payload.get("configured_by") or "location_file"),
            large_download_notice_accepted=bool(
                payload.get("large_download_notice_accepted", True)
            ),
            version=int(payload.get("version") or CONFIG_VERSION),
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return None


def save_location_config(
    app_home: Path,
    export_dir: Path,
    *,
    configured_by: str = "setup_wizard",
    accepted: bool = True,
    path: Path | None = None,
) -> LocationConfig:
    app_home = app_home.expanduser().resolve()
    export_dir = export_dir.expanduser().resolve()
    app_home.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)
    target = path or location_config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    config = LocationConfig(
        app_home=str(app_home),
        export_dir=str(export_dir),
        configured_at=datetime.now().isoformat(timespec="seconds"),
        configured_by=configured_by,
        large_download_notice_accepted=accepted,
    )
    temp = target.with_suffix(target.suffix + ".tmp")
    temp.write_text(json.dumps(asdict(config), ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(target)
    return config


def _read_dotenv_value(project_root: Path, name: str) -> str:
    path = project_root / ".env"
    if not path.is_file():
        return ""
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip().upper() == name.upper():
            return value.strip().strip('"').strip("'")
    return ""


def explicit_value(project_root: Path, names: tuple[str, ...]) -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    for name in names:
        value = _read_dotenv_value(project_root, name)
        if value:
            return value
    return ""


def legacy_data_root(project_root: Path) -> Path:
    return project_root / "data"


def meaningful_legacy_data(project_root: Path) -> bool:
    root = legacy_data_root(project_root)
    if not root.is_dir():
        return False
    meaningful = {"career_agent.db", "browser", "models", "media", "logs", "runtime", "database"}
    return any((root / name).exists() for name in meaningful)


def default_app_home(project_root: Path) -> Path:
    explicit = explicit_value(project_root, ("CAREER_AGENT_HOME", "CAREERAGENT_HOME"))
    if explicit:
        return Path(explicit).expanduser().resolve()
    saved = read_location_config()
    if saved:
        return saved.app_home_path
    if meaningful_legacy_data(project_root):
        return legacy_data_root(project_root).resolve()
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return (Path(os.environ["LOCALAPPDATA"]) / "CareerAgent").resolve()
    return (Path.home() / ".careeragent").resolve()


def default_export_dir(project_root: Path, app_home: Path | None = None) -> Path:
    explicit = explicit_value(
        project_root,
        ("CAREER_AGENT_EXPORT_DIR", "CAREERAGENT_EXPORT_DIR", "TRANSCRIPTION_EXPORT_DIR"),
    )
    if explicit:
        return Path(explicit).expanduser().resolve()
    saved = read_location_config()
    if saved:
        return saved.export_dir_path
    root = app_home or default_app_home(project_root)
    return (root / "exports").resolve()


def resolve_locations(project_root: Path) -> LocationConfig:
    app_home = default_app_home(project_root)
    export_dir = default_export_dir(project_root, app_home)
    saved = read_location_config()
    return LocationConfig(
        app_home=str(app_home),
        export_dir=str(export_dir),
        configured_at=saved.configured_at if saved else "",
        configured_by=(saved.configured_by if saved else "environment_or_default"),
        large_download_notice_accepted=(
            saved.large_download_notice_accepted if saved else False
        ),
    )


def validate_writable_directory(path: Path) -> tuple[bool, str]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".careeragent_write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True, ""
    except OSError as exc:
        return False, f"目录不可写：{exc}"


def free_space_bytes(path: Path) -> int:
    candidate = path
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    try:
        return int(shutil.disk_usage(candidate).free)
    except OSError:
        return 0


def format_bytes(value: int) -> str:
    size = float(max(0, value))
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} TB"


def choose_directory_native(initial: Path, title: str) -> Path | None:
    if os.name == "nt":
        safe_initial = str(initial).replace("'", "''")
        safe_title = title.replace("'", "''")
        script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$dialog = New-Object System.Windows.Forms.FolderBrowserDialog; "
            f"$dialog.Description = '{safe_title}'; "
            f"$dialog.SelectedPath = '{safe_initial}'; "
            "$dialog.ShowNewFolderButton = $true; "
            "if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) "
            "{ [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            "Write-Output $dialog.SelectedPath }"
        )
        try:
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-STA", "-Command", script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            value = completed.stdout.strip().splitlines()
            if completed.returncode == 0 and value:
                return Path(value[-1]).expanduser().resolve()
            return None
        except OSError:
            pass
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        return None
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        value = filedialog.askdirectory(
            title=title,
            initialdir=str(initial if initial.exists() else initial.parent),
            mustexist=False,
            parent=root,
        )
    finally:
        root.destroy()
    return Path(value).expanduser().resolve() if value else None


def _setup_dialog(default_data: Path, default_export: Path) -> tuple[Path, Path] | None:
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError:
        return None

    result: dict[str, Path] = {}
    root = tk.Tk()
    root.title("CareerAgent 首次运行设置")
    root.geometry("720x560")
    root.minsize(680, 520)
    root.attributes("-topmost", True)

    data_var = tk.StringVar(value=str(default_data))
    export_var = tk.StringVar(value=str(default_export))

    frame = ttk.Frame(root, padding=24)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="选择 CareerAgent 存储位置", font=("Microsoft YaHei UI", 16, "bold")).pack(anchor="w")
    ttk.Label(
        frame,
        text=(
            "在下载 CUDA/PyTorch、语音模型和 OCR 模型前，请先指定存储目录。"
            "以后生成的 Word/TXT 也会保存到你设置的导出目录。"
        ),
        wraplength=650,
        justify="left",
    ).pack(anchor="w", pady=(8, 16))

    info = (
        "预计空间（按需下载，实际大小随模型版本变化）：\n"
        "• Python + CUDA/PyTorch 运行环境：约 4–7 GB\n"
        "• SenseVoice / Paraformer / Whisper / OCR 模型：约 1–5 GB\n"
        "• 临时媒体缓存：默认最多 2 GB，任务完成后自动清理\n"
        "• 数据库和日志：通常较小\n\n"
        "建议选择至少有 15 GB 可用空间的磁盘。"
    )
    info_box = tk.Text(frame, height=9, wrap="word", bg="#F4F7FB", relief="flat", padx=14, pady=12)
    info_box.insert("1.0", info)
    info_box.configure(state="disabled")
    info_box.pack(fill="x", pady=(0, 18))

    def add_path_row(label: str, variable: tk.StringVar, chooser_title: str) -> None:
        ttk.Label(frame, text=label, font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w")
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=(5, 14))
        ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True)

        def browse() -> None:
            initial = Path(variable.get() or default_data)
            value = filedialog.askdirectory(
                title=chooser_title,
                initialdir=str(initial if initial.exists() else initial.parent),
                mustexist=False,
                parent=root,
            )
            if value:
                variable.set(value)

        ttk.Button(row, text="浏览…", command=browse).pack(side="left", padx=(8, 0))

    add_path_row("运行数据与大文件目录", data_var, "选择 CareerAgent 数据目录")
    add_path_row("文字结果导出目录", export_var, "选择 Word/TXT 导出目录")

    space_label = ttk.Label(frame, text="")
    space_label.pack(anchor="w", pady=(0, 12))

    def refresh_space(*_args: object) -> None:
        try:
            path = Path(data_var.get()).expanduser()
            free = free_space_bytes(path)
            space_label.configure(text=f"目标磁盘可用空间：{format_bytes(free)}")
        except Exception:
            space_label.configure(text="无法读取目标磁盘空间")

    data_var.trace_add("write", refresh_space)
    refresh_space()

    buttons = ttk.Frame(frame)
    buttons.pack(side="bottom", fill="x", pady=(18, 0))

    def confirm() -> None:
        data = Path(data_var.get().strip()).expanduser()
        export = Path(export_var.get().strip()).expanduser()
        if not str(data) or not str(export):
            messagebox.showerror("路径无效", "两个目录都必须填写。", parent=root)
            return
        ok, message = validate_writable_directory(data)
        if not ok:
            messagebox.showerror("数据目录不可用", message, parent=root)
            return
        ok, message = validate_writable_directory(export)
        if not ok:
            messagebox.showerror("导出目录不可用", message, parent=root)
            return
        free = free_space_bytes(data)
        if free and free < 10 * 1024**3:
            proceed = messagebox.askyesno(
                "可用空间较少",
                f"目标磁盘只剩 {format_bytes(free)}，可能不足以安装 CUDA 运行环境和多个模型。仍然继续吗？",
                parent=root,
            )
            if not proceed:
                return
        result["data"] = data.resolve()
        result["export"] = export.resolve()
        root.destroy()

    def cancel() -> None:
        if messagebox.askyesno(
            "取消设置",
            "取消后本次不会安装大文件，也不会启动 CareerAgent。确定取消吗？",
            parent=root,
        ):
            root.destroy()

    ttk.Button(buttons, text="取消", command=cancel).pack(side="right")
    ttk.Button(buttons, text="确认并继续安装", command=confirm).pack(side="right", padx=(0, 10))
    root.protocol("WM_DELETE_WINDOW", cancel)
    root.mainloop()
    if "data" not in result:
        return None
    return result["data"], result["export"]


def ensure_location_configuration(project_root: Path, *, interactive: bool = True) -> LocationConfig:
    explicit_home = explicit_value(project_root, ("CAREER_AGENT_HOME", "CAREERAGENT_HOME"))
    explicit_export = explicit_value(
        project_root,
        ("CAREER_AGENT_EXPORT_DIR", "CAREERAGENT_EXPORT_DIR", "TRANSCRIPTION_EXPORT_DIR"),
    )
    if explicit_home:
        app_home = Path(explicit_home).expanduser().resolve()
        export_dir = Path(explicit_export).expanduser().resolve() if explicit_export else app_home / "exports"
        return save_location_config(
            app_home,
            export_dir,
            configured_by="environment",
            accepted=True,
        )

    saved = read_location_config()
    if saved:
        saved.app_home_path.mkdir(parents=True, exist_ok=True)
        saved.export_dir_path.mkdir(parents=True, exist_ok=True)
        return saved

    default_data = default_app_home(project_root)
    default_export = default_export_dir(project_root, default_data)
    noninteractive = os.environ.get("CAREERAGENT_NONINTERACTIVE", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    if interactive and not noninteractive and os.name == "nt":
        selected = _setup_dialog(default_data, default_export)
        if selected is None:
            raise KeyboardInterrupt("Storage setup cancelled")
        data, export = selected
    else:
        data, export = default_data, default_export
    return save_location_config(data, export, configured_by="setup_wizard", accepted=True)


def update_export_directory(project_root: Path, export_dir: Path) -> LocationConfig:
    current = resolve_locations(project_root)
    return save_location_config(
        current.app_home_path,
        export_dir,
        configured_by="settings_ui",
        accepted=current.large_download_notice_accepted,
    )


def update_app_home_for_next_start(
    project_root: Path,
    app_home: Path,
    *,
    export_dir: Path | None = None,
) -> LocationConfig:
    current = resolve_locations(project_root)
    target_export = export_dir or (
        app_home / "exports"
        if current.export_dir_path == current.app_home_path / "exports"
        else current.export_dir_path
    )
    return save_location_config(
        app_home,
        target_export,
        configured_by="settings_ui",
        accepted=True,
    )
