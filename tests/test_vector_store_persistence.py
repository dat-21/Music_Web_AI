from __future__ import annotations

import asyncio
import os

from src.vector_store.faiss_store import FAISSStore
from src.vector_store.persistence import FAISSPersistence
from src.vector_store.types import VectorRecord


def build_vector(index: int, size: int) -> list[float]:
    values = [0.0] * size
    values[index] = 1.0
    return values


def run(coro):
    return asyncio.run(coro)


def test_persistence_round_trip(tmp_path) -> None:
    path = os.path.join(tmp_path, "faiss.index")
    persistence = FAISSPersistence(path=path)

    store = FAISSStore(dimension=8, nlist=1, pq_m=2)
    records = [
        VectorRecord(song_id="song-a", embedding=build_vector(0, 8), metadata={"x": "1"}),
        VectorRecord(song_id="song-b", embedding=build_vector(1, 8), metadata={"x": "2"}),
    ]
    run(store.add_vectors(records))

    run(persistence.save(store))
    loaded = run(persistence.load())

    assert loaded.index is not None
    assert loaded.index.ntotal == store.index.ntotal
    assert len(loaded.metadata) == len(store.metadata)


def test_backup_rotation(tmp_path) -> None:
    path = os.path.join(tmp_path, "faiss.index")
    persistence = FAISSPersistence(path=path)
    store = FAISSStore(dimension=8, nlist=1, pq_m=2)
    records = [
        VectorRecord(song_id="song-a", embedding=build_vector(0, 8), metadata={}),
    ]
    run(store.add_vectors(records))

    for _ in range(7):
        run(persistence.save(store))

    backups = [
        name
        for name in os.listdir(tmp_path)
        if name.startswith("faiss.index.") and name.endswith(".bak") and ".metadata." not in name
    ]
    assert len(backups) <= 5
