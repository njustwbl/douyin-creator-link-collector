# Contributing

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-ci.txt
playwright install chromium
```

Run checks:

```bash
pytest -q
ruff check app tests bootstrap.py careeragent_location.py configure_storage.py migrate_to_lightweight.py
python -m compileall -q app tests bootstrap.py
node --check app/web/static/app.js
```

## Contribution boundaries

- keep platform-specific behavior inside Provider modules;
- keep routers thin and put business logic in services;
- do not write another module's tables directly;
- preserve raw data and derived text version history;
- add a stable error code for new user-facing failure modes;
- add tests for parsing, fallback, retry, and idempotency behavior;
- avoid loading heavyweight models at import time;
- do not commit model files, media, databases, cookies, keys, or personal exports.

## Pull requests

A pull request should include:

1. the problem being solved;
2. the implementation approach;
3. compatibility or migration impact;
4. tests added or updated;
5. screenshots with synthetic data for UI changes;
6. documentation updates when behavior changes.

## Commit examples

```text
feat(retrieval): add configurable score threshold
fix(article): reject title-only rendered candidates
test(collection): cover filtered batch results
docs: update local model deployment guide
```
