#!/usr/bin/env python3
"""
Chroma Vector Database for Pattern Learning
Production-ready RAG solution with metadata filtering and persistence
"""

import chromadb
import numpy as np
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

class ChromaVectorDB:
    """Chroma-based vector database for pattern recognition and RAG"""

    def __init__(self, storage_path: str = "~/.config/multi-dictate/chroma"):
        self.storage_path = Path(os.path.expanduser(storage_path))
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize Chroma client
        self.client = chromadb.PersistentClient(path=str(self.storage_path))

        # Collections for different types of data
        self.patterns_collection = self.client.get_or_create_collection(
            name="user_patterns",
            metadata={"description": "User interaction patterns for learning"}
        )

        self.knowledge_collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"description": "General knowledge for RAG enhancement"}
        )

        # Learning tracking
        self.pattern_success = {}  # pattern_id -> success_metrics

        print(f"🔥 Chroma Vector Database initialized at {self.storage_path}")
        print(f"📚 Pattern collection: {self.patterns_collection.count()} items")
        print(f"🧠 Knowledge collection: {self.knowledge_collection.count()} items")

    def add_pattern(self,
                   text: str,
                   solution: str,
                   category: str = "general",
                   metadata: Dict = None) -> str:
        """Add a new pattern to the database"""

        # Create unique ID
        pattern_id = f"pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(text) % 10000}"

        # Prepare metadata
        full_metadata = {
            "type": "user_pattern",
            "category": category,
            "created_at": datetime.now().isoformat(),
            "success_count": 0,
            "total_usage": 0,
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            **(metadata or {})
        }

        # Add to Chroma
        self.patterns_collection.add(
            ids=[pattern_id],
            documents=[text],
            metadatas=[full_metadata]
        )

        # Store solution separately for easier retrieval
        solution_path = self.storage_path / "solutions" / f"{pattern_id}.json"
        solution_path.parent.mkdir(exist_ok=True)

        with open(solution_path, 'w') as f:
            json.dump({
                "solution": solution,
                "pattern_id": pattern_id,
                "created_at": datetime.now().isoformat()
            }, f, indent=2)

        print(f"💾 Pattern stored: {category} - {pattern_id}")
        return pattern_id

    def add_knowledge(self,
                     text: str,
                     category: str,
                     subcategory: str = None,
                     metadata: Dict = None) -> str:
        """Add general knowledge to the database"""

        knowledge_id = f"knowledge_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(text) % 10000}"

        full_metadata = {
            "type": "knowledge",
            "category": category,
            "subcategory": subcategory,
            "created_at": datetime.now().isoformat(),
            **(metadata or {})
        }

        self.knowledge_collection.add(
            ids=[knowledge_id],
            documents=[text],
            metadatas=[full_metadata]
        )

        print(f"📖 Knowledge stored: {category} - {subcategory}")
        return knowledge_id

    def find_similar_patterns(self,
                            query_text: str,
                            max_results: int = 5,
                            min_similarity: float = 0.7,
                            categories: List[str] = None) -> List[Dict]:
        """Find similar patterns using semantic search"""

        # Build where clause if categories specified
        where_clause = {"type": "user_pattern"}
        if categories:
            where_clause["category"] = {"$in": categories}

        # Query Chroma
        results = self.patterns_collection.query(
            query_texts=[query_text],
            n_results=max_results,
            where=where_clause
        )

        # Format results
        patterns = []
        if results['ids'][0]:
            for i, pattern_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i]  # Lower is better
                similarity = 1.0 - distance  # Convert to similarity

                if similarity >= min_similarity:
                    metadata = results['metadatas'][0][i]

                    # Load solution
                    solution = ""
                    solution_path = self.storage_path / "solutions" / f"{pattern_id}.json"
                    if solution_path.exists():
                        with open(solution_path, 'r') as f:
                            solution_data = json.load(f)
                            solution = solution_data.get("solution", "")

                    patterns.append({
                        "id": pattern_id,
                        "text": results['documents'][0][i],
                        "solution": solution,
                        "similarity": similarity,
                        "category": metadata.get("category", "general"),
                        "success_count": metadata.get("success_count", 0),
                        "total_usage": metadata.get("total_usage", 0),
                        "created_at": metadata.get("created_at"),
                        "metadata": metadata
                    })

        return patterns

    def find_knowledge(self,
                      query_text: str,
                      categories: List[str] = None,
                      max_results: int = 3) -> List[Dict]:
        """Find relevant knowledge items"""

        # Chroma needs different filtering approach
        if categories:
            # Use where with category filter
            results = self.knowledge_collection.query(
                query_texts=[query_text],
                n_results=max_results,
                where={"category": {"$in": categories}}
            )
        else:
            # No category filter, just type filter
            results = self.knowledge_collection.query(
                query_texts=[query_text],
                n_results=max_results,
                where={"type": "knowledge"}
            )

        knowledge_items = []
        if results['ids'][0]:
            for i, knowledge_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i]
                similarity = 1.0 - distance

                metadata = results['metadatas'][0][i]

                knowledge_items.append({
                    "id": knowledge_id,
                    "text": results['documents'][0][i],
                    "similarity": similarity,
                    "category": metadata.get("category"),
                    "subcategory": metadata.get("subcategory"),
                    "metadata": metadata
                })

        return knowledge_items

    def update_pattern_success(self, pattern_id: str, was_successful: bool):
        """Update success metrics for a pattern"""

        # Get current pattern
        try:
            pattern_data = self.patterns_collection.get(ids=[pattern_id])
            if not pattern_data['ids']:
                return

            current_metadata = pattern_data['metadatas'][0]
            success_count = current_metadata.get("success_count", 0)
            total_usage = current_metadata.get("total_usage", 0)

            # Update metrics
            total_usage += 1
            if was_successful:
                success_count += 1

            # Update in Chroma
            current_metadata["success_count"] = success_count
            current_metadata["total_usage"] = total_usage
            current_metadata["last_used"] = datetime.now().isoformat()

            self.patterns_collection.update(
                ids=[pattern_id],
                metadatas=[current_metadata]
            )

            success_rate = success_count / total_usage if total_usage > 0 else 0
            print(f"📊 Pattern {pattern_id}: {success_count}/{total_usage} = {success_rate:.1%}")

            # Track globally
            self.pattern_success[pattern_id] = {
                "success_count": success_count,
                "total_usage": total_usage,
                "success_rate": success_rate
            }

        except Exception as e:
            print(f"⚠️ Could not update pattern success: {e}")

    def get_learning_stats(self) -> Dict:
        """Get comprehensive learning statistics"""

        try:
            # Pattern stats
            total_patterns = self.patterns_collection.count()
            total_knowledge = self.knowledge_collection.count()

            # Get all patterns for analysis
            all_patterns = self.patterns_collection.get()
            categories = {}
            success_rates = []

            for metadata in all_patterns.get('metadatas', []):
                category = metadata.get("category", "general")
                categories[category] = categories.get(category, 0) + 1

                success_count = metadata.get("success_count", 0)
                total_usage = metadata.get("total_usage", 0)
                if total_usage > 0:
                    success_rates.append(success_count / total_usage)

            avg_success_rate = np.mean(success_rates) if success_rates else 0.0

            # Top performing patterns
            top_patterns = sorted(
                [(pid, data["success_rate"]) for pid, data in self.pattern_success.items()],
                key=lambda x: x[1], reverse=True
            )[:5]

            return {
                "total_patterns": total_patterns,
                "total_knowledge": total_knowledge,
                "categories": categories,
                "average_success_rate": avg_success_rate,
                "top_performing_patterns": top_patterns,
                "learning_active": True,
                "storage_path": str(self.storage_path)
            }

        except Exception as e:
            return {"error": str(e), "learning_active": False}

    def get_patterns_by_category(self, category: str) -> List[Dict]:
        """Get all patterns in a specific category"""

        results = self.patterns_collection.get(
            where={"category": category, "type": "user_pattern"}
        )

        patterns = []
        for i, pattern_id in enumerate(results['ids']):
            metadata = results['metadatas'][i]

            # Load solution
            solution = ""
            solution_path = self.storage_path / "solutions" / f"{pattern_id}.json"
            if solution_path.exists():
                with open(solution_path, 'r') as f:
                    solution_data = json.load(f)
                    solution = solution_data.get("solution", "")

            patterns.append({
                "id": pattern_id,
                "text": results['documents'][i],
                "solution": solution,
                "category": metadata.get("category"),
                "success_count": metadata.get("success_count", 0),
                "total_usage": metadata.get("total_usage", 0),
                "metadata": metadata
            })

        return patterns

    def clear_old_patterns(self, days_old: int = 30):
        """Remove patterns older than specified days"""

        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)

        # Get all patterns to check dates
        all_patterns = self.patterns_collection.get()
        to_remove = []

        for i, pattern_id in enumerate(all_patterns['ids']):
            metadata = all_patterns['metadatas'][i]
            created_at = metadata.get("created_at", "")

            if created_at:
                try:
                    pattern_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).timestamp()
                    if pattern_date < cutoff_date:
                        to_remove.append(pattern_id)
                except:
                    pass

        if to_remove:
            self.patterns_collection.delete(ids=to_remove)

            # Remove solution files
            for pattern_id in to_remove:
                solution_path = self.storage_path / "solutions" / f"{pattern_id}.json"
                if solution_path.exists():
                    solution_path.unlink()

            print(f"🗑️ Cleared {len(to_remove)} old patterns")
        else:
            print("✅ No old patterns to clear")

    def initialize_base_knowledge(self):
        """Initialize the knowledge base with basic RAG content"""

        # Check if already initialized
        if self.knowledge_collection.count() > 0:
            print("📚 Knowledge base already initialized")
            return

        print("🔧 Initializing base knowledge...")

        # Mood enhancement knowledge
        mood_knowledge = [
            {
                "text": "Get 10 minutes of sunlight exposure to regulate circadian rhythm and boost vitamin D levels",
                "category": "mood_enhancer",
                "subcategory": "morning"
            },
            {
                "text": "Practice deep breathing using the 4-7-8 technique: inhale for 4, hold for 7, exhale for 8",
                "category": "mood_enhancer",
                "subcategory": "anytime"
            },
            {
                "text": "Take a brief walk to boost dopamine levels and clear your mind",
                "category": "mood_enhancer",
                "subcategory": "afternoon"
            }
        ]

        # Creativity knowledge
        creativity_knowledge = [
            {
                "text": "Apply artificial constraints to solve problems with limited resources",
                "category": "creativity_booster",
                "subcategory": "when_stuck"
            },
            {
                "text": "Use mind mapping to visualize connections between ideas",
                "category": "creativity_booster",
                "subcategory": "brainstorming"
            },
            {
                "text": "Practice the SCAMPER technique: Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse",
                "category": "creativity_booster",
                "subcategory": "innovation"
            }
        ]

        # Productivity knowledge
        productivity_knowledge = [
            {
                "text": "Start with just 2 minutes of a task using the Kaizen method to overcome procrastination",
                "category": "productivity_technique",
                "subcategory": "motivation"
            },
            {
                "text": "Use the Pomodoro technique: 25 minutes of focused work followed by a 5-minute break",
                "category": "productivity_technique",
                "subcategory": "focus"
            },
            {
                "text": "Apply the 2-minute rule: if it takes less than 2 minutes, do it now",
                "category": "productivity_technique",
                "subcategory": "efficiency"
            }
        ]

        # Programming knowledge
        programming_knowledge = [
            {
                "text": "Always check for None values before accessing object attributes to prevent null pointer exceptions",
                "category": "programming_pattern",
                "subcategory": "error_prevention"
            },
            {
                "text": "Use meaningful variable names and add comments to explain complex logic",
                "category": "programming_pattern",
                "subcategory": "best_practices"
            },
            {
                "text": "Add proper error handling with try-catch blocks and provide helpful error messages",
                "category": "programming_pattern",
                "subcategory": "robustness"
            }
        ]

        # Add all knowledge to Chroma
        all_knowledge = mood_knowledge + creativity_knowledge + productivity_knowledge + programming_knowledge

        for item in all_knowledge:
            self.add_knowledge(
                text=item["text"],
                category=item["category"],
                subcategory=item["subcategory"]
            )

        print(f"✅ Initialized {len(all_knowledge)} knowledge items")