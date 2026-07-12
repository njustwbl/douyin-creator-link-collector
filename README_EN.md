# CareerAgent

CareerAgent is a local-first content ingestion, transcription, refinement, and retrieval-evaluation platform designed for AI career learning workflows.

It turns public short-form content into traceable knowledge assets through the following pipeline:

```text
Collection
→ Video ASR / Gallery OCR / Article Extraction
→ Quality Gate and Human Reference Text
→ Cleaning and Terminology Refinement
→ Knowledge Preparation
→ Embedding Indexes
→ Dense / Hybrid / RRF Retrieval
→ Optional Reranking
→ Single-label and Multi-label Retrieval Evaluation
```

## Highlights

- FastAPI + async SQLAlchemy + SQLite;
- API-first Douyin creator collection with browser fallback;
- SenseVoice, Paraformer, Whisper, RapidOCR, and article extraction;
- batch processing, task recovery, structured errors, trace IDs, and diagnostics;
- automatic text quality scoring, cross-ASR comparison, and Chinese CER;
- deterministic cleaning, domain terminology correction, local model refinement, and OpenAI-compatible API refinement;
- embedding model profiles, Dense/BM25 hybrid search, Reciprocal Rank Fusion, MMR diversification, and optional reranking;
- retrieval test sets with Hit@K, Recall@K, Precision@K, and full-hit metrics;
- local storage controls and Windows DPAPI-protected API keys.

## Quick Start

Recommended environment: Windows 10/11 and Python 3.11 or 3.12.

For normal users, double-click:

```text
CareerAgent_Start.bat
```

For development:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
playwright install chromium
uvicorn app.main:app --reload
```

Optional local ASR/OCR dependencies:

```bash
pip install -r requirements-asr.txt
```

## Security and Local Data

The repository excludes cookies, browser profiles, databases, logs, media, model weights, exported documents, `.env`, and API keys. See [SECURITY.md](SECURITY.md).

## Current Scope

CareerAgent is currently a Windows-first, local, single-user application. It is not a hosted SaaS platform. Douyin interfaces may change, and users must comply with applicable terms, copyright, privacy, and local laws.

For the full Chinese documentation, see [README.md](README.md).

## License

Apache-2.0 for the main project. Third-party notices and model-license considerations are documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
