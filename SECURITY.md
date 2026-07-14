# Security policy

## Supported version

Security fixes are applied to the latest published release.

## Reporting a vulnerability

Do not include API keys, cookies, browser profiles, private content, diagnostic packages, or personal filesystem paths in a public issue.

Use a private GitHub security advisory when available. Include:

- affected version;
- reproduction steps using synthetic data;
- expected and actual behavior;
- impact assessment;
- relevant redacted logs.

## Secrets and local data

CareerAgent may locally store:

- Douyin browser session data;
- OpenAI-compatible API settings;
- SQLite records;
- text, media caches, and exports;
- model files and diagnostic logs.

The repository excludes these through `.gitignore`. Remembered API keys use Windows DPAPI and are never returned through settings endpoints. Diagnostic bundles redact known cookie, token, and signing fields.

## Deployment guidance

The default application binds to localhost for personal use. Do not expose it directly to the public internet without adding authentication, authorization, TLS, request limits, audit controls, and a review of all file-opening/system-management endpoints.

## External services

Users are responsible for the security, data policy, pricing, terms, and licensing of any selected API provider, content platform, Ollama model, ASR model, or OCR dependency.
