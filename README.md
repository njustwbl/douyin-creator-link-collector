# Douyin Creator Link Collector

> 输入抖音博主主页链接，快速获取作者公开资料与前 N 条公开作品，并完成类型识别、幂等入库、增量检测和全链路诊断。

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688)
![SQLite](https://img.shields.io/badge/SQLite-Local%20First-003B57)
![License](https://img.shields.io/badge/License-Apache--2.0-blue)

![CareerAgent Collector 界面](docs/images/collector-dashboard.png)

## 项目定位

当前版本聚焦抖音主页采集，支持：

- 输入抖音博主主页长链或分享短链；
- 获取作者昵称、简介、抖音号、粉丝数、获赞数、公开作品数等资料；
- 分页获取前 N 条公开作品；
- 独立识别视频、普通图文和长文章；
- 保存标题、描述、发布时间、封面、话题和互动数据；
- 使用 `platform + aweme_id` 幂等去重；
- 区分首次发现、内容更新和内容未变化；
- 极速接口失败后自动降级到浏览器主页采集；
- 记录任务阶段、错误码、Trace ID 和诊断日志；
- 提供本地 Web 界面、FastAPI 接口和 CLI；
- 支持 CSV、JSON 和诊断包导出。

## 核心亮点

### 1. API-first 的混合采集策略

```text
DouyinHybridProvider
├── DouyinFastApiProvider       默认使用分页接口，速度快
└── DouyinBrowserProvider       接口失败时只打开目标主页兜底
```

系统不会逐条打开作品详情页。正常情况下，几十条作品只需要少量分页请求；浏览器仅用于首次登录和接口失败兜底。

### 2. 可替换的 Provider 架构

采集逻辑与业务层解耦。后续新增 Bilibili、YouTube、网页或本地文档时，只需实现统一 Provider 协议，不需要修改数据库、Web 界面和后续知识处理模块。

### 3. 面向后续 AI 工作流的增量设计

同一作品再次采集时，系统会区分：

- `new_count`：首次发现；
- `updated_count`：标题、正文、类型、发布时间、话题等发生变化；
- `unchanged_count`：语义内容未变化。

点赞和评论数字变化不会触发内容重新处理。后续可以只为新增或真正变化的作品创建转写、知识卡和 Embedding 任务。

### 4. 可观测性与错误诊断

每次任务都有独立 `run_id` 和 `trace_id`，并按阶段记录：

```text
输入校验 → 链接解析 → 登录状态 → 极速接口
→ 浏览器兜底 → 数据标准化 → 数据库写入 → 完成
```

错误会被转换为稳定错误码，例如：

- `NOT_PROFILE_URL`
- `LOGIN_REQUIRED`
- `RATE_LIMITED`
- `HUMAN_VERIFICATION_REQUIRED`
- `UPSTREAM_FORMAT_CHANGED`
- `DATABASE_LOCKED`

详细列表见 [ERROR_CODES.md](ERROR_CODES.md)。

## 技术栈

| 层级 | 技术 |
|---|---|
| Web API | FastAPI、Pydantic |
| 数据访问 | SQLAlchemy Async、aiosqlite |
| 采集 | HTTPX、Playwright |
| 浏览器登录 | Playwright Persistent Context |
| 本地存储 | SQLite |
| 前端 | 原生 HTML、CSS、JavaScript |
| 日志 | JSON Lines、RotatingFileHandler |
| 测试 | pytest、pytest-asyncio |

## 快速开始

### Windows 一键启动

要求：Windows 10/11，已安装 Python 3.11 或更高版本。

1. 下载或克隆仓库；
2. 双击 `CareerAgent_Start.bat`；
3. 首次运行会自动创建 `.venv`、安装依赖和 Playwright Chromium；
4. 浏览器会自动打开 `http://127.0.0.1:8000/`；
5. 首次使用点击“首次登录抖音”，在 Chromium 中完成登录后关闭窗口；
6. 输入博主主页链接、采集数量和作品类型，点击“开始采集”。

### 开发方式启动

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements-dev.txt
playwright install chromium
uvicorn app.main:app --reload
```

访问：

- 管理界面：`http://127.0.0.1:8000/`
- OpenAPI 文档：`http://127.0.0.1:8000/docs`

## API 示例

```http
POST /api/v1/collections/douyin/profile
Content-Type: application/json
```

```json
{
  "url": "https://www.douyin.com/user/SEC_USER_ID",
  "count": 20,
  "media_type": "all"
}
```

主要接口：

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/collections/douyin/login` | 打开登录浏览器 |
| POST | `/api/v1/collections/douyin/profile` | 采集作者及作品 |
| GET | `/api/v1/collections/runs` | 最近任务 |
| GET | `/api/v1/collections/runs/{run_id}` | 单次任务阶段日志 |
| GET | `/api/v1/collections/diagnostics/download` | 导出诊断包 |

## 项目结构

```text
career-agent-collector/
├── app/
│   ├── api/v1/                  # API 聚合路由
│   ├── core/                    # 配置与日志
│   ├── db/                      # 数据库初始化与会话
│   ├── modules/collection/
│   │   ├── providers/           # 平台 Provider
│   │   ├── errors.py            # 统一错误分类
│   │   ├── models.py            # 数据模型
│   │   ├── repository.py        # 数据访问
│   │   ├── service.py           # 业务编排
│   │   └── router.py            # 采集接口
│   └── web/                     # 本地管理界面
├── tests/                       # 自动化测试
├── docs/                        # 开发、上传与作品集文档
├── data/                        # 本地运行数据，不提交 Git
├── CareerAgent_Start.bat        # Windows 一键启动
├── bootstrap.py                 # 环境检查、依赖安装与启动
└── requirements*.txt
```

完整架构说明见 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 数据与隐私

以下内容只保存在本机，已通过 `.gitignore` 排除：

- `.env`
- SQLite 数据库
- 浏览器登录目录
- Cookie 快照
- 日志、导出文件和诊断包

**不要把 `data/`、`.env`、Cookie、Token 或真实用户数据提交到 GitHub。**

安全报告方式见 [SECURITY.md](SECURITY.md)。

## 测试

```bash
pytest -q
python -m compileall -q app tests bootstrap.py
node --check app/web/static/app.js
ruff check app tests bootstrap.py
```

GitHub Actions 会在推送和 Pull Request 时自动执行基础检查。

## 已知限制

- 当前只支持单机、单用户和 SQLite；
- 平台接口属于非稳定外部依赖，字段或签名变化可能导致采集失败；
- 不提供验证码自动绕过、私密账号访问或权限提升；
- 仅采集当前登录账号能够正常查看的公开内容；
- 项目当前是 CareerAgent 的第一阶段模块，尚未包含转写、RAG 和学习 Agent。

## Roadmap

- [ ] 异步任务队列与可取消任务
- [ ] 定时增量采集和失败重试策略
- [ ] Bilibili、YouTube 和本地文档 Provider
- [ ] ContentAsset 与转写任务模型
- [ ] ASR 术语纠错和人工确认队列
- [ ] 知识卡、Chunk、Embedding 与 RAG
- [ ] PostgreSQL、Alembic 和对象存储
- [ ] Tauri/WebView2 桌面封装
- [ ] OpenTelemetry / Langfuse 可观测性

## 合规说明

本项目用于个人学习、技术研究和公开内容管理。使用者应遵守适用法律、平台规则、访问权限和合理请求频率。项目不用于绕过验证码、访问私密内容、规避权限控制或批量滥用平台服务。详见 [docs/COMPLIANCE.md](docs/COMPLIANCE.md)。

## 第三方代码与许可证

本项目采用 [Apache License 2.0](LICENSE)。部分签名辅助代码来自或改编自 Apache-2.0 许可项目，原始声明保留在源文件中，详细归属见：

- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
- [NOTICE](NOTICE)

## 作品集说明

如何在简历和面试中介绍该项目，见 [docs/PORTFOLIO_GUIDE.md](docs/PORTFOLIO_GUIDE.md)。
