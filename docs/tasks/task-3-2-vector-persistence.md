# Task 3.2 - Vector Store Persistence

## Status

Implemented.

## Goal

Provide production-grade persistence for the FAISS index with startup load, shutdown save, and backup rotation.

## Architecture Overview

- Persistence module: [src/vector_store/persistence.py](src/vector_store/persistence.py)
- Lifespan integration: [src/main.py](src/main.py)
- Configuration: [src/core/config.py](src/core/config.py)
- Backup rotation script: [scripts/rotate_faiss_backups.sh](scripts/rotate_faiss_backups.sh)

## Startup/Shutdown Flow

Startup:
- Load FAISS index from disk via FAISSPersistence.load().
- Replace the global vector store instance.
- Store in app.state.vector_store for service access.

Shutdown:
- Save index and metadata via FAISSPersistence.save().
- Create timestamped backups and rotate old snapshots.

## Persistence Behavior

- Index written to /data/faiss.index (configurable via settings).
- Metadata stored alongside as /data/faiss.index.metadata.
- Writes use temp files + atomic replace.
- If metadata is corrupted or mismatched, it is reset to empty.

## Backup Rotation

- Keep last 5 snapshots.
- Snapshot names: faiss.index.<timestamp>.bak and faiss.index.metadata.<timestamp>.bak.
- Script for manual rotation: [scripts/rotate_faiss_backups.sh](scripts/rotate_faiss_backups.sh).

## Tests

- Persistence round-trip: [tests/test_vector_store_persistence.py](tests/test_vector_store_persistence.py)
- Backup rotation: [tests/test_vector_store_persistence.py](tests/test_vector_store_persistence.py)

## Notes

- Load path configured by settings.faiss_index_path.
- Lifespan integration keeps the index in sync with process lifecycle.
