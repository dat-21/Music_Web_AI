from __future__ import annotations

import json
import os
import time

import faiss

from src.core.config import settings
from src.vector_store.faiss_store import FAISSStore


class FAISSPersistence:
    def __init__(self, path: str | None = None) -> None:
        self.path = path or settings.faiss_index_path

    def _rotate_backups(self, keep: int = 5) -> None:
        directory = os.path.dirname(self.path) or "."
        basename = os.path.basename(self.path)
        prefix = basename + "."
        metadata_prefix = f"{basename}.metadata.json."
        backups = [
            os.path.join(directory, name)
            for name in os.listdir(directory)
            if name.startswith(prefix)
            and name.endswith(".bak")
            and not name.startswith(metadata_prefix)
        ]
        backups.sort(key=os.path.getmtime, reverse=True)
        for old in backups[keep:]:
            timestamp = os.path.basename(old)[len(prefix) : -len(".bak")]
            metadata_backup = os.path.join(directory, f"{basename}.metadata.json.{timestamp}.bak")
            if os.path.exists(old):
                os.remove(old)
            if os.path.exists(metadata_backup):
                os.remove(metadata_backup)

    async def save(self, store: FAISSStore) -> str:
        if store.index is None:
            return self.path

        directory = os.path.dirname(self.path) or "."
        os.makedirs(directory, exist_ok=True)

        metadata_path = self.path + ".metadata.json"
        timestamp = str(time.time_ns())
        backup_index = f"{self.path}.{timestamp}.bak"
        backup_metadata = f"{metadata_path}.{timestamp}.bak"

        tmp_index = self.path + ".tmp"
        tmp_metadata = metadata_path + ".tmp"

        faiss.write_index(store.index, tmp_index)
        with open(tmp_metadata, "w", encoding="utf-8") as handle:
            json.dump(store.metadata, handle)

        if os.path.exists(self.path):
            os.replace(self.path, backup_index)
        if os.path.exists(metadata_path):
            os.replace(metadata_path, backup_metadata)

        os.replace(tmp_index, self.path)
        os.replace(tmp_metadata, metadata_path)

        self._rotate_backups()
        return self.path

    async def load(self) -> FAISSStore:
        store = FAISSStore()
        if not os.path.exists(self.path):
            return store

        try:
            store.index = faiss.read_index(self.path)
            if store.index is not None:
                store.dimension = int(store.index.d)
                if hasattr(store.index, "nlist"):
                    store.nlist = int(store.index.nlist)
                if hasattr(store.index, "nprobe"):
                    store.nprobe = int(store.index.nprobe)
            metadata_path = self.path + ".metadata.json"
            if os.path.exists(metadata_path):
                with open(metadata_path, encoding="utf-8") as handle:
                    store.metadata = json.load(handle)
            if store.index is not None and len(store.metadata) != store.index.ntotal:
                store.metadata = []
        except Exception:
            store.index = None
            store.metadata = []
        return store


_persistence = FAISSPersistence()


def get_persistence() -> FAISSPersistence:
    return _persistence
