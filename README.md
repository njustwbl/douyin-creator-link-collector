# CareerAgent

> 面向 AI 学习内容的采集、文本化、质量评估与安全纠错工作台。

CareerAgent 从真实的短视频学习流程出发，将抖音创作者公开作品采集、视频 ASR、图文 OCR、长文章正文提取、文本质量评估和可追踪纠错串成一条本地工作流，为后续知识卡、RAG 和学习 Agent 提供干净的数据入口。

当前公开版本：**v0.9.0**  
当前里程碑：**已完成“内容采集 → 转文字 → 基础清洗与简单纠错”闭环。**

## 项目解决的问题

短视频转写文本不能直接进入知识库：它通常包含断句混乱、重复口头语、ASR 控制标签、专业术语误识别，以及数字和技术标识被错误修改的风险。CareerAgent 保留原始文本，并通过分层处理和安全校验生成可审核版本，而不是直接覆盖原文。

## 已实现功能

### 1. 抖音公开内容采集

- 单博主前 N 条作品采集；
- 多博主按完整自然日增量采集；
- 视频、普通图文和长文章分别识别；
- API-first + 浏览器兜底；
- 作者、作品、采集批次和错误日志结构化入库；
- 幂等去重及新增/更新/未变化识别。

### 2. 多类型内容转文字

```text
视频   → 下载媒体 → FFmpeg 提取音频 → SenseVoice / Paraformer / Whisper
图文   → 下载图片 → RapidOCR → 按图片顺序合并
文章   → 结构化接口 / 页面 JSON / 隐藏浏览器 → 提取正文
```

支持单条和批量后台任务、失败项单独重试、历史结果查询，以及 TXT / Word 导出。

### 3. 文本质量评估

- 自动质量评分和风险分层；
- 重复片段、异常字符、超长无标点句和术语风险检测；
- 可选第二 ASR 模型交叉复核；
- 支持人工标准稿与 CER 计算；
- 质量结果长期保存，可用于构建评测集。

### 4. 简单清洗与纠错（当前里程碑）

| 模式 | 当前状态 | 作用 |
|---|---|---|
| 基础清洗 | 稳定 | 清理标签、异常空格、重复行、标点和段落结构 |
| 术语纠错 | 稳定 | 使用内置 AI 术语词典和自定义词表修正 Agent、RAG、Token 等误识别 |
| 本地轻量纠错 | 实验性 | 按需加载本地 1.5B 模型，处理局部错字和轻微语病 |
| API 可读化整理 | 可选增强 | 调用用户配置的 OpenAI 兼容模型重建可阅读文本 |

文本版本独立保存：

```text
raw 原始稿
→ normalized 清洗稿
→ corrected 纠错稿
→ final 人工确认稿
```

自动修改会检查数字、日期、比例、URL、版本号、英文缩写、文本长度和修改比例；存在风险时标记为 `review_required`，不会冒充人工确认稿。

## 系统架构

```text
Web UI
  ↓
FastAPI Router
  ↓
Service / Repository
  ├── Collection Provider
  │     ├── Fast API Provider
  │     └── Browser Fallback
  ├── Transcription Pipeline
  │     ├── ASR Engines
  │     ├── OCR
  │     └── Article Extractor
  ├── Quality Gate
  └── Text Refinement
        ├── Rule Normalizer
        ├── Terminology Dictionary
        ├── Local Correction Model
        └── OpenAI-compatible API
  ↓
SQLite + Local Filesystem
```

详细设计见 [ARCHITECTURE.md](ARCHITECTURE.md) 和 [TEXT_REFINEMENT.md](TEXT_REFINEMENT.md)。

## 技术栈

- **Backend**：FastAPI、Pydantic、SQLAlchemy Async、SQLite
- **Collection**：HTTPX、Playwright
- **ASR**：FunASR / SenseVoice、Paraformer、faster-whisper
- **OCR**：RapidOCR、ONNX Runtime
- **Text refinement**：规则清洗、领域术语词典、Transformers、OpenAI-compatible API
- **Engineering**：后台批任务、Trace ID、结构化日志、错误码、诊断包、缓存清理

## 快速开始（Windows）

### 运行环境

- Windows 10/11；
- Python 3.11 或 3.12；
- 首次安装和模型下载需要网络；
- NVIDIA GPU 可选，没有 GPU 时自动回退 CPU。

### 启动

1. 下载或克隆项目；
2. 双击 `CareerAgent_Start.bat`；
3. 首次运行按向导选择数据目录；
4. 浏览器自动打开 `http://127.0.0.1:8000`；
5. 首次采集前在页面完成抖音登录。

基础 Web 后端依赖会自动安装；第一次使用 ASR/OCR 时才安装对应的大体积依赖和模型，不会把模型权重提交到仓库。

## 开发运行

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload
```

需要本地 ASR/OCR 时：

```bash
pip install -r requirements-asr.txt
```

运行轻量单元测试（不下载 ASR/OCR 模型）：

```bash
pytest -q tests/test_url_parser.py tests/test_normalizer.py tests/test_fast_api_provider.py tests/test_refinement.py
```

## 数据与隐私

以下内容只保存在用户本机，不应上传 GitHub：

- `.env`；
- 抖音 Cookie 和浏览器登录目录；
- API Key；
- SQLite 数据库；
- 日志、诊断包、媒体缓存和模型权重。

`.gitignore` 已排除这些目录。Windows 下选择“记住 API Key”时使用当前用户范围 DPAPI 加密；项目日志和诊断包会对敏感参数脱敏。

## 当前边界

- 这是学习与工程实践项目，不保证第三方平台接口长期稳定；
- 不实现验证码绕过；遇到验证时需要用户人工完成；
- 自动纠错不能替代人工核对，尤其是数字、版本号、专名和技术结论；
- 仅处理用户有权访问的公开内容，并应遵守目标平台条款及适用法律；
- 模型和第三方库按各自许可证使用，详见源文件归属说明。

## Roadmap

- [x] 单博主和多博主内容采集
- [x] 视频 / 图文 / 文章统一文本化
- [x] ASR 质量评估和 CER
- [x] 基础清洗与术语纠错
- [x] 本地和 API 可选纠错
- [ ] 知识卡结构化抽取
- [ ] Chunk、Embedding、Hybrid Search 和引用式 RAG
- [ ] 学习掌握度、错题与间隔复习
- [ ] 项目 Backlog 和面试陪练 Agent

## 作品集表达

> 基于 FastAPI、Playwright、FunASR、faster-whisper 和 SQLAlchemy Async，设计并实现多源 AI 学习内容处理平台。系统支持抖音创作者公开作品的增量采集，视频 ASR、图文 OCR、长文章抽取，以及带质量门禁和版本追踪的文本纠错；通过任务状态、Trace ID、结构化错误码与诊断日志实现可观测的后台处理链路，为后续 RAG 和学习 Agent 提供标准化数据入口。

## License

项目主体代码使用 [Apache License 2.0](LICENSE)。部分签名辅助实现及模型、第三方依赖遵循各自上游许可证和归属声明。
