# CareerAgent

> 本地优先的 AI 内容处理、RAG 评测与多层行业情报问答平台：将短视频、图文和长文章转化为可清洗、可检索、可引用、可评测、可追踪的知识资产与行业情报。

**当前版本：v1.23.0**

CareerAgent 面向 AI 学习、求职准备和行业研究场景，覆盖从公开内容采集到多层证据问答的完整数据链路：

```text
内容采集
→ 视频 ASR / 图文 OCR / 长文章正文提取
→ 文本质量门禁与安全纠错
→ 人工最终稿与知识结构化
→ PostgreSQL / pgvector 正式入库
→ Dense / BM25 / Hybrid / RRF / Reranker
→ 带引用 RAG 与回归评测
→ 实体、Claim、观点簇、事件、统计、博主画像和学习资源关系化
→ 多层行业情报问答
→ 趋势、预警、报告、数据质量与性能治理
```

该仓库既是可运行的本地 Web 应用，也是面向 AI 应用开发、RAG 工程、Agent 工程、数据产品与 AI 产品岗位的作品集项目。

## 核心能力

### 1. 多源内容采集

- 单博主前 N 条公开作品采集；
- 多博主按自然日增量采集；
- 区分视频、普通图文和长文章；
- API-first，失败时只打开目标主页做浏览器兜底；
- `platform + aweme_id` 幂等去重；
- 任务、阶段事件、错误码、Trace ID 和诊断包全链路记录。

### 2. 视频、图文与文章文本化

| 内容类型 | 处理链路 |
|---|---|
| 视频 | 媒体解析 → 下载 → FFmpeg 提取音频 → ASR |
| 图文 | 图片下载 → RapidOCR → 文本合并 |
| 长文章 | 结构化字段 → 页面内嵌数据 → DOM 兜底 |

视频 ASR 支持 SenseVoiceSmall、Paraformer 和 faster-whisper，提供 GPU 自动检测、CPU 回退、批量任务、失败重试、模型复用和媒体缓存治理。

### 3. 文本质量门禁与安全纠错

- 原始稿、清洗稿、纠错稿和人工最终稿分层保存；
- 重复片段、异常字符、超长无标点句和术语风险检测；
- 双 ASR 模型交叉复核与人工标准稿 CER 评测；
- Agent、RAG、Token、Prompt、MCP 等领域术语规范化；
- API 模型或 Ollama 本地 Qwen 保守纠错；
- 数字、URL、版本号、缩写、长度和修改比例安全校验。

### 4. 本地优先知识库与带引用 RAG

- 父子分块和长期增量索引同步；
- API Embedding 与 Ollama 本地 Embedding；
- Dense、BM25、加权混合、RRF 和 MMR；
- Qwen3 Reranker 可选精排；
- 查询路由、父块回溯、相邻去重和动态证据压缩；
- 低置信度拒答；
- `[1]`、`[2]` 编号引用绑定真实来源；
- 检索结果、上下文、回答、引用、耗时和 Token 可追踪。

### 5. RAG 评测与优化闭环

- 参考答案、关键要点、拒答预期和调参集/测试集；
- 检索评测与端到端问答评测分离；
- 自动定位召回、排序、上下文、生成、引用和拒答问题；
- 历史运行作为回归基线；
- 通过率、正确性、忠实度、引用、耗时和 Token 对比；
- 统一检索默认配置可发布到正式问答链路。

### 6. 行业情报结构化与分析

人工最终稿可进一步关系化为：

- 实体与实体提及；
- Claim、事实、建议、风险及证据；
- 原始事件、规范事件及证据；
- 学习项、工具和资源；
- 内容主题、作者、发布时间与稳定身份。

在此基础上提供趋势统计、观点聚类、共识/分歧分析、事件归并、关注列表、可解释预警、日报/周报/专题报告、博主画像、观点演变、数据质量和数据库性能诊断。

### 7. 多层行业情报问答（v1.23.0）

知识库问答提供三种模式：

