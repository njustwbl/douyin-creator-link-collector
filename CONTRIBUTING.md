# Contributing

## Development setup

```bash
python -m venv .venv
pip install -r requirements-dev.txt
playwright install chromium
```

Use SQLite for lightweight development:

```env
CAREERAGENT_DATABASE_MODE=sqlite
```

## Pull requests

- keep domain logic out of frontend event handlers;
- preserve Router → Service → Repository/Provider boundaries;
- add tests for behavior changes;
- avoid logging credentials, cookies, tokens, or raw signing URLs;
- update documentation and CHANGELOG for user-visible changes;
- do not bundle model weights or user-generated data.

## Checks

```bash
pytest -q
ruff check app tests bootstrap.py careeragent_location.py configure_storage.py database_bootstrap.py
python -m compileall -q app tests bootstrap.py
node --check app/web/static/app.js
```
