# CareerAgent Collector v1.7.0

CareerAgent 的内容入口。目前包括：

1. 单博主前 N 条作品采集；
2. 多博主按完整自然日采集，支持视频、图文、文章；
3. 单个或批量抖音作品自动分类并转成文字。


## v1.7.0：本地 Qwen 模型可选运行

- 文本清洗与纠错移除旧的本地 1.5B 纠错模型，“本地”模式改为通过 Ollama 调用 `qwen3.5:4b`；
- 新增统一的 Ollama 本地模型设置，可配置地址、对话模型、Embedding 模型、上下文、超时、保活时间和向量批量大小；
- RAG 知识入库准备可由用户手动选择 API 大模型或本地 `qwen3.5:4b`，不会自动串联或自动切换；
- 知识库检索新增 Ollama 本地 Embedding 提供商，默认候选为 `qwen3-embedding:4b`；
- 知识库问答可手动选择 API 大模型或本地 `qwen3.5:4b`，本地模式采用较小来源数、上下文和输出预算；
- 本地对话统一关闭思考输出、使用非流式结构化响应、串行执行，并保留现有数字、URL、版本号和引用安全校验；
- API 模式继续保留，现阶段各步骤相互独立，便于使用同一批数据分别测试本地模型与 API 模型。

首次使用本地模型：

```powershell
ollama pull qwen3.5:4b
ollama pull qwen3-embedding:4b
```

启动 Ollama 后，可在“文本清洗与纠错 → Ollama 本地模型设置”中分别测试对话模型和 Embedding 模型。


## v1.6.0：RAG 评测与优化闭环

- 新增独立的“评测与优化”页面，覆盖端到端问答评测、失败诊断、参数实验和默认配置发布；
- 可将已有检索评测题一键导入为 RAG 问答评测题，并补充参考答案、关键要点、拒答标注及调参集/测试集划分；
- 每道题保存完整链路：检索排名、发送给回答模型的资料、最终答案、引用来源、耗时、HTTP 请求和 Token；
- 自动区分召回失败、排序失败、上下文选择失败、多来源不完整、答案生成失败、引用错位、幻觉风险、拒答错误和速度成本问题；
- 端到端评测默认使用规则代理指标，不额外调用“裁判大模型”，避免评测成本翻倍；
- 新增检索参数实验：加权混合、RRF、低置信度精排等方案使用同一套评测题自动对比；
- 自动给出质量最高、成本最低和综合最优方案，并可一键设为正式知识库问答默认配置；
- 正式知识库问答页面会读取保存后的默认索引、检索方式、Reranker、来源数量、上下文和回答 Token 配置。

推荐流程：先将现有 52 道检索题导入，补充关键要点；在“调参集”上比较配置，确认后只在“测试集”上做一次最终验证。


## v1.5.0：带引用的知识库问答闭环

- 新增独立的“知识库问答”页面：输入问题后自动完成检索、可选精排和大模型回答；
- 默认使用 RRF 混合检索，多来源问题自动扩大召回并启用 MMR；
- 仅对低置信度单文档问题调用 Reranker，控制等待时间和 API 成本；
- 回答模型复用“文本清洗与纠错”页面配置的 OpenAI 兼容 API，默认关闭思考模式；
- 每个事实结论要求使用 `[1]`、`[2]` 等编号引用，引用卡片由程序绑定真实标题、作者、原文片段和视频链接；
- 长文命中时可在字符预算内补充相邻片段，降低切分导致的上下文缺失；
- 模型未给出有效引用时，系统会把回答标记为证据不足，避免脱离知识库自由发挥；
- 高级设置支持来源数量、上下文上限、回答 Token 上限和相邻片段开关。

推荐流程：先在“知识库检索”建立索引，再到“知识库问答”选择索引并提问。


## v1.4.5：知识库界面重排与旧进程识别

