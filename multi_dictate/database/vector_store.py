#!/usr/bin/env python3
"""Local vector storage for RAG system using ChromaDB and Sentence-Transformers"""

import logging
import os
import json
import uuid
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

class LocalVectorStore:
    """Local vector database using ChromaDB and sentence-transformers"""

    def __init__(self, storage_path: str = "~/.config/multi-dictate/vector_store"):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize embedding model
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_dim = 384
            logger.info("✅ Loaded sentence-transformers model")
        except ImportError:
            logger.error("❌ sentence-transformers not installed. Run: pip install sentence-transformers")
            raise

        # Initialize ChromaDB
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=str(self.storage_path / "chroma"))
            self.collection = self.client.get_or_create_collection(
                name="dictate_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("✅ ChromaDB initialized")
        except ImportError:
            logger.error("❌ chromadb not installed. Run: pip install chromadb")
            raise

        # Cache for embeddings
        self.embedding_cache = {}
        self.cache_file = self.storage_path / "embedding_cache.json"
        self._load_cache()

    def _load_cache(self):
        """Load embedding cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    # Convert strings back to numpy arrays
                    for text, emb in cache_data.items():
                        self.embedding_cache[text] = np.array(emb)
                logger.info(f"📦 Loaded {len(self.embedding_cache)} cached embeddings")
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")

    def _save_cache(self):
        """Save embedding cache to disk"""
        try:
            # Convert numpy arrays to lists for JSON serialization
            cache_data = {text: emb.tolist() for text, emb in self.embedding_cache.items()}
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")

    def embed_text(self, text: str) -> np.ndarray:
        """Convert text to vector embedding with caching"""
        # Check cache first
        if text in self.embedding_cache:
            return self.embedding_cache[text]

        # Generate new embedding
        try:
            embedding = self.embedder.encode(text, convert_to_numpy=True)
            self.embedding_cache[text] = embedding
            return embedding
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            # Return zero vector as fallback
            return np.zeros(self.embedding_dim)

    def add_document(self, text: str, metadata: Dict, doc_id: Optional[str] = None):
        """Add document to vector store"""
        doc_id = doc_id or str(uuid.uuid4())

        # Generate embedding
        embedding = self.embed_text(text)

        # Add to ChromaDB
        self.collection.add(
            embeddings=[embedding.tolist()],
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )

        logger.debug(f"Added document: {doc_id}")
        return doc_id

    def search(self, query: str, n_results: int = 5, filters: Optional[Dict] = None) -> List[Dict]:
        """Search for similar documents"""
        # Generate query embedding
        query_embedding = self.embed_text(query)

        # Build where clause for filters
        where_clause = None
        if filters:
            where_clause = filters

        # Search in ChromaDB
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=n_results,
                where=where_clause
            )

            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                        'id': results['ids'][0][i] if results['ids'] else None
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_by_metadata(self, filters: Dict, limit: int = 10) -> List[Dict]:
        """Get documents by metadata filters"""
        try:
            results = self.collection.get(
                where=filters,
                limit=limit
            )

            formatted_results = []
            if results['documents']:
                for i in range(len(results['documents'])):
                    formatted_results.append({
                        'text': results['documents'][i],
                        'metadata': results['metadatas'][i] if results['metadatas'] else {},
                        'id': results['ids'][i] if results['ids'] else None
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"Metadata query failed: {e}")
            return []

    def delete_document(self, doc_id: str):
        """Delete document by ID"""
        try:
            self.collection.delete(ids=[doc_id])
            logger.debug(f"Deleted document: {doc_id}")
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")

    def update_document(self, doc_id: str, text: str, metadata: Dict):
        """Update existing document"""
        self.delete_document(doc_id)
        self.add_document(text, metadata, doc_id)

    def get_stats(self) -> Dict:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'cache_size': len(self.embedding_cache),
                'storage_path': str(self.storage_path)
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'total_documents': 0, 'cache_size': 0, 'storage_path': str(self.storage_path)}

    def save_cache(self):
        """Manually save cache to disk"""
        self._save_cache()
        logger.info("💾 Saved embedding cache")

    def clear_cache(self):
        """Clear embedding cache"""
        self.embedding_cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("🗑️ Cleared embedding cache")