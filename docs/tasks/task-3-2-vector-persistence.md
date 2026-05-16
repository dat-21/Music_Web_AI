# Task 3.2 - Vector Store Persistence

## Status

Planned (not implemented in codebase yet).

## Goal

Provide production-grade persistence for the FAISS index with startup load, shutdown save, and backup rotation.

## Planned Behavior

- Startup:
  - Load FAISS index from disk
  - Validate index health
  - Mark service ready
- Shutdown:
  - Save index to disk
  - Persist metadata

## Backup Rotation

- Keep last 5 snapshots
- Remove older snapshots on each save cycle

## Test Plan

- Restart preserves index and metadata
- Load 1M vectors < 30 seconds
- Corruption detection and safe fallback

## Notes

- Persistence layer should be async-friendly and robust to partial writes.
- Add checksum or metadata validation to detect corruption.