- “单题检索”和“批量评测”都按 **基础检索 / 多来源召回 / 精排策略** 分为独立卡片；
- 加权混合只显示 Dense 权重，RRF 混合只显示 RRF 常数，关闭 Reranker 后隐藏无效字段；
- 静态资源统一 `no-store`，首页按当前 `APP_VERSION` 动态注入 CSS/JS 版本；
- 启动器会识别 8000 端口上的旧 CareerAgent 实例。旧版本仍占用端口时，新代码自动使用 8001～8020 的可用端口；
- 页面右上角同时显示前端版本、后端版本和进程 PID。版本不一致时会直接提示当前响应服务的项目路径；
- `/health` 增加项目根目录、前端资源目录和资源签名，便于定位“覆盖了 A 文件夹、实际却启动 B 文件夹”的问题。

推荐始终从当前代码目录中的 `CareerAgent_Start.bat` 启动，不要复用旧终端窗口或其他副本的快捷方式。


## v0.9.0：统一 ASR 后处理与可选大模型 API

本版不再针对每一种新文本不断追加零散字符规则，而是把三种 ASR 输出统一转换为
“带时间边界的语音片段”，再使用同一套段落重建器处理：

- SenseVoice：原始控制标签和声音事件保留在 raw_text；阅读稿自动移除音乐、掌声、情绪 emoji 等元数据符号；
- Paraformer：优先使用 sentence_info、VAD 时间和 CT-Punc 标点结果，并支持统一领域热词；
- Whisper：使用时间停顿、标点和目标句长重建句子，避免每片一行或整篇一个超长段落；
- 三种模型共用同一套中英混排、句子和段落格式化逻辑，减少按模型堆叠特例。

文本纠错模式改为显式四选一，移除“智能推荐”：

| 模式 | 说明 |
|---|---|
| 基础清洗 | 统一格式、控制标签、声音事件和段落结构 |
| 术语纠错 | 基础清洗 + 本地领域词典 |
| 本地 Qwen3.5-4B | 基础清洗 + 术语纠错 + Ollama 本地模型，面向 ASR/OCR 的保守纠错与可读化 |
| API 可读化整理 | 使用用户配置的 OpenAI 兼容模型，将碎片化 ASR/OCR 整理成可连续阅读文本 |

API 设置支持 OpenAI、DeepSeek、SiliconFlow、Ollama 和自定义兼容接口。可填写
Base URL、模型 ID、API Key、Temperature、最大输出 Token 和超时。Windows 下选择
“记住 Key”时使用当前用户 DPAPI 加密，Key 不会回传页面、写入日志或诊断包。




## v0.8.2：文本化历史管理与缓存语义修正

- “清理媒体文件”只删除 MP4、WAV 和 OCR 图片，不再让用户误以为会删除历史文字；
- 文本化任务、识别文本、质量评估、CER、纠错稿和最终稿都长期保存在 SQLite，所以程序重启后仍会显示；
- 质量评估下拉框默认只显示“同一作品 + 同一模型”的最新一次，减少重复记录；
- 可切换“显示同作品全部历史”，用于对比不同运行结果；
- 支持删除当前文本化记录；
- 支持安全清理重复记录，含人工最终稿或人工标准稿的旧记录会受保护；
- 存储页面新增“清空文本化历史”，需要二次确认，且不会删除采集结果、模型或登录状态。

## v0.8.1：质量评估历史任务入口修复

- “文本质量评估”板块始终可以从顶部导航进入；
- 页面刷新或程序重启后，仍可选择以前完成的文本化任务；
- 历史任务没有质量结果时，会自动补做规则评估；
- 质量评估不再依赖“刚刚完成的那一次任务”。

## v0.8.0：文本清洗、术语纠错与保守通顺

本版开始真正修改识别文本，但仍然坚持“原文永不覆盖、每次修改可追踪、风险修改必须人工确认”。新增顶部板块：

```text
文本清洗与纠错
```

