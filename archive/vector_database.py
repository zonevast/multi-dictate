#!/usr/bin/env python3
"""
FAISS Vector Database for Pattern Learning
Stores and retrieves similar patterns based on semantic similarity
"""

import faiss
import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import hashlib

class VectorDatabase:
    """FAISS-based vector database for pattern recognition"""

    def __init__(self, storage_path: str = "~/.config/multi-dictate/vectors"):
        self.storage_path = Path(os.path.expanduser(storage_path))
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # FAISS index
        self.dimension = 384  # Using sentence-transformers dimension
        self.index = faiss.IndexFlatIP(self.dimension)

        # Storage
        self.vectors_file = os.path.join(self.storage_path, "vectors.faiss")
        self.metadata_file = os.path.join(self.storage_path, "metadata.json")

        # In-memory storage
        self.metadata = []
        self.vector_count = 0

        # Learning tracking
        self.pattern_success = {}  # pattern -> success_rate
        self.user_patterns = {}    # user_id -> common patterns

        print(f"🧠 FAISS Vector Database initialized at {self.storage_path}")

        # Load existing data
        self.load_data()

    def load_data(self):
        """Load existing vectors and metadata"""
        try:
            # Load vectors
            if os.path.exists(self.vectors_file):
                self.index = faiss.read_index(self.vectors_file)
                print(f"📚 Loaded {self.index.ntotal} vectors from disk")

            # Load metadata
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                    self.vector_count = len(self.metadata)
                print(f"📝 Loaded {self.vector_count} metadata entries")

        except Exception as e:
            print(f"⚠️ Could not load data: {e}")

    def save_data(self):
        """Save vectors and metadata to disk"""
        try:
            # Save vectors
            if self.vector_count > 0:
                faiss.write_index(self.index, self.vectors_file)
                print(f"💾 Saved {self.vector_count} vectors to disk")

            # Save metadata
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
                print(f"💾 Saved metadata to disk")

        except Exception as e:
            print(f"⚠️ Could not save data: {e}")

    def add_entry(self, text: str, vector: np.ndarray, metadata: Dict):
        """Add new entry to vector database"""
        # Store in FAISS
        index_id = self.index.ntotal
        self.index.add(vector.reshape(1, -1))

        # Store metadata
        metadata['id'] = index_id
        metadata['text'] = text
        metadata['timestamp'] = datetime.now().isoformat()
        metadata['vector'] = vector.tolist()
        metadata['hash'] = hashlib.md5(text.encode()).hexdigest()

        self.metadata.append(metadata)
        self.vector_count += 1

    def find_similar(self, query_vector: np.ndarray, k: int = 5, min_similarity: float = 0.7) -> List[Dict]:
        """Find similar entries based on vector similarity"""
        if self.vector_count == 0:
            return []

        # Search in FAISS (using inner product, higher is better)
        distances, indices = self.index.search(query_vector.reshape(1, -1), min(k, self.vector_count))

        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx >= 0 and idx < len(self.metadata):
                # For IndexFlatIP, distance is the dot product (similarity)
                similarity = float(dist)

                if similarity >= min_similarity:
                    result = self.metadata[idx].copy()
                    result['similarity'] = similarity
                    results.append(result)

        return results

    def update_success(self, pattern_id: str, success: bool):
        """Update success rate for a pattern"""
        if pattern_id not in self.pattern_success:
            self.pattern_success[pattern_id] = {
                'total': 0,
                'success': 0,
                'rate': 0.0
            }

        self.pattern_success[pattern_id]['total'] += 1
        if success:
            self.pattern_success[pattern_id]['success'] += 1

        # Calculate rate
        total = self.pattern_success[pattern_id]['total']
        success_count = self.pattern_success[pattern_id]['success']
        self.pattern_success[pattern_id]['rate'] = success_count / total if total > 0 else 0.0

        print(f"📊 Pattern {pattern_id}: {success_count}/{total} = {self.pattern_success[pattern_id]['rate']:.1%}")

    def get_pattern_stats(self) -> Dict:
        """Get statistics about pattern learning"""
        return {
            'total_patterns': len(self.pattern_success),
            'total_vectors': self.vector_count,
            'success_rates': self.pattern_success,
            'top_patterns': sorted(
                [(k, v['rate']) for k, v in self.pattern_success.items()],
                key=lambda x: x[1], reverse=True
            )[:5]
        }

    def clear_old_entries(self, days_old: int = 30):
        """Clear entries older than specified days"""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)

        new_metadata = []
        removed_count = 0

        for entry in self.metadata:
            timestamp = datetime.fromisoformat(entry['timestamp']).timestamp()
            if timestamp >= cutoff_date:
                new_metadata.append(entry)
            else:
                removed_count += 1

        self.metadata = new_metadata

        # Rebuild index
        if self.metadata:
            vectors = np.array([np.array(entry['vector']) for entry in self.metadata])
            self.index = faiss.IndexFlatIP(self.dimension)
            self.index.add(vectors)
            self.vector_count = len(self.metadata)
            faiss.write_index(self.index, self.vectors_file)
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.vector_count = 0

        print(f"🗑️ Cleared {removed_count} old entries")

        # Save updated data
        self.save_data()