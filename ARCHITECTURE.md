# Architecture

## 设计目标

CareerAgent 当前采用模块化单体，而不是过早拆分微服务。采集、文本化、质量评估和纠错共享一个 FastAPI 进程与 SQLite 数据库，但通过 Router、Service、Repository 和 Provider 隔离业务边界。后续知识卡和 RAG 可以作为新模块加入，不需要重写已有采集链路。

## 模块划分

```text
app/
├── api/v1/                 API 聚合
├── core/                   配置、存储、计算设备、日志与密钥
├── db/                     SQLAlchemy Async 会话和自动迁移
├── modules/
│   ├── collection/         作者与作品采集、批次、诊断
│   ├── transcription/      视频 ASR、图文 OCR、文章提取、质量门禁
│   └── refinement/         清洗、术语纠错、本地模型、API 整理
└── web/                    本地 Web 管理界面
```

## 核心数据流

```text
Creator / ContentItem
        ↓
TranscriptionJob
        ├── raw_text
        └── text
        ↓
QualityAssessment
        ↓
TextRefinementState
        ├── normalized_text
        ├── corrected_text
        └── final_text
```

后续知识库只读取 `final > corrected > normalized > raw` 的最高可用版本，并通过内容指纹避免重复向量化。

## 采集策略

```text
输入主页链接
→ URL 解析与 sec_uid 标准化
→ Fast API Provider 分页采集
→ 短暂失败指数退避
→ 必要时 Browser Provider 只打开目标主页兜底
→ 标准化、幂等 Upsert、变化检测
```

采集层不直接承担 ASR 或知识抽取。它只负责回答“发现了什么、来自谁、什么时候发布、是否发生变化”。

## 文本化策略

- 视频：媒体下载和音频提取可以并发，ASR 推理通过锁控制显存竞争；
- 图文：按图片顺序执行 OCR 并保留来源顺序；
- 文章：详情接口、页面 JSON 和隐藏浏览器逐级降级；
- 批任务：队列状态写入数据库，程序重启后恢复未完成任务；
- 媒体默认作为临时缓存，文本和质量结果长期保存。

## 文本纠错安全边界

原始稿永不覆盖。所有处理生成新版本，并校验：

- 数字、日期、百分比和版本号；
- URL、邮箱、路径和技术标识；
- 长度比例和字符修改比例；
- 新增、删除和高风险改写。

高风险结果进入人工复核状态，而不是自动成为最终稿。

## 可观测性

每个任务包含 `job_id / batch_id / trace_id`，并记录阶段、耗时、模型、设备、错误码和技术详情。日志按大小轮转，并可导出诊断包；Cookie、Token、API Key 和签名参数会被脱敏。

## 后续扩展

计划新增：

```text
knowledge/       知识卡和概念关系
retrieval/       Chunk、Embedding、Hybrid Search、Rerank
learning/        测验、掌握度和间隔复习
incubation/      项目需求与 Backlog
interview/       面试问题和评分
observability/   LLM Trace、Prompt 版本、Bad Case 和 Eval
```
