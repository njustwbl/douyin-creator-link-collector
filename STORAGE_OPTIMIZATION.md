# CareerAgent 存储位置与轻量化策略

## 首次运行先选择目录

v0.6.2 在下载任何大文件之前会弹出本地设置窗口，分别选择：

1. **运行数据与大文件目录**：Python/CUDA 运行环境、ASR/OCR 模型、数据库、抖音登录状态和临时媒体；
2. **Word/TXT 导出目录**：只有点击导出时才生成文件，并保存到这里。

预计空间（实际大小随版本变化）：

| 内容 | 常见占用 |
|---|---:|
| Python + CUDA/PyTorch 运行环境 | 4–7 GB |
| SenseVoice、Paraformer、Whisper、OCR 模型 | 1–5 GB，按需下载 |
| 临时视频、WAV、图片 | 默认最多 2 GB，任务完成后自动清理 |
| 数据库、日志、文字结果 | 通常较小 |

建议选择至少有 15 GB 可用空间的磁盘，例如 `D:\CareerAgentData`。

## 模型按需下载

启动程序只安装运行依赖，不会一次下载全部模型。第一次使用某个模型时，页面会显示：

- 模型名称；
- 预计下载大小；
- 实际保存目录；
- 是否继续下载。

模型目录位于：

```text
<运行数据目录>\models
```

## 媒体缓存策略

```text
作品链接
→ 下载临时视频 / 图片
→ 提取 WAV 或 OCR
→ 完成本地识别
→ 文字写入 SQLite
→ 删除临时媒体
→ 用户点击导出后才生成 Word / TXT
```

默认配置：

```env
TRANSCRIPTION_KEEP_MEDIA=false
TRANSCRIPTION_KEEP_FAILED_MEDIA=false
TRANSCRIPTION_CACHE_TTL_HOURS=24
TRANSCRIPTION_CLEANUP_ON_STARTUP=true
TRANSCRIPTION_MEDIA_CACHE_MAX_BYTES=2147483648
```

## 导出结果

单条任务点击“导出 TXT 到设置目录”，批量任务点击“导出合并 Word 到设置目录”。后端从数据库生成文件并保存到所选目录，不再自动下载到浏览器默认下载文件夹。

页面底部可以随时：

- 查看当前大文件目录和导出目录；
- 修改导出目录，立即生效；
- 修改运行数据目录，下次启动生效；
- 打开对应目录；
- 清理媒体缓存或模型缓存。

修改运行数据目录后不会自动删除旧目录。Python 虚拟环境不适合直接搬移，因此新目录会在下次启动时重新创建运行环境；需要保留的数据库、模型或登录数据应手动复制，或者先保留旧目录。

也可以在程序关闭时双击：

```text
CareerAgent_Storage_Settings.bat
```

重新选择两个目录。
