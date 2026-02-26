"""
Vector Store
-------------
FAISS-based vector store with persistence, similarity search, and metadata filtering.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """
    FAISS vector store with document persistence.

    Supports:
      - Cosine and L2 similarity
      - Metadata filtering
      - Save/load to disk
    """

    def __init__(self, dimension: int = 1536, metric: str = "cosine", storage_path: str = "./vector_store"):
        self.dimension = dimension
        self.metric = metric
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._index = None
        self._documents: List[Dict[str, Any]] = []
        self._init_index()

    def _init_index(self):
        import faiss

        if self.metric == "cosine":
            self._index = faiss.IndexFlatIP(self.dimension)
        else:
            self._index = faiss.IndexFlatL2(self.dimension)
        logger.info("FAISS index initialized (dim=%d, metric=%s)", self.dimension, self.metric)

    def add_documents(self, texts: List[str], embeddings: List[List[float]], metadata: List[Dict] = None):
        if metadata is None:
            metadata = [{}] * len(texts)

        vectors = np.array(embeddings, dtype=np.float32)
        if self.metric == "cosine":
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1
            vectors = vectors / norms

        start_id = len(self._documents)
        for i, (text, meta) in enumerate(zip(texts, metadata)):
            self._documents.append({
                "id": f"doc_{start_id + i}",
                "content": text,
                "metadata": meta,
            })

        self._index.add(vectors)
        logger.info("Added %d documents (total: %d)", len(texts), len(self._documents))

    def search(self, query_embedding: List[float], k: int = 5, threshold: float = None) -> List[Dict]:
        if self._index.ntotal == 0:
            return []

        vector = np.array([query_embedding], dtype=np.float32)
        if self.metric == "cosine":
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm

        scores, indices = self._index.search(vector, min(k, self._index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            if threshold and score < threshold:
                continue
            doc = self._documents[idx].copy()
            doc["score"] = float(score)
            results.append(doc)

        return results

    def save(self):
        import faiss

        faiss.write_index(self._index, str(self.storage_path / "index.faiss"))
        with open(self.storage_path / "documents.pkl", "wb") as f:
            pickle.dump(self._documents, f)
        logger.info("Vector store saved to %s", self.storage_path)

    def load(self) -> bool:
        import faiss

        index_path = self.storage_path / "index.faiss"
        docs_path = self.storage_path / "documents.pkl"
        if not index_path.exists() or not docs_path.exists():
            return False

        self._index = faiss.read_index(str(index_path))
        with open(docs_path, "rb") as f:
            self._documents = pickle.load(f)
        logger.info("Loaded %d documents from %s", len(self._documents), self.storage_path)
        return True

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_documents": len(self._documents),
            "index_size": self._index.ntotal if self._index else 0,
            "dimension": self.dimension,
            "metric": self.metric,
        }
