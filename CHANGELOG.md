# Changelog

## v1.23.0

- Added three question-answering modes: normal RAG, industry intelligence analysis and automatic routing;
- added intent-based retrieval across raw chunks, claims, claim clusters, canonical events, statistics, creator profiles and learning resources;
- added cross-layer candidate fusion, evidence-layer labels, evidence gating and persistent query traces;
- split the knowledge-base service into core, indexing, retrieval, answering and evaluation modules;
- added frontend modular contract checks and dedicated intelligence query tests.

## v1.22.x

- Added database-backed manual background jobs for indexing, intelligence synchronization, clustering, event deduplication, statistics, reports, profiles, quality and performance tasks;
- added persistent progress events, resource locks, idempotent request reuse, cooperative cancellation, retry and restart recovery;
- added large-data performance tests and supporting database indexes.

## v1.21.0

- Added a dedicated data quality and performance center;
- persisted quality issues with pending, ignored and resolved states;
- added PostgreSQL/SQLite storage diagnostics and representative query benchmarks;
- added persistent statistics cache with source-signature invalidation;
- added safe manual cleanup for expired media, logs and statistics cache.

## v1.20.0

- Added creator profiles, content style scores, publishing rhythm, topic concentration and viewpoint evolution timelines.

## v1.19.0

- Added deterministic daily, weekly and topic reports with source-numbered evidence snapshots and Word export.

## v1.18.0

- Added canonical event deduplication, watchlists and explainable intelligence alerts.

## v1.17.x

- Added claim clustering, consensus/disagreement analysis, threshold scanning, pair labeling and clustering evaluation.

## v1.14.x

- Added formal intelligence materialization for entities, claims, events, learning items and resources.

## v1.11.x

- Added PostgreSQL 17, pgvector, Alembic migrations, Docker bootstrap, SQLite migration and vector backend abstraction.

## v1.9.x

- Added parent-child chunking, multi-model embedding profiles, retrieval routing, dynamic evidence compression, caching and RAG regression baselines.

## v1.7.x

- Added Ollama local Qwen chat/embedding support and portable Windows deployment.

## v1.5–v1.6

- Added cited knowledge-base question answering, end-to-end RAG evaluation, failure diagnosis and configuration comparison.

Earlier implementation history is available in [docs/releases/DEVELOPMENT_HISTORY.md](docs/releases/DEVELOPMENT_HISTORY.md).
