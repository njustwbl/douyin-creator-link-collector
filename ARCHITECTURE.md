# CareerAgent Architecture

## 1. Design goals

CareerAgent uses a **modular monolith** rather than premature microservices. A single FastAPI process keeps local deployment simple, while domain modules maintain boundaries that can later be extracted into workers or services.

Primary goals:

1. preserve raw source and every derived text version;
2. make each stage observable and restartable;
3. avoid repeated ASR, LLM, Embedding, and indexing costs;
4. support API and local-model implementations behind stable interfaces;
5. keep user credentials and content local by default;
6. allow collection, transcription, refinement, retrieval, and evaluation to evolve independently.

## 2. Domain modules

### `collection`

Responsibilities:

- parse creator and content URLs;
- collect creator metadata and public content lists;
- distinguish video, gallery, and article items;
- run single-creator and multi-creator jobs;
- deduplicate by platform ID;
- record run events, errors, retries, and trace IDs;
- expose pending content for downstream processing.

Provider strategy:

```text
DouyinHybridProvider
├── Fast API provider
│   ├── saved browser session snapshot
│   ├── signed pagination requests
│   └── exponential backoff
└── Browser provider
    ├── one creator profile page
    ├── network response interception
    └── DOM fallback
```

### `transcription`

Responsibilities:

- resolve a content URL to a stable item;
- download media using bounded limits and timeouts;
- route by content type;
- run SenseVoice, Paraformer, or faster-whisper;
- run RapidOCR for gallery posts;
- extract long-article content through structured and rendered fallbacks;
- persist raw text, model metadata, runtime device, duration, and errors;
- schedule background batches and retry failed children.

### `refinement`

Responsibilities:

- deterministic text normalization;
- domain glossary corrections;
- API or local Qwen readable-text refinement;
- numeric, URL, version, length, and edit-ratio validation;
- keep raw, normalized, refined, and human-final versions separately;
- prepare document-level metadata for the knowledge base.

### `knowledge_base`

Responsibilities:

- prepare approved documents;
- chunk text and build independent index profiles;
- generate embeddings through API or Ollama;
- retrieve using Dense, BM25, weighted hybrid, or RRF;
- apply MMR and optional reranking;
- answer strictly from retrieved evidence with numbered citations;
- manage retrieval and end-to-end RAG evaluation sets;
- diagnose failures and compare parameter experiments;
- publish the selected runtime configuration.

### `local_models`

Responsibilities:

- store Ollama settings;
- install the official Windows portable package;
- verify archives and manage download resumes;
- configure local model directories;
- pull and test chat and embedding models sequentially;
- avoid modifying ASR/PyTorch environments.

## 3. Application layers

```text
Web UI
  ↓ HTTP/JSON
FastAPI routers
  ↓
Domain services
  ↓
Providers / engines / validators
  ↓
Repositories
  ↓
SQLite + local filesystem + optional remote APIs
```

The web UI does not contain collection, ASR, or RAG business rules. CLI and HTTP entry points share the same service layer.

## 4. Data lifecycle

```text
Creator
  └── ContentItem
        └── TranscriptionJob
              ├── Raw text
              ├── Quality assessment
              ├── Cross-model review
              └── RefinementJob
                    ├── Normalized text
                    ├── Refined text
                    ├── Human final text
                    └── Knowledge preparation
                          └── Chunk / Embedding profile
                                ├── Retrieval evaluation
                                └── RAG answer evaluation
```

Each content item has a semantic version/fingerprint. Interaction metrics can update without causing expensive downstream text processing. A semantic change marks the item pending again.

## 5. Observability

Every long-running task records:

- stable task ID;
- trace ID;
- current stage and progress;
- provider/model/device;
- elapsed time;
- structured error code;
- retry and fallback events;
- redacted technical details.

Application logs are JSONL and rotate by size. Diagnostic bundles intentionally exclude cookies, browser profiles, remembered API keys, model files, and user media.

## 6. Storage

Default Windows data lives outside the code directory under the user's local application-data path. The user may separately configure:

- Python runtime and CUDA environment;
- model cache;
- database and browser session;
- temporary media cache;
- Word/TXT exports;
- Ollama application and model roots.

This separation allows code upgrades without losing user data or requiring a new Douyin login.

## 7. Security boundaries

- API keys are never returned by settings endpoints;
- remembered keys use Windows DPAPI;
- sensitive query parameters and cookies are redacted from logs;
- browser verification is manual;
- downloads enforce size and timeout limits;
- external model/provider terms remain the user's responsibility.

## 8. Planned evolution

The modular boundaries support later extraction into:

- collector workers;
- transcription GPU workers;
- LLM/Embedding workers;
- PostgreSQL persistence;
- object storage;
- a durable queue such as Dramatiq, Celery, or ARQ;
- multi-user workspaces and permissions.
