# Third-party notices

CareerAgent is distributed under Apache License 2.0. Third-party source code, libraries, browser binaries, model runtimes, model weights, and remote services remain subject to their own upstream licenses and terms.

## Douyin signing helpers

The isolated helpers under:

- `app/modules/collection/providers/douyin/abogus.py`
- `app/modules/collection/providers/douyin/xbogus.py`

contain or adapt Apache-2.0 licensed implementations associated with the F2 / Douyin_TikTok_Download_API ecosystems and the user-provided `douyin-downloader` reference project. Original attribution is retained in the relevant source files.

## Runtime libraries

Major optional or direct dependencies include FastAPI, SQLAlchemy, HTTPX, Playwright, Beautiful Soup, python-docx, RapidFuzz, sentence-transformers, Transformers, FunASR, faster-whisper, CTranslate2, RapidOCR, ONNX Runtime, PyTorch, torchaudio, imageio-ffmpeg, FFmpeg, and Ollama. Refer to each upstream project for its current license.

## Models

CareerAgent does not redistribute model weights. Models are downloaded locally by the user and remain governed by their model cards and upstream terms, including but not limited to:

- SenseVoiceSmall and Paraformer-family models;
- Whisper-family models;
- `qwen3.5:4b`;
- `qwen3-embedding:0.6b` and `qwen3-embedding:4b`;
- `Qwen/Qwen3-Reranker-0.6B` and `Qwen/Qwen3-Reranker-4B`.

Review model licenses before redistribution or commercial use.

## OpenAI-compatible APIs

CareerAgent can call user-configured OpenAI-compatible endpoints. It does not bundle, resell, or grant access to any remote model. Users are responsible for provider accounts, API keys, pricing, data policies, model licenses, and terms of service. Remembered keys are excluded from Git and diagnostic packages and are protected with Windows DPAPI where supported.
