# Contributing

## 开发环境

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
playwright install chromium
```

本地 ASR/OCR 功能另行安装 `requirements-asr.txt`。

## 提交前检查

```bash
ruff check .
pytest -q
python -m compileall -q app tests bootstrap.py
```

## 代码边界

- Router 只负责 HTTP 输入输出和错误映射；
- Service 编排业务流程；
- Repository 负责数据库读写；
- Provider/Engine/Client 隔离外部平台和模型；
- 不在 UI 代码中直接实现采集或模型业务逻辑；
- 新增任务必须考虑状态、重试、错误码、Trace 和幂等性；
- 原始文本不得被清洗稿或最终稿覆盖。

## Pull Request

请说明：

1. 解决了什么问题；
2. 是否修改数据结构；
3. 是否增加依赖或模型下载；
4. 是否影响 Cookie、API Key、日志或诊断包；
5. 已运行哪些测试。
