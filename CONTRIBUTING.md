# Contributing

## Development setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt
playwright install chromium
```

Use SQLite for lightweight development:

```env
CAREERAGENT_DATABASE_MODE=sqlite
APP_ENV=test
```

## Pull requests

- keep domain logic out of frontend event handlers;
- preserve Router → Service → Repository/Provider boundaries;
- add tests for behavior changes;
- avoid logging credentials, cookies, tokens or raw signing URLs;
- update documentation and CHANGELOG for user-visible changes;
- do not bundle model weights, browser profiles or user-generated data;
- keep long-running operations compatible with the persistent job center.

## Checks

```bash
pip install -r requirements-ci.txt
ruff check app tests bootstrap.py careeragent_location.py configure_storage.py database_bootstrap.py backup_postgres.py restore_postgres.py migrate_sqlite_to_postgres.py migrate_to_lightweight.py
python -m compileall -q app tests bootstrap.py
node --check app/web/static/app.js
find app/web/static/js -name '*.js' -print0 | xargs -0 -n1 node --check
node tools/frontend_smoke.js
pytest -q --ignore=tests/test_background_jobs.py
pytest -q tests/test_background_jobs.py
```
