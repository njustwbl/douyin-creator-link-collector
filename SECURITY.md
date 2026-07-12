# Security Policy

## 不应提交到仓库的内容

- `.env`；
- API Key、Access Token、Cookie；
- Playwright 浏览器用户目录；
- `douyin_session.json` 或类似登录快照；
- SQLite 数据库；
- 日志和诊断包；
- 用户导出的 Word/TXT/JSON；
- 视频、音频、图片和模型权重。

`.gitignore` 已覆盖这些常见文件，但提交者仍应在每次推送前检查：

```bash
git status
git diff --cached
```

## 密钥存储

- Windows 下，用户选择“记住 Key”时使用当前 Windows 用户的 DPAPI；
- API Key 不应返回前端页面或写入日志；
- 诊断包导出前应进行敏感字段脱敏；
- Ollama 等本地接口可以不配置 API Key。

## 报告安全问题

请不要在公开 Issue 中粘贴真实 Cookie、API Key、数据库或完整诊断日志。可以仅提供：

- 稳定错误码；
- Trace ID；
- 脱敏后的阶段日志；
- 可复现步骤；
- 软件版本和操作系统。

## 支持范围

当前项目是本地单用户应用，默认只绑定 `127.0.0.1`。如自行改为公网监听，必须额外增加身份认证、HTTPS、CSRF/CORS 策略、访问审计、请求限流和密钥管理。
