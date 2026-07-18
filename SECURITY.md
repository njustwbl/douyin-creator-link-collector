# Security Policy

## Sensitive data

Do not commit API keys, cookies, browser profiles, model-provider credentials, database passwords, local databases, logs, diagnostic archives, or user content.

The repository `.gitignore` excludes the default runtime locations, but contributors must still review staged files before every push.

## Reporting a vulnerability

Please report security issues privately to the repository owner instead of opening a public issue. Include:

- affected version;
- reproduction steps;
- impact;
- suggested mitigation, when available.

## Scope notes

CareerAgent runs local browser automation and model processes. Users should only load trusted code and model artifacts, keep dependencies updated, and verify upstream model and API-provider terms.