支持三个处理等级：

| 模式 | 是否下载大模型 | 处理范围 |
|---|---:|---|
| 基础清洗 | 否 | 空格、标点、异常换行、重复行、SenseVoice 标签等确定性问题 |
| 术语纠错 | 否 | 基础清洗 + Agent、RAG、Token、Prompt、LangGraph 等领域术语；支持自定义词表 |
| 本地 Qwen3.5-4B | 首次需要 | 基础清洗 + 术语纠错 + Ollama `qwen3.5:4b`，修复明显错字、断句和病句并改善可读性 |

完整流程：

```text
原始识别文本
→ 确定性规则清洗
→ 领域术语规范化
→ 可选 Ollama 本地 Qwen3.5-4B 保守纠错与可读化
→ 数字 / URL / 版本号 / 长度 / 修改比例安全检查
→ 人工编辑并标记最终稿
```

主要能力：

- 原始文本、清洗稿、纠错稿和最终稿分别保存，不会覆盖 ASR/OCR 原文；
- 页面左右对照显示来源文本与处理后文本；
- 展示修改项、风险项、修改比例和安全校验结果；
- 数字、百分比、版本号、URL 或技术标识发生变化时自动标记“需要人工确认”；
- 自定义词表格式为 `规范词=别名1|别名2`；
- Qwen 模型由 Ollama 单独下载和管理，不随代码包发布；
- 用户可以手动编辑并保存最终稿，也可以恢复自动稿；
- TXT 与批量合并 Word 优先导出最终稿，其次纠错稿、清洗稿，最后才是原始识别文本；
- 纠错任务、模型、设备、耗时、错误和 Trace ID 均写入诊断日志。

详细设计见 [TEXT_REFINEMENT.md](TEXT_REFINEMENT.md)。

## v0.7.0：文本质量门禁与可量化评测

本版在“识别完成”和“进入纠错/知识库”之间增加质量门禁。它不声称在没有标准稿时能够证明文本完全正确，而是把识别风险显式化：

- 自动质量评分（0～100）与高可信 / 需关注 / 建议人工复核三级分层；
- 视频按音频时长检查字数密度，图文按图片数量检查 OCR 完整性，文章检查是否只提取标题或混入页面噪声；
- 检测重复片段、异常字符、超长无标点句、疑似 AI 专业术语误识别、数字和版本号风险；
- 可选第二 ASR 模型交叉复核，展示主模型与复核模型的字符相似度和两份文本；
- 支持粘贴人工标准稿，计算中文 CER、替换/插入/删除错误；
- 质量结果、复核文本和 CER 长期写入 SQLite，可在诊断日志和批量任务中查看；
- 合并 Word 会带上质量评分、是否需复核、双模型一致性和人工 CER；
- 可导出单条质量报告 JSON，便于形成测试集和面试演示材料。

推荐先选 20～50 条有代表性的短视频人工制作标准稿，再比较 SenseVoice、Paraformer 和 Whisper 的 CER。详细说明见 [QUALITY_EVALUATION.md](QUALITY_EVALUATION.md)。

## v0.6.3：板块导航与统一诊断中心

页面顶部新增粘性板块导航，工作台、采集结果、多博主结果、单条文本化、批量文本化、历史管理、诊断日志和存储设置不再纵向堆在一页。点击对应按钮即可切换，结果生成后相关按钮会自动启用。

诊断中心现在同时查看：

- 单博主采集阶段事件与错误码；
- 文本化任务的模型、设备、阶段、Trace ID、耗时和技术异常；
- 程序运行日志 `career_agent.jsonl`；
- 启动与安装日志 `bootstrap.log`；
- 一键打开日志目录或导出包含近期采集、批量采集、文本化任务和程序日志的诊断包。

日志会自动脱敏 Cookie、Token、`a_bogus`、`X-Bogus` 等敏感字段，并按大小轮转。