| 模式 | 证据范围 | 适用问题 |
|---|---|---|
| 普通 RAG | 当前索引的原文 Chunk | 查原话、参数、单篇内容 |
| 行业情报分析 | Claim、观点簇、事件、统计、博主画像、学习资源和可选原文 | 趋势、共识、分歧、事件、博主比较 |
| 自动判断 | 先识别意图，再选择证据层 | 混合型自然语言问题 |

系统会记录各层候选、融合分、最终引用、证据层级和耗时。启用证据门控时，没有直接高相关证据就拒绝生成确定性结论，避免把相关背景误写成事实依据。

### 8. 持久化后台任务中心

- 索引同步、正式情报同步、观点聚类、阈值扫描、事件归并、统计刷新、报告生成等长任务统一管理；
- 任务状态、进度、步骤、错误、日志和结果持久化；
- 同一请求幂等复用，共享资源任务排队；
- 支持协作式取消、失败重试和应用重启后的中断恢复；
- GPU、Embedding、聚类和报告资源使用显式锁管理。

### 9. PostgreSQL、pgvector 与可运维性

- Docker Desktop 启动 PostgreSQL 17 + pgvector；
- SQLite 保留为轻量兼容模式；
- Alembic 管理数据库迁移；
- SQLite 到 PostgreSQL 数据迁移、备份和人工确认恢复；
- pgvector 向量存储和 HNSW 索引；
- 结构化日志轮转、敏感字段脱敏和诊断包导出；
- 数据库、模型、缓存、日志和导出目录可独立配置。

## 系统架构

```mermaid
flowchart LR
    A[公开内容源] --> B[Collection]
    B --> C{内容类型}
    C -->|视频| D[ASR]
    C -->|图文| E[OCR]
    C -->|文章| F[Article Extractor]
    D --> G[Quality Gate]
    E --> G
    F --> G
    G --> H[Refinement]
    H --> I[人工最终稿]
    I --> J[Knowledge Preparation]
    J --> K[Parent-Child Chunking]
    K --> L[Embedding / pgvector]
    L --> M[Dense + BM25 + Hybrid + RRF]
    M --> N[Optional Reranker]
    N --> O[Cited RAG]
    O --> P[RAG Evaluation]
    I --> Q[Intelligence Materialization]
    Q --> R[Claim / Cluster / Event / Statistics]
    R --> S[Multi-layer Intelligence Query]
    S --> T[Alerts / Reports / Creator Profiles]
    U[Persistent Job Center] --> J
    U --> R
    U --> T
```

应用采用模块化单体架构：

```text
app/
├── core/               # 配置、路径、日志、存储、密钥和计算环境
├── db/                 # SQLAlchemy Async、SQLite、PostgreSQL、pgvector
├── modules/
│   ├── collection/     # 单博主、多博主、增量采集与诊断
│   ├── transcription/  # 视频 ASR、图文 OCR、文章正文与批量任务
│   ├── refinement/     # 清洗、术语纠错、LLM 整理与知识结构化
│   ├── knowledge_base/ # 分块、索引、检索、问答、评测与优化
│   ├── intelligence/   # 统计、聚类、事件、预警、报告、画像与多层问答
│   ├── jobs/           # 持久化后台任务、资源锁、取消与恢复
│   └── local_models/   # Ollama 部署、模型拉取与健康检查
├── api/                # FastAPI 路由聚合
└── web/                # 原生 HTML / CSS / JavaScript 管理界面
```

详细设计见 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 技术栈

- **Backend:** FastAPI, Pydantic, SQLAlchemy Async, HTTPX
- **Database:** PostgreSQL 17, pgvector, Alembic, SQLite compatibility mode
- **Browser automation:** Playwright
- **ASR:** FunASR, SenseVoiceSmall, Paraformer, faster-whisper
- **OCR:** RapidOCR, ONNX Runtime
- **Local models:** Ollama, Qwen3.5, Qwen3 Embedding, Qwen3 Reranker
- **Retrieval:** Dense, BM25, weighted hybrid, RRF, MMR
- **Export:** python-docx
- **Testing:** pytest, pytest-asyncio, Ruff, GitHub Actions

