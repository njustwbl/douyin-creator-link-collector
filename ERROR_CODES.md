# v0.5.1 内容文本化错误码

| 错误码 | 含义 | 常见处理 |
|---|---|---|
| `INVALID_CONTENT_URL` | 不是有效抖音作品链接 | 重新复制视频、图文或文章链接 |
| `PROFILE_URL_NOT_SUPPORTED` | 输入了博主主页 | 打开具体作品再复制 |
| `CONTENT_ID_NOT_FOUND` | 未解析到作品 ID | 使用完整分享链接 |
| `LOGIN_REQUIRED` | 登录状态不可用 | 点击首次登录抖音 |
| `CONTENT_RESOLVE_FAILED` | 作品详情无法解析 | 重新登录或稍后重试 |
| `MEDIA_RESOLVE_FAILED` | 视频媒体地址为空 | 查看技术日志 |
| `IMAGE_RESOLVE_FAILED` | 图文图片地址为空 | 确认作品仍公开 |
| `ARTICLE_TEXT_NOT_FOUND` | 文章正文为空 | 页面结构可能变化 |
| `MEDIA_DOWNLOAD_FAILED` | 视频下载失败 | 网络或临时地址过期 |
| `IMAGE_DOWNLOAD_FAILED` | 图片下载失败 | 网络或临时地址过期 |
| `FFMPEG_FAILED` | 音频提取失败 | 检查视频和依赖 |
| `ASR_ENGINE_INVALID` | 语音模型选项无效 | 选择三个已支持模型之一 |
| `ASR_DEPENDENCY_MISSING` | ASR 依赖缺失 | 重新运行启动脚本 |
| `MODEL_LOAD_FAILED` | 模型加载或下载失败 | 检查网络、磁盘、CUDA |
| `TRANSCRIPTION_FAILED` | ASR 推理失败 | 换模型重试并看日志 |
| `EMPTY_TRANSCRIPT` | 没识别到人声 | 检查音频内容 |
| `OCR_DEPENDENCY_MISSING` | OCR 依赖缺失 | 重新运行启动脚本 |
| `OCR_MODEL_LOAD_FAILED` | OCR 初始化失败 | 检查安装和磁盘 |
| `OCR_FAILED` | 某张图片识别失败 | 查看技术详情 |
| `EMPTY_OCR_TEXT` | 图片中没有文字 | 可能是纯照片或文字太小 |
| `STORAGE_FAILED` | 数据保存失败 | 检查写入权限和磁盘 |
| `INTERNAL_ERROR` | 未分类异常 | 导出日志定位 |


## Whisper CUDA 自动回退

当 `WHISPER_DEVICE=auto` 且检测到 `libcublas64_12.dll`、cuDNN、CUDA 驱动或显存相关错误时，v0.5.1 会自动使用 CPU/int8 重试。只有 CPU 重试仍失败时，任务才会记录为 `TRANSCRIPTION_FAILED`。

## 批量文本化

| 错误码 | 含义 |
|---|---|
| `TRANSCRIPTION_JOB_NOT_FOUND` | 批量队列中的子任务不存在或已被删除 |
| `ASR_ENGINE_INVALID` | 选择了不支持的语音模型 |
| `INVALID_CONTENT_URL` | 输入不是可识别的抖音作品链接 |

批量任务中单条作品失败不会终止其他作品。失败项会保留错误码、阶段和技术详情，并可单独重试。


## v0.8.0 文本清洗与纠错

| 错误码 | 含义 | 常见处理 |
|---|---|---|
| `TRANSCRIPT_NOT_FOUND` | 对应文本化任务或原始文本不存在 | 先完成作品文本化，再进入纠错 |
| `EMPTY_SOURCE_TEXT` | 来源文本为空 | 检查 ASR、OCR 或文章提取结果 |
| `INVALID_REFINEMENT_MODE` | 纠错模式不受支持 | 选择基础清洗、术语纠错、本地轻量纠错或 API 可读化整理 |
| `CORRECTION_DEPENDENCY_MISSING` | 本地纠错模型依赖未安装 | 重新运行启动器安装依赖 |
| `CORRECTION_MODEL_LOAD_FAILED` | 模型下载或加载失败 | 检查网络、模型目录空间和 GPU/CPU 环境 |
| `CORRECTION_FAILED` | 本地模型推理失败 | 查看纠错任务诊断并重试 |
| `REFINEMENT_JOB_NOT_FOUND` | 纠错任务不存在 | 刷新页面或重新创建任务 |
| `REFINEMENT_INTERNAL_ERROR` | 未分类纠错异常 | 导出任务诊断包定位 |

数字、URL、版本号改变或修改比例过大不是运行错误，任务会成功保存，但 `validation_status` 会变为 `review_required`。


## v0.9.0 大模型 API 错误

| 错误码 | 含义 | 处理 |
|---|---|---|
| `LLM_API_NOT_CONFIGURED` | 未配置 Base URL | 在纠错页面展开 API 设置 |
| `LLM_API_MODEL_MISSING` | 未填写模型 ID | 填写提供商要求的完整模型名称 |
| `LLM_API_KEY_MISSING` | 未配置 API Key | 填写 Key；Ollama 本地接口可不填 |
| `LLM_API_TIMEOUT` | 请求超时 | 增加超时、缩短文本或检查网络 |
| `LLM_API_HTTP_ERROR` | API 返回 4xx/5xx | 检查 Key、模型、余额和 Base URL |
| `LLM_API_INVALID_RESPONSE` | 响应不符合 Chat Completions 结构 | 换用兼容接口或检查网关 |
| `LLM_API_REQUEST_FAILED` | 网络或连接失败 | 检查代理、DNS 和接口地址 |