## v0.6.2：首次路径向导、大文件下载提示与指定目录导出

本版在下载任何数 GB 依赖之前先弹出本地设置窗口：

- 选择 Python/CUDA 运行环境、模型、数据库、登录状态和缓存的总目录；
- 选择 Word/TXT 的默认导出目录；
- 显示大致空间需求和目标磁盘剩余空间；
- 第一次使用 SenseVoice、Paraformer 或 Whisper 时，页面再次显示模型预计大小与保存位置；
- 单条 TXT 和批量 Word 只有点击导出时才生成，并直接保存到设置目录；
- 页面底部可以修改目录、打开目录和查看各部分占用；
- 运行数据目录修改后下次启动生效，导出目录修改后立即生效。

默认媒体仍为临时缓存，任务完成后自动删除。详细说明见 [STORAGE_OPTIMIZATION.md](STORAGE_OPTIMIZATION.md)。

## v0.6.0：后台批量文本化与流水线加速

“作品转文字”页面支持一次输入多个视频、图文和文章链接。提交后立即创建后台任务，页面每秒刷新进度。

```text
多个作品链接
→ 受控并发解析作品与下载媒体
→ 视频并发提取音频
→ 同一 ASR 模型只加载一次并常驻内存/显存
→ 视频按模型队列推理，图文 OCR 与文章提取可并行
→ 失败项单独记录并可一键重试
```

除了 CUDA，本版还通过以下方式提速：

- HTTP 下载连接复用，减少重复 TLS 建连；
- 同一批任务内复用临时视频、音频和图片；任务完成后按轻量策略自动清理；
- SenseVoice、Paraformer、Whisper 模型对象进程内复用；
- “快速模式”将 Whisper beam 调为 1，并关闭前文条件，同时增大 FunASR 批处理窗口；
- 解析、下载、FFmpeg 与模型推理组成流水线，而不是一条处理完再开始下一条；
- GPU 推理仍受引擎锁保护，避免同一显卡同时加载多份模型造成显存不足。

批量 API：

```http
POST /api/v1/transcriptions/douyin/batch
GET  /api/v1/transcriptions/batches/{batch_id}
POST /api/v1/transcriptions/batches/{batch_id}/retry-failed
```

请求示例：

```json
{
  "input_text": "https://www.douyin.com/video/1\nhttps://www.douyin.com/article/2",
  "asr_model": "sensevoice",
  "speed_mode": "fast",
  "concurrency": 3
}
```

批量任务和子任务都写入 SQLite。程序意外退出后，再次启动会恢复未完成的排队任务。


## v0.5.4：CPU / NVIDIA GPU 自动安装与检测

启动器现在会自动检测 NVIDIA 显卡和驱动，并单独管理 PyTorch：

```text
检测到 NVIDIA GPU
→ 从 PyTorch 官方 cu128 源安装 torch + torchaudio
→ SenseVoiceSmall / Paraformer 自动使用 cuda:0
→ 将 torch/lib 中的 CUDA 12、cuDNN DLL 注册给 CTranslate2
→ Whisper 优先使用 cuda/float16

没有 NVIDIA GPU或 GPU 自检失败
→ 安装 CPU 版 PyTorch
→ Whisper 使用 cpu/int8
```

普通用户不需要再手动卸载 CPU 版 PyTorch、复制 DLL 或配置 PATH。首次启动仍需可用网络，使用 GPU 时需要正常的 NVIDIA 驱动。完整说明见 [COMPUTE_ENVIRONMENT.md](COMPUTE_ENVIRONMENT.md)。

进入“作品转文字”后，页面会显示四张计算设备卡片：NVIDIA GPU、SenseVoiceSmall、Paraformer 和 Whisper，并列出缺失运行库或自动回退原因。

为避免 CUDA 版 PyTorch再次被覆盖，`requirements-asr.txt` 不再声明 `torch` 和 `torchaudio`；它们只由 `bootstrap.py` 根据硬件安装。



