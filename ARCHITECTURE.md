# v0.5.4 架构说明

```text
Web UI
  ↓ POST /transcriptions/douyin/content
TranscriptionService（实际为单作品文本化编排器）
  ↓
DouyinContentResolver
  ├─ 视频：media_urls
  ├─ 图文：image_url_groups
  └─ 文章：article_text
  ↓
Content Router
  ├─ video   → MediaDownloader → AudioExtractor → ASR Engine Factory
  │                                      ├─ FunASR + SenseVoiceSmall
  │                                      ├─ FunASR + Paraformer
  │                                      └─ faster-whisper + Whisper
  ├─ gallery → MediaDownloader → RapidOCR
  └─ article → Direct Article Extractor
  ↓
TranscriptionRepository
  ├─ transcription_jobs
  └─ transcripts
```

## 设计原则

1. **作品解析与内容处理分离**：抖音字段变化只改 Resolver。
2. **ASR 引擎统一接口**：上层不依赖 FunASR 或 faster-whisper 的具体返回格式。
3. **按内容类型分流**：图文不误走 ASR，文章不误走 OCR。
4. **本地模型懒加载并复用**：第一次加载慢，后续任务复用进程内模型。
5. **资产缓存**：相同作品重复处理时复用已下载视频、音频和图片。
6. **原始结果与可读文本并存**：为后续纠错、评估和知识库追踪保留证据。

## 后续演进

下一步应把同步 HTTP 调用升级为后台任务：

```text
创建任务 → Worker 领取 → 下载/OCR/ASR → 页面轮询进度 → 完成后通知
```

届时可直接复用现有 Resolver、Downloader、Engine Factory 和 Repository。


## 文章正文解析

文章处理不会只依赖静态 HTML。解析顺序为详情 API、旧版信息接口、页面 hydration JSON、隐藏浏览器渲染兜底。浏览器兜底复用登录 Cookie，但使用独立临时上下文，避免锁定本地持久化登录目录。


## 文章正文候选选择

文章解析不会因为网络响应出现标题就立即成功。解析器会并行收集：

- 标准作品数据中的正文；
- 非标准 JSON 正文候选；
- 渲染页面的正文 DOM。

标题、近似标题和极短摘要会被排除，最后按文本长度、段落、标点与来源权重选择最佳正文。


## v0.5.4 运行环境管理层

```text
CareerAgent_Start.bat
  → bootstrap.py
      → NVIDIA 驱动检测
      → PyTorch CPU/CUDA 选择与自检
      → ASR/OCR 依赖安装
      → 计算环境报告
  → app/core/compute.py
      → Windows DLL 搜索路径注册
      → PyTorch/CTranslate2 在线诊断
  → GET /api/v1/system/compute-status
      → 前端计算设备面板
```

PyTorch 不再由通用 requirements 文件管理，避免 GPU wheel 被普通 PyPI CPU wheel 覆盖。Whisper 仍使用 CTranslate2，但在进程启动时优先复用 PyTorch wheel 自带的 CUDA 12 和 cuDNN DLL。

## v0.6.1 批量文本化流水线

```text
transcription_batches
        ↓ 创建多个 queued 子任务
transcription_jobs
        ↓ 后台 BatchManager 调度
受控并发解析 / 下载 / FFmpeg
        ↓
ASR 引擎内部队列（模型常驻，仅加载一次）
OCR 引擎内部队列（模型常驻）
文章正文解析（可并行）
        ↓
transcripts
```

批量并发不是简单地同时运行多份 GPU 模型。网络和预处理阶段并发，ASR 推理通过各引擎的进程级锁串行执行，从而兼顾吞吐量和显存稳定性。

后台任务状态保存在 SQLite。程序重启时会把未完成的 `running` 子任务恢复为 `queued` 并继续执行。

## v0.6.3 位置配置与导出边界

