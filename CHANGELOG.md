# Changelog

All notable changes to this project are documented here.

## 0.2.6

### Added

- structured error codes and user-facing recovery guidance;
- collection run events and trace IDs;
- rotating JSON Lines application logs;
- diagnostic ZIP export;
- new / updated / unchanged content detection;
- automatic SQLite schema compatibility upgrade.

### Changed

- improved failure classification for links, networking, login state, risk control, browsers, databases, permissions, and disk errors;
- interaction metrics no longer trigger semantic content reprocessing.

## 0.2.5

- separated long-form articles from ordinary image galleries;
- added article filtering, statistics, canonical links, and export labels.

## 0.2.4

- introduced API-first fast collection;
- removed per-work detail-page opening;
- retained a single-profile-page browser fallback.

## 0.2.3

- corrected false-positive DOM work links;
- added creator ownership validation and public work-count handling.

## 0.2.2

- merged setup and startup into `CareerAgent_Start.bat`;
- added dependency hash checking and automatic Chromium installation.

## 0.2.0

- added the local Web management interface;
- added creator cards, result tables, search, copy, CSV and JSON export.