## v0.5.3 文章只提取标题修复

部分抖音文章网络响应只包含标题。旧版会把带中文和标点的标题误判为正文，导致隐藏浏览器尚未读取完整页面正文就提前返回。现在会：

1. 单独比较标题和正文，标题或近似标题不能作为正文；
2. 不再使用第一个网络候选立即返回；
3. 同时收集网络结构化正文和浏览器 DOM 正文；
4. 根据正文长度、段落数、标点和来源可靠性选择最佳候选；
5. 等待页面可见文本明显长于标题后再执行 DOM 提取。

正常结果中的正文字数应为完整文章长度，处理方式通常显示 `rendered_page_dom` 或 `rendered_page_network`。


## v0.5.2 文章正文提取修复

抖音长文章正文可能由前端脚本动态加载，普通 HTTP 请求有时只能取得页面外壳。现在文章处理采用四级降级：

1. 已登录作品详情接口；
2. iesdouyin 作品信息接口；
3. 页面内嵌 JSON；
4. 隐藏 Chromium 渲染页面，并从网络响应与正文 DOM 中提取。

浏览器兜底为无界面模式，不会弹出文章窗口；会清除导航、推荐视频、评论区等页面噪声。

## v0.5.2：Whisper CUDA 自动回退修复

Windows 上即使能够检测到 NVIDIA 显卡，也可能缺少 CTranslate2 所需的 CUDA 12 动态库，例如 `libcublas64_12.dll`。现在 `WHISPER_DEVICE=auto` 时，若 CUDA 模型在加载或首次推理阶段失败，程序会自动切换到 `CPU + int8` 并重试，不需要手动安装 CUDA Toolkit。转写结果的设备字段会显示 `CPU/int8（CUDA 自动回退）`。

需要强制使用 CPU 时，可在 `.env` 中设置：

```env
WHISPER_DEVICE=cpu
```

## v0.5.0：作品自动文本化

网页顶部进入：

```text
作品转文字
```

可以粘贴：

```text
https://www.douyin.com/video/{id}
https://www.douyin.com/note/{id}
https://www.douyin.com/article/{id}
https://v.douyin.com/分享短链/
包含抖音作品链接的整段分享文案
```

程序先解析短链和作品详情，再按作品类型自动分流：

```text
视频
→ 解析媒体地址
→ 流式下载 MP4
→ FFmpeg 提取 16kHz 单声道 WAV
→ 使用用户选择的 ASR 模型

图文
→ 获取全部图片地址
→ 逐张流式下载
→ RapidOCR 本地识别
→ 按图片顺序合并文字

文章
→ 从作品详情或页面内嵌数据提取正文
→ 清理 HTML 并保留段落
→ 不调用语音模型或 OCR
```

目前不进行术语纠错、同音词改写或 LLM 润色。系统保留：

```text
raw_text   模型原始分段、OCR 置信度输出或原始文章正文
text       便于阅读和导出的正文
```

## 视频可选模型

页面可以选择：

| 页面选项 | 运行方式 | 默认具体模型 | 适用方向 |
|---|---|---|---|
| SenseVoiceSmall | FunASR | `iic/SenseVoiceSmall` | 中文口播、速度优先 |
| Paraformer | FunASR | `paraformer-zh` + `fsmn-vad` + `ct-punc` | 普通话、标点恢复 |
| Whisper | faster-whisper | `small` | 中英混合、复杂音频 |

选择只对视频生效；图文固定使用 RapidOCR，文章直接提取正文。

第一次使用某个模型时会按需下载到 CareerAgent 本地数据目录中的 `models`。
新安装的默认位置是：

```text
%LOCALAPPDATA%\CareerAgent\models
```

覆盖旧版本时，如果检测到项目内旧 `data/models`，会继续复用，避免重新下载。

