# Changelog

All notable public releases of CareerAgent are documented here.

## [1.7.2] - 2026-07

### Changed

- replaced silent Ollama installer execution with the official Windows portable archive;
- added resumable download and retry handling;
- added release metadata, SHA-256 verification when available, and ZIP CRC/layout validation;
- standardized Ollama installation under the selected `app` directory and models under `models`;
- kept local chat and embedding model downloads/tests sequential to reduce VRAM contention;
- preserved complete separation from SenseVoice, Paraformer, faster-whisper, and PyTorch/CUDA.

## [1.7.1] - 2026-07

### Added

- one-click Windows deployment for Ollama and Qwen local models;
- install-root selection, progress reporting, service startup, model download, and live tests;
- disk-space checks and isolated Ollama model storage.

## [1.7.0] - 2026-07

### Added

- local Qwen3.5-4B refinement through Ollama;
- local Qwen embedding provider;
- local or API model selection for knowledge preparation and RAG answers;
- unified Ollama settings and health tests.

### Removed

- the old local 1.5B correction runtime path.

## [1.6.0] - 2026-07

### Added

- end-to-end RAG evaluation sets;
- failure diagnosis across retrieval, ranking, context, answer, citation, and refusal stages;
- retrieval parameter experiments;
- publishing the selected configuration as the production default.

## [1.5.0] - 2026-07

### Added

- citation-grounded knowledge-base question answering;
- RRF, weighted hybrid, Dense, MMR, and adaptive reranking;
- evidence-insufficient and invalid-citation safe fallback.

Detailed release notes are available under [`docs/releases`](docs/releases/).
