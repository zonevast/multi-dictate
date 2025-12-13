#!/usr/bin/env python3
"""Knowledge base management for RAG system"""

import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from .vector_store import LocalVectorStore

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Manages knowledge ingestion and retrieval for RAG"""

    def __init__(self, storage_path: str = "~/.config/multi-dictate"):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize vector store
        self.vector_store = LocalVectorStore(str(self.storage_path / "vector_store"))

        # Knowledge categories
        self.categories = {
            'mood_enhancers': {
                'description': 'Activities and techniques for mood improvement',
                'examples': [
                    'Meditation and breathing exercises help regulate emotions',
                    'Physical exercise releases endorphins and improves mood',
                    'Creative activities like art or music provide emotional expression',
                    'Social connection and community activities boost wellbeing'
                ]
            },
            'creativity_boosters': {
                'description': 'Methods to spark creativity and new ideas',
                'examples': [
                    'Changing environment stimulates fresh perspectives',
                    'Mind mapping visualizes connections between ideas',
                    'Limitations force creative problem-solving',
                    'Cross-disciplinary learning inspires innovation'
                ]
            },
            'self_sufficiency': {
                'description': 'Strategies for internal mood regulation',
                'examples': [
                    'Journaling externalizes and processes emotions',
                    'Gratitude practice shifts focus to positive aspects',
                    'Self-reflection builds emotional awareness',
                    'Habit stacking creates consistent positive routines'
                ]
            },
            'productivity_techniques': {
                'description': 'Methods to maintain productivity regardless of mood',
                'examples': [
                    'Pomodoro technique maintains focus with breaks',
                    'Task batching reduces context switching',
                    'Energy matching aligns tasks with current state',
                    'Micro-habits build momentum with small wins'
                ]
            },
            'environmental_independence': {
                'description': 'Creating internal stability despite external factors',
                'examples': [
                    'Morning routines establish daily foundation',
                    'Personal rituals create predictability',
                    'Internal validation reduces external dependency',
                    'Flexible thinking adapts to circumstances'
                ]
            }
        }

        # Initialize with base knowledge
        self._initialize_base_knowledge()

        # Track learning
        self.learning_log = []
        self.learning_file = self.storage_path / "learning_log.json"

    def _initialize_base_knowledge(self):
        """Initialize knowledge base with mood and creativity enhancement content"""
        logger.info("🧠 Initializing knowledge base with mood enhancement content")

        base_knowledge = {
            'mood_patterns': [
                {
                    'text': 'Morning sunlight exposure regulates circadian rhythm and improves mood',
                    'metadata': {
                        'category': 'mood_enhancers',
                        'type': 'technique',
                        'time_sensitive': 'morning',
                        'effectiveness': 0.9
                    }
                },
                {
                    'text': 'Deep breathing exercises activate parasympathetic nervous system, reducing stress',
                    'metadata': {
                        'category': 'mood_enhancers',
                        'type': 'technique',
                        'time_sensitive': 'anytime',
                        'effectiveness': 0.85
                    }
                },
                {
                    'text': 'Physical movement, even brief walks, increases dopamine and serotonin',
                    'metadata': {
                        'category': 'mood_enhancers',
                        'type': 'technique',
                        'time_sensitive': 'anytime',
                        'effectiveness': 0.8
                    }
                },
                {
                    'text': 'Creative constraints enhance innovation by forcing alternative thinking',
                    'metadata': {
                        'category': 'creativity_boosters',
                        'type': 'principle',
                        'applicable': 'creative_blocks',
                        'effectiveness': 0.85
                    }
                },
                {
                    'text': 'Changing physical environment stimulates neuroplasticity and new perspectives',
                    'metadata': {
                        'category': 'creativity_boosters',
                        'type': 'technique',
                        'applicable': 'stuck_thinking',
                        'effectiveness': 0.8
                    }
                },
                {
                    'text': 'Internal validation through self-reflection builds emotional independence',
                    'metadata': {
                        'category': 'self_sufficiency',
                        'type': 'practice',
                        'applicable': 'emotional_regulation',
                        'effectiveness': 0.9
                    }
                },
                {
                    'text': 'Habit stacking anchors new behaviors to existing routines',
                    'metadata': {
                        'category': 'productivity_techniques',
                        'type': 'method',
                        'applicable': 'habit_formation',
                        'effectiveness': 0.85
                    }
                }
            ]
        }

        # Add to vector store
        for item in base_knowledge['mood_patterns']:
            self.add_knowledge(item['text'], item['metadata'])

        logger.info(f"✅ Initialized with {len(base_knowledge['mood_patterns'])} knowledge items")

    def add_knowledge(self, text: str, metadata: Dict, source: str = "user") -> str:
        """Add new knowledge to the base"""
        metadata.update({
            'source': source,
            'added_at': datetime.now().isoformat(),
            'user_feedback': None
        })

        doc_id = self.vector_store.add_document(text, metadata)

        # Log for learning
        self.learning_log.append({
            'action': 'added',
            'doc_id': doc_id,
            'text': text[:100] + "..." if len(text) > 100 else text,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        })

        logger.info(f"➕ Added knowledge: {text[:50]}...")
        return doc_id

    def search_knowledge(self, query: str, context: Optional[Dict] = None, n_results: int = 5) -> List[Dict]:
        """Search knowledge base with context"""
        # Add time-based filtering if context provided
        filters = {}
        if context:
            if 'current_time' in context:
                current_time = context['current_time'].lower()
                if 'morning' in current_time:
                    filters['time_sensitive'] = 'morning'
                elif 'evening' in current_time:
                    filters['time_sensitive'] = 'evening'

        results = self.vector_store.search(query, n_results=n_results, filters=filters)

        # Add relevance scoring
        for result in results:
            # Boost based on effectiveness
            effectiveness = result['metadata'].get('effectiveness', 0.5)
            result['relevance_score'] = (1 - result['distance']) * effectiveness

        # Sort by relevance
        results.sort(key=lambda x: x['relevance_score'], reverse=True)

        return results

    def get_mood_suggestions(self, current_state: str, constraints: List[str] = None) -> List[Dict]:
        """Get personalized mood enhancement suggestions"""
        query = f"mood enhancement improvement {current_state}"

        context = {
            'current_time': datetime.now().strftime("%H:%M"),
            'constraints': constraints or []
        }

        results = self.search_knowledge(query, context, n_results=5)
        return results

    def get_creativity_boosters(self, current_block: str, available_resources: List[str] = None) -> List[Dict]:
        """Get creativity enhancement techniques"""
        query = f"creativity new ideas innovation {current_block}"

        results = self.search_knowledge(query, n_results=5)

        # Filter by available resources if provided
        if available_resources:
            results = [
                r for r in results
                if not any(req in r['text'].lower() for req in available_resources)
            ]

        return results

    def learn_from_interaction(self, user_input: str, context: str, ai_response: str, feedback: int = None):
        """Learn from successful interactions"""
        # Create learning entry
        learning_text = f"Context: {context}\nUser: {user_input}\nSolution: {ai_response}"

        metadata = {
            'category': 'learned_pattern',
            'type': 'successful_interaction',
            'context_pattern': self._extract_pattern(context),
            'feedback_score': feedback,
            'usefulness': 0.8 if feedback and feedback > 0 else 0.5
        }

        self.add_knowledge(learning_text, metadata, source="learning")

        # Update existing knowledge based on feedback
        if feedback is not None:
            self._update_knowledge_feedback(user_input, context, feedback)

    def _extract_pattern(self, context: str) -> str:
        """Extract common pattern from context"""
        # Simple pattern extraction - can be enhanced with NLP
        patterns = {
            'feeling_stuck': ['stuck', 'blocked', 'cant think'],
            'low_energy': ['tired', 'low energy', 'fatigue'],
            'anxious': ['anxious', 'worried', 'stress'],
            'unmotivated': ['unmotivated', 'procrastinate', 'no drive']
        }

        context_lower = context.lower()
        for pattern, keywords in patterns.items():
            if any(kw in context_lower for kw in keywords):
                return pattern

        return 'general'

    def _update_knowledge_feedback(self, user_input: str, context: str, feedback: int):
        """Update knowledge effectiveness based on feedback"""
        # Search for similar entries
        similar = self.vector_store.search(user_input, n_results=3)

        for item in similar:
            current_feedback = item['metadata'].get('feedback_scores', [])
            current_feedback.append(feedback)

            # Update metadata
            new_metadata = item['metadata'].copy()
            new_metadata['feedback_scores'] = current_feedback[-5:]  # Keep last 5
            new_metadata['avg_feedback'] = sum(current_feedback) / len(current_feedback)
            new_metadata['effectiveness'] = min(1.0, new_metadata['avg_feedback'] / 5.0)

            self.vector_store.update_document(item['id'], item['text'], new_metadata)

    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        stats = self.vector_store.get_stats()
        stats['learning_entries'] = len(self.learning_log)
        stats['categories'] = list(self.categories.keys())
        return stats

    def save_learning(self):
        """Save learning log to disk"""
        try:
            with open(self.learning_file, 'w') as f:
                json.dump(self.learning_log, f, indent=2)
            logger.info("💾 Saved learning log")
        except Exception as e:
            logger.error(f"Failed to save learning log: {e}")

    def export_knowledge(self, category: str = None) -> List[Dict]:
        """Export knowledge for review"""
        if category:
            filters = {'category': category}
        else:
            filters = {}

        return self.vector_store.get_by_metadata(filters, limit=100)