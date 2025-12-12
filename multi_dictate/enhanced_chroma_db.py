#!/usr/bin/env python3
"""
Enhanced Chroma Vector Database with Configurable Embedding Functions
Supports multiple embedding backends: ONNX, OpenAI, HuggingFace, etc.
"""

import chromadb
import chromadb.utils.embedding_functions as ef
import numpy as np
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

class EnhancedChromaDB:
    """Enhanced ChromaDB with configurable embedding functions"""

    def __init__(self,
                 storage_path: str = "~/.config/multi-dictate/chroma",
                 embedding_function: str = "onnx",  # Options: onnx, openai, huggingface, fastembed
                 api_key: str = None,
                 model_name: str = None):

        self.storage_path = Path(os.path.expanduser(storage_path))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.embedding_type = embedding_function

        # Initialize embedding function
        self.embedding_function = self._get_embedding_function(
            embedding_function, api_key, model_name
        )

        print(f"🔥 Enhanced Chroma DB initialized with {embedding_function} embeddings")

        # Initialize Chroma client
        self.client = chromadb.PersistentClient(path=str(self.storage_path))

        # Collections for different types of data
        # Try to get existing collections first to avoid embedding function conflicts
        try:
            self.patterns_collection = self.client.get_collection("user_patterns")
            print(f"📚 Using existing patterns collection with current embedding function")
        except Exception:
            # Create new collection with custom embedding function
            self.patterns_collection = self.client.get_or_create_collection(
                name="user_patterns",
                embedding_function=self.embedding_function,
                metadata={"description": "User interaction patterns for learning"}
            )
            print(f"📚 Created new patterns collection with {embedding_function} embeddings")

        try:
            self.knowledge_collection = self.client.get_collection("knowledge_base")
            print(f"🧠 Using existing knowledge collection with current embedding function")
        except Exception:
            # Create new collection with custom embedding function
            self.knowledge_collection = self.client.get_or_create_collection(
                name="knowledge_base",
                embedding_function=self.embedding_function,
                metadata={"description": "General knowledge for RAG enhancement"}
            )
            print(f"🧠 Created new knowledge collection with {embedding_function} embeddings")

        # Learning tracking
        self.pattern_success = {}

        print(f"📚 Pattern collection: {self.patterns_collection.count()} items")
        print(f"🧠 Knowledge collection: {self.knowledge_collection.count()} items")

    def _get_embedding_function(self, embedding_type: str, api_key: str = None, model_name: str = None):
        """Get the appropriate embedding function"""

        if embedding_type == "onnx":
            # Default: Fast, no external dependencies, uses ONNX optimized MiniLM
            print("📦 Using ONNX MiniLM-L6-v2 (fast, no dependencies)")
            return ef.ONNXMiniLM_L6_V2()

        elif embedding_type == "openai":
            # Best quality, requires API key
            if not api_key:
                # Try to get from environment
                api_key = os.getenv("OPENAI_API_KEY") or self._get_openai_key_from_config()
            if not api_key:
                raise ValueError("OpenAI API key required for OpenAI embeddings")
            print("🚀 Using OpenAI text-embedding-ada-002 (best quality)")
            return ef.OpenAIEmbeddingFunction(api_key=api_key)

        elif embedding_type == "huggingface":
            # Good quality, local processing
            model = model_name or "all-MiniLM-L6-v2"
            print(f"🤗 Using HuggingFace {model} (good quality, local)")
            try:
                return ef.HuggingFaceEmbeddingFunction(model_name=model)
            except Exception as e:
                print(f"⚠️ HuggingFace failed, falling back to ONNX: {e}")
                return ef.ONNXMiniLM_L6_V2()

        elif embedding_type == "fastembed":
            # Fast, lightweight
            print("⚡ Using FastEmbed (ultra-fast)")
            try:
                return ef.Text2VecEmbeddingFunction()
            except Exception as e:
                print(f"⚠️ FastEmbed not available, falling back to ONNX: {e}")
                return ef.ONNXMiniLM_L6_V2()

        elif embedding_type == "jina":
            # Good alternative, requires API key
            if not api_key:
                raise ValueError("Jina API key required for Jina embeddings")
            print(f"🎯 Using Jina embeddings (good quality)")
            return ef.JinaEmbeddingFunction(api_key=api_key)

        else:
            print(f"⚠️ Unknown embedding type '{embedding_type}', using ONNX")
            return ef.ONNXMiniLM_L6_V2()

    def _get_openai_key_from_config(self):
        """Try to get OpenAI key from dictate.yaml"""
        try:
            config_path = Path.home() / ".config/multi-dictate/dictate.yaml"
            if config_path.exists():
                import yaml
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    return config.get('general', {}).get('openai_api_key')
        except Exception:
            pass
        return None

    def add_pattern(self,
                   text: str,
                   solution: Any,  # Can be string or structured solution object
                   category: str = "general",
                   metadata: Dict = None) -> str:
        """Add a new pattern to the database"""

        # Create unique ID
        pattern_id = f"pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(text) % 10000}"

        # Enhanced metadata for structured solutions
        full_metadata = {
            "type": "user_pattern",
            "category": category,
            "created_at": datetime.now().isoformat(),
            "success_count": 0,
            "total_usage": 0,
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "embedding_type": self.embedding_type,
            **(metadata or {})
        }

        # Handle structured solution objects
        if isinstance(solution, dict) and "implementation_steps" in solution:
            # This is a structured solution - add enhanced metadata
            full_metadata.update({
                "has_structured_solution": True,
                "estimated_time": solution.get("metadata", {}).get("estimated_time", "Unknown"),
                "complexity": solution.get("metadata", {}).get("complexity", "medium"),
                "files_count": len(solution.get("files_affected", [])),
                "steps_count": len(solution.get("implementation_steps", []))
            })

        # Add to Chroma
        self.patterns_collection.add(
            ids=[pattern_id],
            documents=[text],
            metadatas=[full_metadata]
        )

        # Store solution separately for easier retrieval
        solution_path = self.storage_path / "solutions" / f"{pattern_id}.json"
        solution_path.parent.mkdir(exist_ok=True)

        # Prepare solution data for storage
        solution_data = {
            "pattern_id": pattern_id,
            "created_at": datetime.now().isoformat(),
            "embedding_type": self.embedding_type,
            "solution_text": solution if isinstance(solution, str) else "",
            "structured_solution": solution if isinstance(solution, dict) else None
        }

        # Add additional metadata for structured solutions
        if isinstance(solution, dict) and "metadata" in solution:
            solution_data.update(solution["metadata"])

        with open(solution_path, 'w') as f:
            json.dump(solution_data, f, indent=2)

        print(f"💾 Pattern stored: {category} - {pattern_id} ({self.embedding_type})")
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
            "embedding_type": self.embedding_type,
            **(metadata or {})
        }

        self.knowledge_collection.add(
            ids=[knowledge_id],
            documents=[text],
            metadatas=[full_metadata]
        )

        print(f"📖 Knowledge stored: {category} - {subcategory} ({self.embedding_type})")
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

                    # Load solution (enhanced to handle structured solutions)
                    solution = ""
                    structured_solution = None
                    solution_path = self.storage_path / "solutions" / f"{pattern_id}.json"
                    if solution_path.exists():
                        with open(solution_path, 'r') as f:
                            solution_data = json.load(f)
                            # Handle both old and new solution formats
                            solution = solution_data.get("solution_text", "") or solution_data.get("solution", "")
                            structured_solution = solution_data.get("structured_solution")

                    # Calculate success rate
                    success_count = metadata.get("success_count", 0)
                    total_usage = metadata.get("total_usage", 0)
                    success_rate = (success_count / total_usage) if total_usage > 0 else 0.0

                    pattern_data = {
                        "id": pattern_id,
                        "text": results['documents'][0][i],
                        "solution": solution,
                        "structured_solution": structured_solution,
                        "similarity": similarity,
                        "category": metadata.get("category", "general"),
                        "success_count": success_count,
                        "total_usage": total_usage,
                        "success_rate": success_rate,
                        "created_at": metadata.get("created_at"),
                        "embedding_type": metadata.get("embedding_type", self.embedding_type),
                        "metadata": metadata
                    }

                    # Add enhanced metadata if available
                    if metadata.get("has_structured_solution"):
                        pattern_data.update({
                            "has_structured_solution": True,
                            "estimated_time": metadata.get("estimated_time", "Unknown"),
                            "complexity": metadata.get("complexity", "medium"),
                            "files_count": metadata.get("files_count", 0),
                            "steps_count": metadata.get("steps_count", 0)
                        })

                    patterns.append(pattern_data)

        return patterns

    def find_knowledge(self,
                      query_text: str,
                      categories: List[str] = None,
                      max_results: int = 3) -> List[Dict]:
        """Find relevant knowledge items"""

        # Chroma needs different filtering approach
        if categories:
            results = self.knowledge_collection.query(
                query_texts=[query_text],
                n_results=max_results,
                where={"category": {"$in": categories}}
            )
        else:
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
                    "embedding_type": metadata.get("embedding_type", self.embedding_type),
                    "metadata": metadata
                })

        return knowledge_items

    def update_pattern_success(self, pattern_id: str, was_successful: bool):
        """Update success metrics for a pattern"""

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

            return {
                "total_patterns": total_patterns,
                "total_knowledge": total_knowledge,
                "categories": categories,
                "average_success_rate": avg_success_rate,
                "embedding_type": self.embedding_type,
                "top_performing_patterns": sorted(
                    [(pid, data["success_rate"]) for pid, data in self.pattern_success.items()],
                    key=lambda x: x[1], reverse=True
                )[:5],
                "learning_active": True,
                "storage_path": str(self.storage_path)
            }

        except Exception as e:
            return {"error": str(e), "learning_active": False}

    def test_embedding_quality(self, test_texts: List[str] = None):
        """Test the embedding quality with sample texts"""

        if not test_texts:
            test_texts = [
                "fix database connection error",
                "optimize API performance",
                "implement user authentication",
                "feeling unmotivated at work",
                "need creative ideas for project"
            ]

        print(f"\n🧪 Testing {self.embedding_type} embedding quality...")

        try:
            embeddings = self.embedding_function(test_texts)
            print(f"✅ Generated {len(embeddings)} embeddings")
            print(f"   Dimension: {embeddings[0].shape}")
            print(f"   Sample values: {embeddings[0][:5]}...")

            # Test similarity calculation
            if len(embeddings) >= 2:
                similarity = np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                )
                print(f"   Similarity between first two: {similarity:.3f}")

        except Exception as e:
            print(f"❌ Embedding test failed: {e}")

    def initialize_base_knowledge(self):
        """Initialize the knowledge base with basic RAG content"""

        # Check if already initialized
        if self.knowledge_collection.count() > 0:
            print("📚 Knowledge base already initialized")
            return

        print("🔧 Initializing base knowledge...")

        # Same knowledge items as before
        knowledge_items = [
            # Mood enhancement
            {
                "text": "Get 10 minutes of sunlight exposure to regulate circadian rhythm",
                "category": "mood_enhancer",
                "subcategory": "morning"
            },
            {
                "text": "Practice deep breathing: 4-7-8 technique for 3 minutes",
                "category": "mood_enhancer",
                "subcategory": "anytime"
            },
            # Creativity
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
            # Productivity
            {
                "text": "Start with just 2 minutes of a task using the Kaizen method",
                "category": "productivity_technique",
                "subcategory": "motivation"
            },
            {
                "text": "Use the Pomodoro technique: 25 minutes focused, 5 minutes break",
                "category": "productivity_technique",
                "subcategory": "focus"
            },
            # Programming
            {
                "text": "Always check for None values before accessing object attributes",
                "category": "programming_pattern",
                "subcategory": "error_prevention"
            },
            {
                "text": "Use meaningful variable names and add comments for complex logic",
                "category": "programming_pattern",
                "subcategory": "best_practices"
            }
        ]

        # Add all knowledge to Chroma
        for item in knowledge_items:
            self.add_knowledge(
                text=item["text"],
                category=item["category"],
                subcategory=item["subcategory"]
            )

        print(f"✅ Initialized {len(knowledge_items)} knowledge items with {self.embedding_type} embeddings")