# Security policy

## Sensitive local data

CareerAgent Collector can create local browser sessions, cookies, databases, logs, exports, and diagnostic packages. These files must never be committed to a public repository.

The repository `.gitignore` excludes runtime data under `data/`, `.env`, virtual environments, databases, logs, and ZIP exports.

Before every push, verify:

```bash
git status
git diff --cached
```

Do not commit:

- `.env`;
- `data/browser/`;
- `douyin_session.json`;
- SQLite database files;
- diagnostics containing real user data;
- passwords, cookies, tokens, session IDs, API keys, or personal information.

## Reporting a vulnerability

Do not publish active credentials or sensitive reproduction data in a public issue. Remove or redact secrets before sharing logs.

## Scope

This project does not implement automated CAPTCHA bypass, private-content access, privilege escalation, or credential extraction. Such features are out of scope.
