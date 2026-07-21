# Third-party notices

CareerAgent depends on third-party open-source libraries, local model runtimes and optional remote model services. This file provides a practical attribution summary; the license files and model cards published by each upstream project remain authoritative.

## Douyin request helpers

The isolated signing helpers under:

- `app/modules/collection/providers/douyin/abogus.py`
- `app/modules/collection/providers/douyin/xbogus.py`

are adapted from Apache License 2.0 implementations associated with the F2 / Douyin_TikTok_Download_API ecosystem and the referenced `douyin-downloader` project. Original attribution and license headers are retained where applicable.

## Web and database stack

The application uses components including:

- FastAPI and Uvicorn;
- SQLAlchemy, Alembic, asyncpg and aiosqlite;
- PostgreSQL and pgvector;
- Pydantic, HTTPX, Typer and Rich;
- Playwright and Beautiful Soup;
- python-docx, NumPy and RapidFuzz.

Review the corresponding upstream license before redistributing a packaged build.

## Local transcription and OCR

Optional local processing uses components including:

- FunASR;
- SenseVoiceSmall model weights;
- Paraformer model weights;
- faster-whisper and CTranslate2;
- PyTorch and torchaudio;
- RapidOCR and ONNX Runtime;
- FFmpeg or imageio-ffmpeg.

Model weights are not bundled in the project ZIP and are downloaded to the user's local model directory when needed. Model weights may use licenses different from the runtime library license. Review the current upstream model card before commercial redistribution or hosted use.

## Local language and embedding models

Ollama is an optional external runtime. Users may install models such as Qwen chat and embedding models separately. CareerAgent does not redistribute Ollama or model weights in the code package. Model usage is governed by the model publisher's license and Ollama's applicable terms.

The optional local Reranker path uses Transformers and sentence-transformers-compatible runtimes. The selected model's own model-card license must also be reviewed.

## OpenAI-compatible APIs

CareerAgent can call user-configured OpenAI-compatible Chat Completions and Embedding endpoints. CareerAgent does not bundle, resell or grant access to remote models. Users are responsible for the selected provider's:

- account and API key;
- pricing and usage limits;
- data retention and privacy policy;
- model license;
- terms of service.

API keys are excluded from logs and diagnostic packages. On Windows, remembered keys are protected with the current user's DPAPI where supported.

## Distribution responsibility

Before publishing a binary package, Docker image, hosted service or commercial derivative:

1. include all required upstream notices;
2. verify the exact installed dependency versions and licenses;
3. verify every downloaded model's current license;
4. avoid distributing model files or browser login data without permission;
5. do not include user databases, API keys, cookies, logs or private exports.
