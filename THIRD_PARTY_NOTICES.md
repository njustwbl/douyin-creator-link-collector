# Third-party notices

CareerAgent integrates or depends on multiple open-source projects and external model/API providers. This file is informational and does not replace the upstream license texts.

## Adapted signing helpers

The isolated helpers under:

- `app/modules/collection/providers/douyin/abogus.py`
- `app/modules/collection/providers/douyin/xbogus.py`

include code adapted from Apache-2.0 licensed implementations associated with the F2 / Douyin_TikTok_Download_API ecosystem and an earlier user-provided `douyin-downloader` reference project. Original attribution and license headers are retained where applicable.

The rest of the CareerAgent application is independently organized around Provider, Service, Repository, Engine, API, and Web UI layers.

## Core libraries

The project uses libraries including FastAPI, Uvicorn, SQLAlchemy, aiosqlite, Pydantic, HTTPX, Playwright, Typer, Rich, GMSSL, Beautiful Soup, python-docx, RapidFuzz, Pytest, and Ruff. Review each package's installed metadata or upstream repository for the exact license version.

## Local transcription and OCR

Optional local processing may use:

- FunASR;
- SenseVoiceSmall model weights;
- Paraformer model weights;
- PyTorch and torchaudio;
- faster-whisper and CTranslate2;
- imageio-ffmpeg and its FFmpeg binary;
- RapidOCR and ONNX Runtime;
- Transformers;
- optional Chinese text-correction model weights.

Model weights are not distributed in this repository. They are downloaded to the user's configured local model directory. Model weights may have licenses different from the inference libraries. Review the current upstream model card before redistribution or commercial use.

## External APIs

CareerAgent can call user-configured OpenAI-compatible Chat Completions, Embedding, and Rerank endpoints. CareerAgent does not provide or resell remote model access. Users are responsible for provider accounts, API keys, pricing, rate limits, data policies, model licenses, and terms of service.

## Platform content

This repository does not include user-collected videos, images, articles, transcripts, cookies, or browser profiles. Users must ensure they have the right to access and process any content used with the application.
