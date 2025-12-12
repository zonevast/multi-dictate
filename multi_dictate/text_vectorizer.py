#!/usr/bin/env python3
"""
Simple text vectorizer without external dependencies
Creates meaningful embeddings based on word overlap and patterns
"""

import re
import hashlib
import math
from typing import List, Dict, Tuple
import numpy as np

class SimpleVectorizer:
    """Create vectors without sentence-transformers"""

    def __init__(self):
        # Common words and weights
        self.common_words = {
            'fix', 'error', 'issue', 'bug', 'problem', 'solution', 'code',
            'api', 'database', 'sql', 'null', 'pointer', 'exception',
            'function', 'method', 'class', 'import', 'export',
            'mood', 'enhance', 'creative', 'idea', 'innovate',
            'walk', 'exercise', 'sunlight', 'stretch', 'meditation'
        }

        # Programming keywords
        self.programming_keywords = [
            'nullpointer', 'typoerror', 'indexerror', 'keyerror',
            'debug', 'test', 'deploy', 'production', 'development',
            'frontend', 'backend', 'database', 'api', 'rest',
            'json', 'xml', 'yaml', 'config', 'settings'
        ]

        # Mood/creativity keywords
        self.productivity_keywords = [
            'motivated', 'stuck', 'focused', 'procrastinate', 'energetic',
            'inspiration', 'brainstorm', 'ideas', 'create', 'innovate'
        ]

        self.vocabulary = list(self.common_words) + self.programming_keywords + self.productivity_keywords

    def _clean_text(self, text: str) -> List[str]:
        """Clean and tokenize text"""
        # Convert to lowercase and extract words
        text = text.lower()
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        # Split into words
        words = text.split()
        return [w for w in words if len(w) > 2]

    def _generate_simple_embedding(self, text: str) -> np.ndarray:
        """Generate 384-dimensional vector"""
        words = self._clean_text(text)
        vector = np.zeros(384, dtype=np.float32)

        # Simple frequency-based embedding
        word_freq = {}
        max_freq = 0
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
            max_freq = max(max_freq, word_freq[word])

        # Fill first part of vector with word frequencies
        for i, (word, freq) in enumerate(word_freq.items()):
            if i < 180:  # Use first 180 dimensions for vocabulary
                # Normalize frequency
                norm_freq = freq / max_freq if max_freq > 0 else 0
                # Use word hash to distribute across dimensions
                word_hash = hash(word) % 180
                vector[word_hash] = norm_freq

        # Add programming language features
        if any(word in self.programming_keywords for word in words):
            vector[180:280] = 1.0  # Programming indicator
            if 'error' in words or 'exception' in words:
                vector[280:290] = 1.0  # Error indicator
            if 'test' in words:
                vector[290:300] = 1.0  # Test indicator

        # Add mood/creativity features
        if any(word in self.productivity_keywords for word in words):
            vector[300:340] = 1.0  # Productivity indicator
            if 'mood' in words:
                vector[340:350] = 1.0  # Mood indicator
            if 'creative' in words or 'ideas' in words:
                vector[350:360] = 1.0  # Creativity indicator

        # Add semantic patterns
        if len(words) > 1:
            # Length indicator
            length_norm = min(len(words) / 20.0, 1.0)
            vector[360] = length_norm

            # Question vs statement
            if text.endswith('?'):
                vector[361] = 1.0  # Question indicator

            # Urgency indicator
            if any(word in ['urgent', 'now', 'quick', 'asap'] for word in words):
                vector[362] = 1.0

            # Complex language indicators
            if len(words) > 10:
                vector[363] = 1.0

        # Add content type indicators
        if any(file_ext in text for file_ext in ['.py', '.js', '.sql', '.json', '.yaml']):
            vector[364:374] = 1.0  # Code indicator

        # Generate remaining dimensions with small random values
        vector[375:] = np.random.random(9).astype(np.float32) * 0.1

        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector

    def vectorize(self, text: str) -> np.ndarray:
        """Convert text to vector"""
        return self._generate_simple_embedding(text)

    def compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between vectors"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def find_most_similar(self, query_text: str, candidates: List[str]) -> Tuple[str, float]:
        """Find most similar text from candidates"""
        query_vec = self.vectorize(query_text)
        best_match = candidates[0] if candidates else ""
        best_score = 0.0

        for candidate in candidates:
            candidate_vec = self.vectorize(candidate)
            similarity = self.compute_similarity(query_vec, candidate_vec)
            if similarity > best_score:
                best_match = candidate
                best_score = similarity

        return best_match, best_score