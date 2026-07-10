# Contributing

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
playwright install chromium
```

## Before submitting a change

Run:

```bash
pytest -q
python -m compileall -q app tests bootstrap.py
node --check app/web/static/app.js
ruff check app tests bootstrap.py
```

## Design rules

- Platform-specific parsing must remain inside `providers/<platform>/`.
- API and UI code must not contain scraping logic.
- Do not store cookies, tokens, signed URLs, or short-lived playback URLs in primary content tables.
- Use stable platform IDs for idempotency.
- Add or update error codes when introducing a new failure mode.
- Preserve task events and trace IDs across future workflow modules.
- New external code must include compatible licensing and attribution.

## Pull requests

A pull request should explain:

1. the user problem;
2. the implementation boundary;
3. how the change was tested;
4. whether database or configuration compatibility is affected;
5. whether new third-party code or services were introduced.