以后重复使用会复用缓存。Whisper 默认使用 `small`，避免普通电脑首次体验时下载和推理过重；有合适的 NVIDIA GPU 后，可以在 `.env` 改成：

```env
WHISPER_MODEL_NAME=large-v3-turbo
```

## 安装与启动

### 覆盖升级

1. 关闭 CareerAgent 黑色运行窗口；
2. 解压更新包；
3. 将更新包内文件复制到原项目目录并覆盖；
4. 保留原来的 `data`、`.venv`、`.env`；
5. 双击 `CareerAgent_Start.bat`。

依赖文件发生变化后，启动脚本会自动补装 faster-whisper、RapidOCR 和文章解析依赖。第一次更新可能等待较久。

### 完整安装

完整解压项目后直接双击：

```text
CareerAgent_Start.bat
```

脚本会自动：

```text
首次运行先选择大文件目录和导出目录
→ 创建或复用所选目录中的运行环境
→ 安装基础依赖
→ 检测 NVIDIA GPU 与驱动
→ 自动安装 CUDA 或 CPU 版 PyTorch
→ 安装本地 ASR/OCR 依赖
→ 注册 CTranslate2 所需 CUDA/cuDNN DLL 目录
→ 安装 Playwright Chromium
→ 生成计算环境报告
→ 启动 FastAPI 并打开本地页面
```

## 数据保存位置与空间占用

全新安装会先让用户选择目录，例如：

```text
D:\CareerAgentData\
├── database\career_agent.db     任务、文字和状态
├── browser\                     抖音登录状态
├── models\                      按需下载的 ASR / OCR 模型
├── cache\media\                临时视频、音频和图片
├── logs\                        轮转日志
└── runtime\venv\               Python、PyTorch、CUDA 运行环境
```

程序源码通常不到 2 MB。实际数 GB 占用主要来自：

- CUDA 版 PyTorch 和 Python 依赖；
- SenseVoice、Paraformer、Whisper 与 OCR 模型；
- 旧版本残留的视频、WAV 和图片缓存。

媒体缓存默认在文本保存后自动删除。模型与运行环境会保留，因为每次删除都会导致下次重新下载。页面中的“本地空间与缓存”可以查看各部分占用并手动清理。

程序关闭时可以双击 `CareerAgent_Storage_Settings.bat` 重新选择运行数据目录和导出目录。页面内修改运行数据目录后需要重启；旧目录不会自动删除。

## API

统一接口：

```http
POST /api/v1/transcriptions/douyin/content
```

请求示例：

```json
{
  "url": "https://www.douyin.com/video/1234567890",
  "asr_model": "paraformer",
  "speed_mode": "balanced"
}
```

`asr_model` 可选：

```text
sensevoice
paraformer
whisper
```

旧接口仍兼容：

```http
POST /api/v1/transcriptions/douyin/video
```

任务查询：

```http
GET /api/v1/transcriptions/jobs
GET /api/v1/transcriptions/jobs/{job_id}
GET /api/v1/system/compute-status
```

Swagger：

```text
http://127.0.0.1:8000/docs
```

## 关键配置

```env
TRANSCRIPTION_MEDIA_DIR=./data/media
ASR_MODEL_CACHE_DIR=./data/models

SENSEVOICE_MODEL_NAME=iic/SenseVoiceSmall
SENSEVOICE_DEVICE=auto

PARAFORMER_MODEL_NAME=paraformer-zh
PARAFORMER_DEVICE=auto
PARAFORMER_PUNC_MODEL=ct-punc

WHISPER_MODEL_NAME=small
WHISPER_DEVICE=auto
WHISPER_COMPUTE_TYPE_CPU=int8
WHISPER_COMPUTE_TYPE_CUDA=float16
WHISPER_LANGUAGE=auto

OCR_MAX_IMAGE_BYTES=52428800
ARTICLE_MAX_CHARS=500000
```

