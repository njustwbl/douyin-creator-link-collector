# CareerAgent

> A local-first AI content processing, RAG evaluation, and multi-layer industry intelligence question-answering platform.

**Current version: v1.23.0**

CareerAgent turns public short-form content into traceable knowledge and intelligence assets through a complete local pipeline:

```text
Collection
→ Video ASR / Image OCR / Article extraction
→ Quality gates and safe refinement
→ Human-approved final text
→ PostgreSQL / pgvector indexing
→ Dense / BM25 / Hybrid / RRF / Reranking
→ Cited RAG and regression evaluation
→ Claims, clusters, canonical events, statistics and creator profiles
→ Multi-layer intelligence QA
→ Alerts, reports, quality and performance governance
```

## Highlights

- API-first public content collection with browser fallback and diagnostic traces;
- SenseVoice, Paraformer, faster-whisper and RapidOCR pipelines;
- versioned raw, cleaned, corrected and human-approved text;
- parent-child chunking, incremental indexing, hybrid retrieval and optional Qwen reranking;
- cited answers, low-confidence refusal and RAG regression evaluation;
- structured entities, claims, events, learning items and resources;
- trend statistics, claim clustering, event deduplication, alerts, reports and creator profiles;
- three QA modes: normal RAG, industry intelligence analysis and automatic routing;
- persistent background jobs with progress, locks, cancellation, retry and restart recovery;
- PostgreSQL 17, pgvector, Alembic and SQLite compatibility mode.

## Architecture

CareerAgent is a modular monolith. Domain boundaries are explicit while local deployment remains simple:

```text
app/modules/
├── collection
├── transcription
├── refinement
├── knowledge_base
├── intelligence
├── jobs
└── local_models
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

## Quick start

Windows users can start with:

1. install Python 3.11/3.12 and Docker Desktop;
2. clone or download the repository;
3. run `CareerAgent_Start.bat`;
4. choose local data and export directories;
5. complete the platform login in the opened browser when collection is first used.

Model weights, user data, cookies, API keys and databases are not included in the repository.

## Development

```bash
python -m venv .venv
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload
```

For CI checks:

```bash
pip install -r requirements-ci.txt
ruff check app tests bootstrap.py careeragent_location.py configure_storage.py database_bootstrap.py
python -m compileall -q app tests bootstrap.py
node --check app/web/static/app.js
pytest -q --ignore=tests/test_background_jobs.py
pytest -q tests/test_background_jobs.py
```

## Privacy and compliance

The repository excludes local cookies, browser profiles, databases, model files, media, logs, diagnostic packages, exports and secrets. Users are responsible for complying with platform terms, copyright, privacy requirements and model licenses.

## License

Apache License 2.0. Third-party code and model runtimes remain governed by their upstream licenses. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
