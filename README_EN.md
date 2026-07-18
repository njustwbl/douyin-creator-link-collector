# CareerAgent

CareerAgent is a local-first AI content processing, RAG evaluation, and industry intelligence platform. It converts public Douyin videos, image posts, and long-form articles into traceable knowledge assets.

**Current version: v1.21.0**

## Pipeline

```text
Collection
→ Video ASR / Image OCR / Article Extraction
→ Quality Gate and Safe Refinement
→ Human-approved Final Text
→ PostgreSQL / pgvector
→ Dense / BM25 / Hybrid / RRF / Reranking
→ Cited RAG and Evaluation
→ Entity / Claim / Event Materialization
→ Statistics / Clustering / Alerts / Reports
→ Creator Profiles and Data Governance
```

## Highlights

- API-first Douyin creator and content collection with browser fallback;
- SenseVoice, Paraformer, faster-whisper, RapidOCR, and article extraction;
- ASR quality scoring, cross-model review, CER, terminology correction, and human approval;
- parent-child chunking, incremental indexing, pgvector, BM25, RRF, MMR, and optional Qwen reranking;
- cited knowledge-base answers, evidence gating, trace logging, and RAG regression evaluation;
- structured intelligence entities, claims, events, learning items, and resources;
- trend statistics, claim clustering, canonical events, explainable alerts, reports, and creator profiles;
- PostgreSQL 17 + pgvector with SQLite compatibility mode and Alembic migrations;
- local-first storage, redacted diagnostics, configurable model/cache/export paths.

## Quick Start

On Windows, install Python 3.11/3.12 and Docker Desktop, then run:

```text
CareerAgent_Start.bat
```

For a lightweight SQLite setup, copy `.env.example` to `.env` and set:

```env
CAREERAGENT_DATABASE_MODE=sqlite
```

Developer setup:

```bash
python -m venv .venv
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload
```

Optional ASR dependencies:

```bash
pip install -r requirements-asr.txt
```

## Repository Safety

Runtime databases, browser profiles, cookies, API keys, models, media, logs, diagnostics, and exports are excluded through `.gitignore`.

## Documentation

- [Architecture](ARCHITECTURE.md)
- [GitHub upload guide](docs/GITHUB_UPLOAD_GUIDE.md)
- [Portfolio guide](docs/PORTFOLIO_GUIDE.md)
- [Release checklist](docs/RELEASE_CHECKLIST.md)

## License

Apache License 2.0. Third-party components and model weights remain subject to their upstream licenses. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
