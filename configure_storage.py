"""在 CareerAgent 未运行时修改大文件和导出目录。"""
from __future__ import annotations

import os
from pathlib import Path

from careeragent_location import (
    choose_directory_native,
    resolve_locations,
    save_location_config,
)

ROOT = Path(__file__).resolve().parent


def main() -> int:
    current = resolve_locations(ROOT)
    data = choose_directory_native(current.app_home_path, "选择 CareerAgent 运行数据与大文件目录")
    if data is None:
        print("未修改存储目录。")
        return 0
    default_export = data / "exports"
    export = choose_directory_native(default_export, "选择 CareerAgent Word/TXT 导出目录")
    if export is None:
        export = default_export
    config = save_location_config(data, export, configured_by="standalone_settings", accepted=True)
    print("存储位置已保存：")
    print(f"  运行数据目录：{config.app_home}")
    print(f"  导出目录：{config.export_dir}")
    print("下次启动 CareerAgent 时生效。旧目录不会自动删除。")
    if os.name == "nt":
        input("按回车键关闭窗口……")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