`SENSEVOICE_MODEL_CACHE_DIR` 旧配置仍然兼容，会映射到新的 `ASR_MODEL_CACHE_DIR`。

## 媒体与内容解析策略

作品详情按以下顺序降级：

```text
1. 复用当前抖音登录 Cookie 和签名能力请求作品详情
2. 尝试 iesdouyin iteminfo 接口
3. 尝试页面中的 _ROUTER_DATA / RENDER_DATA
4. 视频提取 play_addr、bit_rate、download_addr
5. 图文提取 image_post_info、images、image_list
6. 文章提取 article_info、article_detail、text_mode_info 等明确正文结构
7. 文章结构化字段为空时，再从可见 article/main 页面节点兜底
```

下载采用 `.part` 临时文件和流式写入，不会把整个视频或图片一次性读入内存。

## 当前边界

当前版本仍是同步最小闭环：

- 一次处理一个作品链接；
- 页面需要等待任务完成；
- 尚未增加批量转写队列；
- 尚未增加实时百分比、暂停和取消；
- 尚未增加视频字幕 SRT；
- 尚未进行术语纠错；
- 图文只做 OCR，不做图片场景理解；
- 文章正文提取依赖抖音公开页面结构，平台变化后可能需要更新字段适配。

## 开发检查

```bash
pytest -q
ruff check app tests
node --check app/web/static/app.js
python -m compileall -q app tests bootstrap.py
```

## v0.8.4 纠错板块导航修复

“文本清洗与纠错”现在始终可以进入。当前软件会话尚未产生文本化任务时，页面显示空状态和操作提示；完成单条或批量文本化后，候选任务会自动刷新。历史任务仍只在诊断与历史区域中保留。

## v0.8.5 Whisper 分段与保守纠错修复

- faster-whisper 的 segment 仅作为时间片保存，不再逐片换行展示；可阅读文本自动合并为句子和段落。
- 旧任务可通过“基础清洗”重新整理短行格式。
- 三种纠错模式是强度档位，不需要顺序执行；“保守通顺”内部已包含基础清洗和术语规范化。
- 本地模型新增严格保守提示词与安全回退。出现数字、缩写、英文事实新增、语义漂移或大幅改写时，模型候选会被拒绝，当前纠错稿自动回退到规则结果。

## v0.8.6：智能推荐与逐段安全纠错

本版重点解决两个真实问题：所有文本都手动选择模式，以及长文本中某一段触发风险后整篇模型结果全部回退。

- 新增“智能推荐”默认模式：文章优先基础清洗，高质量 ASR/OCR 优先术语纠错，低质量文本才调用本地 Qwen 模型；
- 长文本按段落和完整句子切块，并给每块提供只读上文，减少块边界断句和上下文丢失；
- 每个文本块独立进行数字、URL、缩写、长度和语义漂移校验；首次失败会自动使用更严格提示重试；
- 只有仍不安全的单个文本块回退到规则稿，其他安全块继续采用模型结果，不再“一处有问题、整篇不变化”；
- 页面显示总块数、采用块数、安全重试块数和回退块数，回退段落可在安全检查中定位；
- 术语安全校验支持显式允许的别名替换，`RAAG → RAG` 等正常修正不再被错误拦截；
- 修复词表连续替换导致 `shisper → Whisperr` 的问题，并避免把 `AI Agent` 错误缩成 `Agent`；
- 新增 Whisper、SenseVoice、Paraformer、PyTorch、CUDA、cuDNN、CTranslate2 等术语规则；
- 自定义词表自动保存在本机浏览器；
- 新增“批量智能处理本次未完成任务”，按顺序处理当前运行会话中的文本，单条失败不会中断整批。

推荐工作流：

```text
识别完成
→ 质量门禁
→ 智能推荐最低必要纠错强度
→ 逐段安全纠错与局部回退
→ 人工确认最终稿
→ 导出或进入后续知识库
```
