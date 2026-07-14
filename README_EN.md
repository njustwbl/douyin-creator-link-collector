# CareerAgent

CareerAgent is a local-first AI content ingestion, transcription, refinement, retrieval, and RAG evaluation platform built for AI learning and career preparation.

**Current release: v1.7.2**

## Pipeline

```text
Douyin collection
→ Video ASR / Gallery OCR / Article extraction
→ Quality gate
→ Text normalization and terminology correction
→ Human-approved final text
→ Knowledge preparation
→ Embedding and hybrid retrieval
→ Citation-grounded RAG answers
→ Evaluation, diagnosis, and parameter optimization
```

## Highlights

- API-first Douyin collection with browser fallback and idempotent persistence;
- SenseVoice, Paraformer, and faster-whisper transcription;
- RapidOCR for gallery posts and rendered-page fallback for long articles;
- quality scores, cross-model checks, CER, and human review;
- deterministic cleanup, domain glossary, OpenAI-compatible APIs, and local Qwen via Ollama;
- Dense, BM25, weighted hybrid, RRF, MMR, and optional reranking;
- citation-grounded knowledge-base answers with safe fallback;
- end-to-end RAG evaluation, failure classification, and parameter experiments;
- structured trace IDs, diagnostic events, rotating logs, and redacted support bundles;
- configurable runtime, model, cache, database, and export locations.

## Quick start on Windows

1. Install Python 3.11 or 3.12.
2. Extract the repository.
3. Run `CareerAgent_Start.bat`.
4. Select local storage locations during the first-run wizard.
5. Complete Douyin login in the browser before collecting content.

Optional ASR and Ollama model files are downloaded locally and are not included in this repository.

## Development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload
```

Tests:

```bash
pip install -r requirements-ci.txt
pytest -q
```

The prepared release passed 84 offline tests.

## Privacy

The repository excludes API keys, cookies, browser profiles, databases, logs, media caches, model weights, and user exports. See [SECURITY.md](SECURITY.md).

## License

Apache License 2.0 for the original CareerAgent code. Third-party components remain under their respective licenses. See [NOTICE](NOTICE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
