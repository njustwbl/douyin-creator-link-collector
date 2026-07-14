# Third-party notices

CareerAgent combines original application code with optional open-source runtimes, models, and API providers. The repository does not redistribute model weights, Ollama binaries, Chromium, FFmpeg, PyTorch, or remote-model access.

## Douyin signing helpers

The isolated helpers under:

- `app/modules/collection/providers/douyin/abogus.py`
- `app/modules/collection/providers/douyin/xbogus.py`

contain or adapt Apache License 2.0 implementations associated with the F2 and Douyin_TikTok_Download_API ecosystems. Original attribution is retained in source headers where applicable.

## Application dependencies

Major dependencies include:

- FastAPI, Starlette, Uvicorn;
- SQLAlchemy and aiosqlite;
- HTTPX and Playwright;
- Beautiful Soup;
- python-docx;
- RapidFuzz;
- Transformers and sentence-transformers.

Each dependency remains governed by its upstream license.

## ASR and OCR

Optional local processing uses:

- FunASR;
- SenseVoiceSmall model weights;
- Paraformer, FSMN-VAD, and CT-Punc model weights;
- faster-whisper and CTranslate2;
- PyTorch and torchaudio;
- RapidOCR and ONNX Runtime;
- imageio-ffmpeg and FFmpeg;
- SoundFile.

Model weights are downloaded locally on demand and remain subject to their model-card licenses. Review the latest upstream terms before redistribution or commercial use.

## Ollama and Qwen models

CareerAgent can install or connect to Ollama and can download locally selected chat and embedding models, including the configured Qwen models. Ollama and all model weights remain under their respective upstream licenses and terms. CareerAgent does not bundle or relicense them.

## OpenAI-compatible APIs

CareerAgent may call user-configured OpenAI-compatible chat and embedding endpoints. The project does not provide, resell, or grant access to a remote model. Users are responsible for provider accounts, API keys, prices, data policies, model licenses, and terms of service.

API keys are excluded from logs and diagnostic packages. On Windows, remembered keys are protected using the current user's DPAPI context.
