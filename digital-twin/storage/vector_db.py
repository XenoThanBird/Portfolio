"""
ChromaDB-based vector store with encryption integration.
Supports sensitivity-aware storage: sensitive content is encrypted at rest
while embeddings remain searchable.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions

from .encryptor import DataClassifier, DataSensitivity, Encryptor


class VectorStore:
    """
    Vector store using ChromaDB for semantic search and retrieval.
    Integrates with the encryption layer for sensitive data.
    """

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = "default",
        embedding_model: str = "all-MiniLM-L6-v2",
        encryption_key: Optional[str] = None,
        encrypt_sensitive: bool = True,
    ):
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
            embedding_model: SentenceTransformer model name
            encryption_key: Fernet key for encrypting sensitive content
            encrypt_sensitive: Whether to encrypt HIGH/MEDIUM sensitivity data
        """
        self.encrypt_sensitive = encrypt_sensitive
        self.encryptor = Encryptor(encryption_key) if encryption_key else None

        if persist_directory is None:
            persist_directory = "./data/vector_db"

        persist_path = Path(persist_directory)
        persist_path.mkdir(parents=True, exist_ok=True)

        chroma_settings = ChromaSettings(
            persist_directory=str(persist_path),
            anonymized_telemetry=False,
        )
        self.client = chromadb.Client(chroma_settings)

        self.embedding_function = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model
            )
        )

        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"created_at": datetime.now().isoformat()},
        )

    def add(
        self,
        documents: Union[str, List[str]],
        metadatas: Optional[Union[Dict, List[Dict]]] = None,
        ids: Optional[Union[str, List[str]]] = None,
        classify_sensitivity: bool = True,
    ) -> List[str]:
        """
        Add documents to the vector store.

        Sensitive documents are still embedded for search but their
        plaintext content is encrypted and stored separately.

        Args:
            documents: Document text(s) to add
            metadatas: Optional metadata for each document
            ids: Optional IDs (auto-generated if omitted)
            classify_sensitivity: Whether to classify and handle sensitive data

        Returns:
            List of document IDs
        """
        if isinstance(documents, str):
            documents = [documents]
        if metadatas is None:
            metadatas = [{}] * len(documents)
        elif isinstance(metadatas, dict):
            metadatas = [metadatas]
        if ids is None:
            ids = [self._generate_id(doc) for doc in documents]
        elif isinstance(ids, str):
            ids = [ids]

        processed_docs = []
        processed_metas = []

        for doc, meta, doc_id in zip(documents, metadatas, ids):
            if classify_sensitivity:
                sensitivity = DataClassifier.classify(
                    data={"text": doc, **meta},
                    data_type=meta.get("data_type"),
                    source=meta.get("source"),
                )
            else:
                sensitivity = DataSensitivity.LOW

            meta = {**meta, "sensitivity": sensitivity.value}

            if (
                self.encryptor
                and self.encrypt_sensitive
                and DataClassifier.should_encrypt(sensitivity)
            ):
                encrypted_content = self.encryptor.encrypt(doc)
                meta["encrypted"] = True
                meta["content_hash"] = self.encryptor.hash_data(doc)
                meta["encrypted_location"] = self._store_encrypted(
                    encrypted_content, doc_id
                )
            else:
                meta["encrypted"] = False

            if "timestamp" not in meta:
                meta["timestamp"] = datetime.now().isoformat()

            processed_docs.append(doc)
            processed_metas.append(meta)

        self.collection.add(
            documents=processed_docs,
            metadatas=processed_metas,
            ids=ids,
        )
        return ids

    def query(
        self,
        query_texts: Union[str, List[str]],
        n_results: int = 10,
        where: Optional[Dict] = None,
        include_encrypted: bool = True,
    ) -> Dict[str, Any]:
        """
        Query the vector store by semantic similarity.

        Args:
            query_texts: Query text(s)
            n_results: Number of results to return
            where: Metadata filter
            include_encrypted: Whether to decrypt encrypted results

        Returns:
            Query results with documents, metadatas, and distances
        """
        if isinstance(query_texts, str):
            query_texts = [query_texts]

        results = self.collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where,
        )

        if include_encrypted and self.encryptor:
            results = self._decrypt_results(results)

        return results

    def get(
        self,
        ids: Optional[Union[str, List[str]]] = None,
        where: Optional[Dict] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get documents by ID or metadata filter."""
        if isinstance(ids, str):
            ids = [ids]
        return self.collection.get(ids=ids, where=where, limit=limit)

    def delete(self, ids: Optional[Union[str, List[str]]] = None, where: Optional[Dict] = None):
        """Delete documents by ID or metadata filter."""
        if isinstance(ids, str):
            ids = [ids]
        self.collection.delete(ids=ids, where=where)

    def count(self) -> int:
        """Get total number of documents in the collection."""
        return self.collection.count()

    def reset(self):
        """Delete all documents from the collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
        )

    # --- internal helpers ---

    def _generate_id(self, document: str) -> str:
        content_hash = hashlib.sha256(document.encode()).hexdigest()
        return f"{content_hash[:16]}_{datetime.now().isoformat()}"

    def _store_encrypted(self, encrypted_content: bytes, doc_id: str) -> str:
        storage_path = Path("./data/encrypted")
        storage_path.mkdir(parents=True, exist_ok=True)
        file_path = storage_path / f"{doc_id}.encrypted"
        with open(file_path, "wb") as f:
            f.write(encrypted_content)
        return str(file_path)

    def _load_encrypted(self, path: str) -> str:
        with open(path, "rb") as f:
            return self.encryptor.decrypt(f.read())

    def _decrypt_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        if "metadatas" not in results:
            return results

        metadatas_list = results.get("metadatas", [])
        documents_list = results.get("documents", [])

        if not metadatas_list or not isinstance(metadatas_list[0], list):
            metadatas_list = [metadatas_list]
            documents_list = [documents_list]
            single = True
        else:
            single = False

        decrypted_all = []
        for metadatas, documents in zip(metadatas_list, documents_list):
            decrypted = []
            for i, meta in enumerate(metadatas):
                if meta.get("encrypted") and "encrypted_location" in meta:
                    try:
                        decrypted.append(self._load_encrypted(meta["encrypted_location"]))
                    except Exception as e:
                        decrypted.append(f"[Decryption failed: {e}]")
                else:
                    decrypted.append(documents[i])
            decrypted_all.append(decrypted)

        results["documents"] = decrypted_all[0] if single else decrypted_all
        return results
