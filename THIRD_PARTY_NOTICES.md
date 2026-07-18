# Third-Party Notices

CareerAgent depends on third-party libraries, services, models, and platform data. This document summarizes major categories but does not replace upstream license texts.

## Douyin signing helpers

The isolated signing helpers under:

- `app/modules/collection/providers/douyin/abogus.py`
- `app/modules/collection/providers/douyin/xbogus.py`

are adapted from Apache License 2.0 implementations associated with the F2 and Douyin/TikTok download API ecosystem. Original attribution and license headers are retained where available. The rest of CareerAgent is independently organized around its own Provider, Service, Repository, API, database, and Web UI layers.

## Backend and data

Major dependencies include FastAPI, Starlette, Uvicorn, Pydantic, SQLAlchemy, Alembic, asyncpg, aiosqlite, pgvector-python, PostgreSQL, and the pgvector PostgreSQL extension. Each remains subject to its upstream license.

The Docker setup uses the public `pgvector/pgvector` image. The image and bundled PostgreSQL components remain subject to their respective upstream licenses.

## Browser and collection

Playwright and its downloaded Chromium runtime remain subject to their upstream licenses and terms. CareerAgent does not bypass login challenges or CAPTCHAs. Users are responsible for complying with platform terms, copyright, privacy, and applicable law.

## Local transcription and OCR

Optional local processing uses components such as:

- FunASR and SenseVoice;
- Paraformer models;
- PyTorch and torchaudio;
- faster-whisper and CTranslate2;
- FFmpeg binaries supplied through the selected runtime;
- RapidOCR and ONNX Runtime;
- Beautiful Soup.

Model weights are not bundled in this repository. They are downloaded locally on demand and may have model-specific licenses that differ from the software library license.

## Local LLM, Embedding, and Reranker

CareerAgent can interact with Ollama and locally downloaded Qwen chat, embedding, and reranker models. Ollama, model runtimes, model weights, and tokenizer files remain subject to their upstream licenses and model cards. Review the current upstream terms before redistribution or commercial use.

## Hosted APIs

CareerAgent can call user-configured OpenAI-compatible chat, embedding, and reranking endpoints. CareerAgent does not bundle, resell, or grant access to these services. Users are responsible for provider accounts, API keys, pricing, data handling, model licenses, and terms.

## User and platform content

The CareerAgent Apache License does not grant rights to third-party videos, images, articles, transcripts, model outputs, or user data processed by the application. Users must have the necessary rights and permissions for their use case.
