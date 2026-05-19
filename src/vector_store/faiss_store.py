from __future__ import annotations

from collections.abc import Iterable

import faiss
import numpy as np

from src.vector_store.types import SearchResult, VectorRecord, VectorStoreHealth


class FAISSStore:
    def __init__(
        self,
        dimension: int = 384,
        nlist: int = 100,
        pq_m: int = 64,
        pq_bits: int = 8,
        hnsw_m: int = 32,
        nprobe: int = 8,
    ) -> None:
        self.dimension = dimension
        self.nlist = nlist
        self.pq_m = pq_m
        self.pq_bits = pq_bits
        self.hnsw_m = hnsw_m
        self.nprobe = nprobe
        self.index: faiss.IndexIVFPQ | None = None
        self.metadata: list[dict[str, str]] = []

    def build_index(self) -> None:
        quantizer = faiss.IndexHNSWFlat(self.dimension, self.hnsw_m, faiss.METRIC_INNER_PRODUCT)
        index = faiss.IndexIVFPQ(
            quantizer,
            self.dimension,
            self.nlist,
            self.pq_m,
            self.pq_bits,
            faiss.METRIC_INNER_PRODUCT,
        )
        training_size = max(1000, self.nlist * 10)
        training_data = np.random.random((training_size, self.dimension)).astype("float32")
        faiss.normalize_L2(training_data)
        index.train(training_data)
        index.nprobe = min(self.nprobe, self.nlist)
        self.index = index

    def _ensure_index(self) -> faiss.IndexIVFPQ:
        if self.index is None:
            self.build_index()
        return self.index

    def _normalize(self, embeddings: np.ndarray) -> np.ndarray:
        if embeddings.ndim != 2 or embeddings.shape[1] != self.dimension:
            raise ValueError("Embedding dimension mismatch")
        embeddings = embeddings.astype("float32")
        faiss.normalize_L2(embeddings)
        return embeddings

    async def add_vectors(self, records: list[VectorRecord]) -> int:
        if not records:
            return 0

        embeddings = np.array([record.embedding for record in records], dtype=np.float32)
        embeddings = self._normalize(embeddings)

        index = self._ensure_index()
        if not index.is_trained:
            index.train(embeddings)
        index.add(embeddings)

        self.metadata.extend(
            [
                {
                    "song_id": record.song_id,
                    "metadata": record.metadata,
                }
                for record in records
            ]
        )
        return len(records)

    async def search(
        self,
        query_embedding: Iterable[float],
        limit: int = 10,
        threshold: float = 0.7,
    ) -> list[SearchResult]:
        if self.index is None or self.index.ntotal == 0:
            return []

        query = np.array([list(query_embedding)], dtype=np.float32)
        query = self._normalize(query)

        distances, indices = self.index.search(query, limit)
        results: list[SearchResult] = []
        for pos, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            score = float(distances[0][pos])
            if score < threshold:
                continue
            record = self.metadata[idx]
            results.append(
                SearchResult(
                    song_id=record["song_id"],
                    score=score,
                    metadata=record.get("metadata", {}),
                )
            )
        return results

    def health(self) -> VectorStoreHealth:
        if self.index is None:
            return VectorStoreHealth(ready=False, trained=False, total_vectors=0)
        return VectorStoreHealth(
            ready=bool(self.index.ntotal > 0),
            trained=bool(self.index.is_trained),
            total_vectors=int(self.index.ntotal),
        )


_vector_store = FAISSStore()


def get_vector_store() -> FAISSStore:
    return _vector_store


def set_vector_store(store: FAISSStore) -> None:
    global _vector_store
    _vector_store = store
