# CareerAgent Collector

CareerAgent Collector is the ingestion foundation of the CareerAgent project. It collects publicly accessible creator and content metadata from a Douyin profile, normalizes the data into a stable model, stores it idempotently, detects content changes, and records a complete diagnostic trace.

Current capabilities include:

- profile URL and share-link resolution;
- creator metadata collection;
- paginated collection of the latest N public works;
- separate classification for video, gallery, and long-form article content;
- API-first collection with a browser fallback;
- idempotent storage using `platform + platform_content_id`;
- new / updated / unchanged detection;
- structured error codes, run events, trace IDs, and diagnostic exports;
- local Web UI, FastAPI endpoints, and CLI support.

See the primary [Chinese README](README.md) for setup, architecture, limitations, and roadmap.

This project is licensed under the Apache License 2.0. Third-party attributions are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