## 快速开始

### Windows 普通用户

要求：

- Windows 10/11；
- Python 3.11 或 3.12；
- Docker Desktop（默认 PostgreSQL 模式）；
- 可用网络；
- 使用 GPU 时需安装 NVIDIA 驱动。

步骤：

1. 克隆或下载仓库并完整解压；
2. 启动 Docker Desktop；
3. 双击 `CareerAgent_Start.bat`；
4. 首次启动选择运行数据与导出目录；
5. 启动器自动创建虚拟环境、准备数据库、安装依赖并启动服务；
6. 浏览器自动打开本地管理页面；
7. 首次采集前，在页面中完成抖音登录。

> ASR、Embedding、Reranker 和 Ollama 模型权重按需下载，不包含在仓库中。

更详细步骤见 [docs/QUICK_START.md](docs/QUICK_START.md)。

### SQLite 轻量模式

不使用 Docker 时，可复制 `.env.example` 为 `.env`，并设置：

```env
CAREERAGENT_DATABASE_MODE=sqlite
```

### 开发者模式

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium

# SQLite 开发模式
set CAREERAGENT_DATABASE_MODE=sqlite
uvicorn app.main:app --reload
```

默认访问：`http://127.0.0.1:8000`

本地 ASR 依赖体积较大，按需安装：

```bash
pip install -r requirements-asr.txt
```

## 测试

```bash
pip install -r requirements-ci.txt
ruff check app tests bootstrap.py careeragent_location.py configure_storage.py database_bootstrap.py
python -m compileall -q app tests bootstrap.py
node --check app/web/static/app.js
pytest -q --ignore=tests/test_background_jobs.py
pytest -q tests/test_background_jobs.py
```

离线测试不会访问真实抖音账号、远程模型、Docker 数据库或本地 GPU。需要真实登录态、GPU、模型和 Docker 的场景不在 CI 中执行。

## 数据与隐私

以下本地数据不会进入 Git 仓库：

- `.env`、API Key 和本地服务密钥；
- 抖音 Cookie 与浏览器登录目录；
- SQLite / PostgreSQL 数据目录和备份；
- ASR、Embedding、Reranker 与 Ollama 模型；
- 视频、音频、OCR 图片和媒体缓存；
- 日志、诊断包、Word/CSV/JSON 等用户导出文件。

这些路径已由 `.gitignore` 排除。发布前仍建议执行 [发布检查清单](docs/RELEASE_CHECKLIST.md)。

## 文档

- [系统架构](ARCHITECTURE.md)
- [快速启动](docs/QUICK_START.md)
- [开发说明](docs/DEVELOPMENT.md)
- [PostgreSQL 与 pgvector](docs/design/DATABASE_POSTGRESQL.md)
- [计算环境设计](docs/design/COMPUTE_ENVIRONMENT.md)
- [质量评估设计](docs/design/QUALITY_EVALUATION.md)
- [文本清洗与纠错](docs/design/TEXT_REFINEMENT.md)
- [存储设计](docs/design/STORAGE_OPTIMIZATION.md)
- [错误码](docs/design/ERROR_CODES.md)
- [路线图](docs/ROADMAP.md)
- [作品集与面试表达](docs/PORTFOLIO_GUIDE.md)
- [GitHub 上传教程](docs/GITHUB_UPLOAD_GUIDE.md)
- [v1.23.0 发布说明](docs/releases/RELEASE_NOTES_v1.23.0.md)

## 项目边界与合规

- 当前采集适配重点为抖音公开内容，平台接口变化后可能需要更新；
- 登录与验证码必须由用户本人完成，项目不绕过验证；
- 使用者应遵守平台条款、版权、隐私和所在地法律；
- 自动质量指标、聚类、预警、统计和模型生成内容不能替代人工判断；
- 上游模型权重不随仓库发布，使用前需核对各自许可证和服务条款。

## License

本项目采用 [Apache License 2.0](LICENSE)。第三方组件、适配代码和模型仍受各自上游许可证约束，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
