# Changelog

## v1.9.3

- Reordered the knowledge-base retrieval page into a clearer operational sequence: unified defaults, embedding settings, index creation, existing indexes, prepared documents, single-query comparison, and evaluation sets.

## v1.9.2

- Added unified batch reranking safety limits by maximum ratio and maximum question count.
- Applied the same limits to retrieval evaluation, end-to-end RAG evaluation, and retrieval-plan comparison.

## v1.9.1

- Added unique, descriptive index names including index ID, chunking mode, chunk count, and build time.
- Added unified retrieval defaults shared by single-query search, batch evaluation, RAG answers, end-to-end evaluation, and plan comparison.
- Added default-versus-custom configuration selection across retrieval workflows.

## v1.9.0

- Added parent-child chunking and enriched embedding text.
- Added Qwen3 Embedding 0.6B/4B parallel index support.
- Added rule-based query routing, dynamic evidence compression, and low-confidence gating.
- Added query/corpus/ranking/context/answer caches with index-version invalidation.
- Added local NDJSON streaming answers and evaluation regression baselines.
- Separated retrieval-only experiments from answer-generation evaluation.

## v1.7.2

- Added portable Ollama deployment, configurable program/model directories, resumable downloads, verification, and model smoke tests.

## v1.7.0

- Replaced the earlier local correction model with Ollama `qwen3.5:4b` and added local Qwen3 Embedding support.

## v1.6.0

- Added end-to-end RAG evaluation, failure diagnosis, parameter experiments, and default-configuration publishing.

## v1.5.0

- Added cited knowledge-base answers with retrieval, optional reranking, evidence binding, and trace persistence.

Detailed historical notes are preserved in `docs/releases/`.