首次启动由标准库脚本 `careeragent_location.py` 在创建虚拟环境之前完成路径选择。小型位置指针保存在系统配置目录，实际大文件可位于任意磁盘。

```text
location.json
├── app_home     运行环境、模型、数据库、登录数据、缓存
└── export_dir   用户主动导出的 Word / TXT
```

应用进程启动后固定使用本次启动解析出的 `app_home`，避免运行中切换数据库路径。导出目录允许在页面中即时修改；运行数据目录的修改仅写入下一次启动配置。


## v0.6.3 界面导航与诊断边界

前端采用单页多板块视图，顶部导航只切换可见板块，不重新加载后端任务。采集、批量采集和文本化结果生成后对应视图才启用。

诊断分为三层：数据库任务状态与阶段事件、JSONL 程序运行日志、启动安装日志。诊断包可汇总最近采集任务、批量任务、文本化任务及轮转日志，但不包含 Cookie、Token 和浏览器登录目录。

## v0.7.0 文本质量门禁

新增：

```text
app/modules/transcription/
├── quality.py           # 无参考质量评分、模型相似度、CER 算法
└── quality_service.py   # 评估持久化、重评估、人工标准稿评测
```

数据表：

```text
transcription_quality_assessments
├── score / level / review_required
├── metrics_json / issues_json
├── verifier_engine / verifier_text / verifier_similarity
└── reference_text / cer / substitutions / insertions / deletions
```

处理链路：

```text
ASR / OCR / 文章正文
→ 自动质量门禁
→ 可选第二 ASR 模型交叉复核
→ 风险分级
→ 人工标准稿 CER
→ 后续纠错与知识库
```

自动质量分只作为风险排序，不应被解释为真实准确率。真实准确率必须由人工标准稿和 CER 评测得到。


## v0.8.0 文本清洗与纠错模块

```text
app/modules/refinement/
├── normalizer.py   # 确定性清洗和领域术语规范化
├── engine.py       # 按需加载本地 1.5B 中文纠错模型
├── validator.py    # 数字、URL、长度、修改比例安全校验
├── models.py       # 当前状态、任务历史和文本版本
├── repository.py
├── service.py
├── schemas.py
└── router.py
```

该模块只读取文本化结果，不修改 `transcripts` 原始记录。所有衍生版本保存在独立表中，导出器按 `final > corrected > normalized > raw` 选择文本。后续知识库模块也应复用这一版本选择策略。

## v0.9.0 ASR 结果规范化与 API 纠错

三种 ASR 引擎不再各自维护展示规则，而是统一输出 `ASRSegment(start, end, text)`：

```text
SenseVoice / Paraformer / Whisper
        ↓
控制标签与声音事件元数据分离
        ↓
统一时间片结构
        ↓
停顿 + 标点 + 目标句长重建句子
        ↓
目标段落长度排版
        ↓
可读文本 + 原始可追溯文本
```

文本纠错层提供四个显式策略：`basic`、`terminology`、`local`、`api`。其中 API 策略
通过 OpenAI-compatible `/chat/completions` 调用用户指定模型。提供商配置存储在应用数据
目录；Windows API Key 使用当前用户 DPAPI 加密，接口响应和诊断包永不返回明文 Key。

## v1.6.0 RAG 评测与优化闭环

新增 `rag_evaluation_cases` 与 `rag_evaluation_runs` 两类持久化数据：

- 评测题保存问题、正确父文档、参考答案、关键要点、拒答预期及 tune/test 划分；
- 评测运行保存检索结果、发送给回答模型的上下文、回答、引用、耗时、请求量、Token 和失败诊断；
- `rag_runtime.json` 保存正式知识库问答默认配置；
- 参数实验复用现有检索评测链路，不调用回答模型；
- 端到端问答评测默认使用规则代理指标，不额外调用裁判 LLM。

该设计保持模块化单体边界，不引入新的队列、向量数据库或微服务。
