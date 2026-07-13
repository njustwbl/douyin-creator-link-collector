# Third-party notices

The isolated signing helpers under:

- `app/modules/collection/providers/douyin/abogus.py`
- `app/modules/collection/providers/douyin/xbogus.py`

are adapted from Apache License 2.0 implementations associated with the F2 / Douyin_TikTok_Download_API ecosystem and the user-provided `douyin-downloader` reference project. Their original license headers and attribution are retained where applicable.

The remaining CareerAgent Collector application code is independently organized around its own Provider, Service, Repository, API and Web UI layers.

## Local transcription dependencies

The optional local transcription feature uses:

- FunASR, distributed under its upstream open-source license;
- SenseVoiceSmall model weights from `iic/SenseVoiceSmall` / FunAudioLLM;
- PyTorch and torchaudio;
- imageio-ffmpeg and the FFmpeg binary it provides.

SenseVoiceSmall model weights are published under a model-specific license. Before redistributing the model files or using them in a commercial product, review the current upstream model license. CareerAgent does not bundle the model weights; they are downloaded to the user's local `data/models` directory on first use.


## v0.5.0 新增组件

- faster-whisper：MIT License，用于运行 Whisper 模型。
- CTranslate2：MIT License，faster-whisper 的底层推理引擎。
- RapidOCR：Apache-2.0 License，用于本地图文 OCR。
- ONNX Runtime：MIT License，用于 RapidOCR CPU 推理。
- Beautiful Soup：MIT License，用于文章 HTML 文本清理。

模型权重各自受其模型许可证约束。项目不会把模型权重打包进发布 ZIP，首次使用时由用户本机下载。

## v0.6.1 新增组件

- python-docx：MIT License，用于用户点击导出时在内存中生成 DOCX。

DOCX 不会在服务器目录自动保留副本；仅通过浏览器响应按需下载。


## v0.8.0 新增组件

- Transformers：Apache-2.0 License，用于按需加载本地中文纠错模型；
- `shibing624/chinese-text-correction-1.5b`：模型权重按其上游模型卡许可证使用，用于保守中文拼写和语法纠错。

纠错模型不会打包进 CareerAgent ZIP。用户第一次运行“保守通顺”时，程序会显示模型名称、预计体积和保存目录，确认后才下载。发布或商用前应再次核对上游模型卡中的最新许可证。

## OpenAI-compatible LLM APIs

v0.9.0 can call user-configured OpenAI-compatible Chat Completions endpoints. CareerAgent does not bundle,
resell, or grant access to any remote model. Users are responsible for the selected provider's account,
API key, pricing, data policy, model license, and terms of service. API keys are excluded from logs and
diagnostic packages; on Windows, remembered keys are protected with the current user's DPAPI.
