#!/usr/bin/env python3
"""Simple RAG processor without heavy dependencies"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import importlib.util

logger = logging.getLogger(__name__)

# Import Enhanced Chroma vector database, file context reader, and file analyzer
try:
    # Import Enhanced Chroma vector database
    chroma_path = os.path.join(os.path.dirname(__file__), "database", "enhanced_chroma_db.py")
    spec = importlib.util.spec_from_file_location("enhanced_chroma_db", chroma_path)
    chroma_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(chroma_module)
    EnhancedChromaDB = chroma_module.EnhancedChromaDB

    # Import File Context Reader
    file_reader_path = os.path.join(os.path.dirname(__file__), "utils", "file_context_reader.py")
    spec = importlib.util.spec_from_file_location("file_context_reader", file_reader_path)
    file_reader_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(file_reader_module)
    FileContextReader = file_reader_module.FileContextReader

    # Import File Analyzer
    analyzer_path = os.path.join(os.path.dirname(__file__), "utils", "file_analyzer.py")
    spec = importlib.util.spec_from_file_location("file_analyzer", analyzer_path)
    analyzer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analyzer_module)
    FileContentAnalyzer = analyzer_module.FileContentAnalyzer

    # Import Implementation Guide Generator
    guide_gen_path = os.path.join(os.path.dirname(__file__), "utils", "implementation_guide_generator.py")
    spec = importlib.util.spec_from_file_location("implementation_guide_generator", guide_gen_path)
    guide_gen_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guide_gen_module)
    ImplementationGuideGenerator = guide_gen_module.ImplementationGuideGenerator

    # Import Prompt Optimizer
    prompt_opt_path = os.path.join(os.path.dirname(__file__), "prompt_optimizer.py")
    spec = importlib.util.spec_from_file_location("prompt_optimizer", prompt_opt_path)
    prompt_opt_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prompt_opt_module)
    PromptOptimizer = prompt_opt_module.PromptOptimizer

    VECTOR_DB_AVAILABLE = True
    logger.info("✅ Enhanced Chroma vector database, file reader, and file analyzer loaded successfully")
except Exception as e:
    VECTOR_DB_AVAILABLE = False
    logger.warning(f"⚠️ Components not available: {e}")
    EnhancedChromaDB = None
    FileContextReader = None
    FileContentAnalyzer = None
    ImplementationGuideGenerator = None
    PromptOptimizer = None


class SimpleRAGProcessor:
    """Lightweight RAG processor using keyword matching"""

    def __init__(self, config):
        self.config = config
        self.storage_path = os.path.expanduser(config.general.get('storage_path', '~/.config/multi-dictate'))

        # Initialize Enhanced Chroma vector database if available
        self.vector_db = None
        if VECTOR_DB_AVAILABLE:
            try:
                # Get embedding configuration
                embedding_config = config.general.get('embedding', 'onnx')  # Default to ONNX

                # Try to get OpenAI key if using OpenAI embeddings
                api_key = None
                if embedding_config == 'openai':
                    api_key = config.general.get('openai_api_key')

                self.vector_db = EnhancedChromaDB(
                    storage_path=self.storage_path,
                    embedding_function=embedding_config,
                    api_key=api_key
                )
                # Initialize base knowledge if empty
                self.vector_db.initialize_base_knowledge()
                logger.info(f"🧠 Enhanced Chroma pattern learning system initialized with {embedding_config} embeddings")
            except Exception as e:
                logger.warning(f"⚠️ Enhanced Chroma DB initialization failed: {e}")
                self.vector_db = None

        # Initialize File Context Reader (separate from ChromaDB)
        self.file_reader = None
        if FileContextReader:
            try:
                self.file_reader = FileContextReader()
                logger.info("📁 File context reader initialized")
            except Exception as e:
                logger.warning(f"⚠️ File context reader initialization failed: {e}")
                self.file_reader = None

        # Initialize File Content Analyzer
        self.file_analyzer = None
        if FileContentAnalyzer:
            try:
                self.file_analyzer = FileContentAnalyzer()
                logger.info("🔍 File content analyzer initialized")
            except Exception as e:
                logger.warning(f"⚠️ File analyzer initialization failed: {e}")
                self.file_analyzer = None

        # Initialize Implementation Guide Generator
        self.guide_generator = None
        if ImplementationGuideGenerator:
            try:
                self.guide_generator = ImplementationGuideGenerator()
                logger.info("📋 Implementation guide generator initialized")
            except Exception as e:
                logger.warning(f"⚠️ Guide generator initialization failed: {e}")
                self.guide_generator = None

        # Initialize Prompt Optimizer
        self.prompt_optimizer = None
        if PromptOptimizer:
            try:
                self.prompt_optimizer = PromptOptimizer()
                logger.info("📝 Prompt optimizer initialized")
            except Exception as e:
                logger.warning(f"⚠️ Prompt optimizer initialization failed: {e}")
                self.prompt_optimizer = None

        # Initialize knowledge base
        self.knowledge = {
            'mood_enhancers': {
                'morning': [
                    "Get 10 minutes of sunlight exposure to regulate circadian rhythm",
                    "Practice deep breathing: 4-7-8 technique for 3 minutes",
                    "Write down 3 things you're grateful for",
                    "Do 5 minutes of light stretching"
                ],
                'afternoon': [
                    "Take a brief walk to boost dopamine and clear your mind",
                    "Change your physical environment for a fresh perspective",
                    "Listen to uplifting music for 10 minutes",
                    "Practice the 2-minute rule for quick accomplishments"
                ],
                'evening': [
                    "Practice self-reflection: What went well today?",
                    "Plan tomorrow's 3 most important tasks",
                    "Disconnect from screens 30 minutes before bed",
                    "Create a closure ritual to signal workday end"
                ],
                'anytime': [
                    "Use the 5-4-3-2-1 grounding technique for anxiety",
                    "Implement the Pomodoro technique for focus",
                    "Apply creative constraints to spark innovation",
                    "Practice internal validation instead of seeking external approval"
                ]
            },
            'creativity_boosters': {
                'when_stuck': [
                    "Change your location - work from a different room or café",
                    "Apply artificial constraints: solve with limited resources",
                    "Use mind mapping to visualize connections",
                    "Take a 15-minute break and do something completely different"
                ],
                'for_new_ideas': [
                    "Practice cross-pollination: connect unrelated concepts",
                    "Use the SCAMPER technique (Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse)",
                    "Engage in free writing for 10 minutes without judgment",
                    "Ask 'What would [child/inventor/artist] do in this situation?'"
                ],
                'for_innovation': [
                    "Challenge assumptions: What if the opposite were true?",
                    "Use analogical thinking from different domains",
                    "Prototype quickly: Build a minimum viable solution",
                    "Gather diverse perspectives from outside your field"
                ]
            },
            'productivity_techniques': {
                'when_unmotivated': [
                    "Start with just 2 minutes of the task (Kaizen method)",
                    "Connect the task to your larger goals",
                    "Use temptation bundling: Pair task with something enjoyable",
                    "Create a visual progress tracker"
                ],
                'for_focus': [
                    "Use time-blocking with clear boundaries",
                    "Implement 'single-tasking' - one thing at a time",
                    "Create a distraction-free environment",
                    "Use the 2-minute rule for small tasks"
                ]
            }
        }

        # Track successful suggestions
        self.success_log = []
        self.load_history()

    def load_history(self):
        """Load interaction history"""
        history_file = os.path.join(self.storage_path, 'rag_history.json')
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    self.success_log = json.load(f)
        except Exception as e:
            logger.debug(f"Could not load history: {e}")

    def save_history(self):
        """Save interaction history"""
        history_file = os.path.join(self.storage_path, 'rag_history.json')
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            with open(history_file, 'w') as f:
                json.dump(self.success_log[-50:], f, indent=2)  # Keep last 50
        except Exception as e:
            logger.debug(f"Could not save history: {e}")

    def store_pattern(self, user_input: str, solution: str, metadata: Dict = None):
        """Store successful patterns for future learning"""
        if not self.vector_db:
            return

        try:
            category = self._categorize_pattern(user_input)
            full_metadata = {
                'user_input': user_input,
                **(metadata or {})
            }

            # Store in Chroma
            pattern_id = self.vector_db.add_pattern(
                text=user_input,
                solution=solution,
                category=category,
                metadata=full_metadata
            )

            logger.info(f"💾 Pattern stored: {category} - {pattern_id}")
            return pattern_id  # Return the pattern_id

        except Exception as e:
            logger.warning(f"Could not store pattern: {e}")
            return None  # Return None on error

    def _categorize_pattern(self, text: str) -> str:
        """Categorize user pattern type"""
        text_lower = text.lower()

        # Programming patterns
        if any(word in text_lower for word in ['fix', 'error', 'bug', 'debug', 'exception']):
            return 'programming_fix'
        elif any(word in text_lower for word in ['implement', 'create', 'build', 'add']):
            return 'implementation'
        elif any(word in text_lower for word in ['test', 'testing', 'validate']):
            return 'testing'
        elif any(word in text_lower for word in ['api', 'database', 'sql', 'query']):
            return 'data_management'

        # Productivity patterns
        elif any(word in text_lower for word in ['mood', 'feel', 'motivated', 'focus']):
            return 'productivity'
        elif any(word in text_lower for word in ['creative', 'ideas', 'innovation']):
            return 'creativity'
        elif any(word in text_lower for word in ['learn', 'understand', 'explain']):
            return 'learning'

        return 'general'

    def find_similar_patterns(self, user_input: str, max_results: int = 3) -> List[Dict]:
        """Find similar past patterns based on semantic similarity"""
        if not self.vector_db:
            return []

        try:
            # Search for similar patterns in Chroma
            patterns = self.vector_db.find_similar_patterns(
                query_text=user_input,
                max_results=max_results,
                min_similarity=0.1  # Lower threshold for testing
            )

            return patterns

        except Exception as e:
            logger.warning(f"Could not find similar patterns: {e}")
            return []

    def update_pattern_success(self, pattern_id: str, was_successful: bool):
        """Update success rate for a pattern"""
        if not self.vector_db:
            return

        try:
            self.vector_db.update_pattern_success(pattern_id, was_successful)
        except Exception as e:
            logger.warning(f"Could not update pattern success: {e}")

    def get_learning_stats(self) -> Dict:
        """Get pattern learning statistics"""
        if not self.vector_db:
            return {'message': 'Pattern learning not available'}

        try:
            stats = self.vector_db.get_learning_stats()
            return stats
        except Exception as e:
            return {'error': str(e)}

    def enhance_prompt(self, text: str, context: Dict = None) -> str:
        """Enhance prompt with structured analysis, implementation guides, and testing procedures"""
        if not context:
            context = {}

        # Check for similar past patterns from ChromaDB memory
        similar_patterns = self.find_similar_patterns(text, max_results=2)

        # Read and analyze file content
        file_analysis_results = []
        file_content = ""
        if context and 'clipboard' in context:
            clipboard_content = context['clipboard']
            if clipboard_content and isinstance(clipboard_content, str):
                # Read file content
                if self.file_reader:
                    file_result = self.file_reader.read_from_clipboard(clipboard_content)
                    if file_result['success']:
                        file_content = file_result['content']

                # Analyze file content for specific issues
                if self.file_analyzer and file_result.get('success'):
                    # Get file paths from file context reader
                    file_paths = file_result.get('file_paths', [])
                    if not file_paths and file_result['files_found'] > 0:
                        # Fallback path construction
                        clipboard_path = Path(clipboard_content.strip())
                        if clipboard_path.is_file():
                            file_paths.append(clipboard_content.strip())
                        else:
                            # Directory - construct paths
                            for file_name in file_result.get('file_names', []):
                                if clipboard_content.startswith('/'):
                                    full_path = os.path.join(clipboard_content, file_name)
                                else:
                                    full_path = file_name
                                file_paths.append(full_path)

                    # Analyze each file for issues
                    for file_path in file_paths[:3]:  # Limit to 3 files
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                analysis = self.file_analyzer.analyze_file_content(file_path, content)
                                if analysis['total_issues'] > 0:
                                    file_analysis_results.append(analysis)
                        except Exception as e:
                            logger.warning(f"Could not analyze {file_path}: {e}")

        # Always try enhanced structured response when RAG is enabled
        # Only fall back if there are actual errors during guide generation
        logger.info(f"🐛 DEBUG: RAG enhance_prompt called with text='{text}', context has clipboard={context and 'clipboard' in context}")
        logger.info(f"🐛 DEBUG: file_analysis_results count={len(file_analysis_results)}, similar_patterns count={len(similar_patterns) if similar_patterns else 0}")

        if self.guide_generator:
            # Generate structured implementation guide
            structured_solution = None
            if similar_patterns and any(p.get('has_structured_solution') for p in similar_patterns):
                # Use structured solution from best matching pattern
                best_pattern = max(
                    [p for p in similar_patterns if p.get('structured_solution')],
                    key=lambda x: x.get('similarity', 0)
                )
                structured_solution = best_pattern.get('structured_solution')

            # Extract URL from text, context, or clipboard if available
            url_match = None
            # Look for URLs in the text
            import re
            url_pattern = r'https?://[^\s]+'

            # First check the voice text for URLs
            url_matches = re.findall(url_pattern, text)
            if url_matches:
                url_match = url_matches[0]

            # If no URL in voice text, check clipboard content
            if not url_match and context and 'clipboard' in context:
                clipboard_content = context['clipboard']
                if clipboard_content and isinstance(clipboard_content, str):
                    clipboard_urls = re.findall(url_pattern, clipboard_content)
                    if clipboard_urls:
                        url_match = clipboard_urls[0]

            # Set URL information on the guide generator BEFORE generating guide
            if url_match:
                self.guide_generator._current_url = url_match
                logger.info(f"🐛 DEBUG: Set URL on guide generator BEFORE generation: {url_match}")

            # Generate the implementation guide
            try:
                logger.info(f"🐛 DEBUG: About to generate guide, url_match={url_match}")
                guide = self.guide_generator.generate_guide(
                    structured_solution=structured_solution,
                    file_analysis=file_analysis_results,
                    pattern_info=similar_patterns
                )
                logger.info(f"🐛 DEBUG: Guide generated with {len(guide['implementation_steps'])} steps")

                # Format as text for output
                enhanced_response = self.guide_generator.format_guide_as_text(guide)
                logger.info(f"🐛 DEBUG: Formatted response length={len(enhanced_response)}")

                # Clear URL after use
                if hasattr(self.guide_generator, '_current_url'):
                    delattr(self.guide_generator, '_current_url')

                # Add file context if available
                if file_content:
                    enhanced_response = f"\n\n📁 File Context (Temporary Enhancement):\n{file_content}\n{enhanced_response}"

                return enhanced_response

            except Exception as e:
                logger.info(f"🐛 DEBUG: Exception in enhanced response: {e}")
                logger.error(f"Failed to generate structured guide: {e}")
                logger.error(f"Text: {text}")
                logger.error(f"Context: {context}")
                logger.error(f"File analysis results: {file_analysis_results}")
                logger.error(f"Similar patterns: {len(similar_patterns) if similar_patterns else 0}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Fall back to traditional format

        # Fall back to traditional enhancement if structured guide generation fails
        logger.info(f"🐛 DEBUG: Falling back to traditional enhancement")
        return self._generate_traditional_enhancement(text, context, similar_patterns, file_analysis_results, file_content)

    def _generate_traditional_enhancement(self, text: str, context: Dict, similar_patterns: List,
                                        file_analysis_results: List, file_content: str) -> str:
        """Generate traditional enhancement format (fallback method)"""

        logger.info(f"🐛 DEBUG: Traditional enhancement called with text='{text}', context keys={list(context.keys()) if context else 'None'}")

        enhancement_parts = []

        # Extract URL from clipboard if available
        url_info = ""
        if context and 'clipboard' in context:
            clipboard_content = context['clipboard']
            if clipboard_content and isinstance(clipboard_content, str):
                import re
                url_pattern = r'https?://[^\s]+'
                clipboard_urls = re.findall(url_pattern, clipboard_content)
                if clipboard_urls:
                    url_info = clipboard_urls[0]

        # Add URL context if found
        if url_info:
            enhancement_parts.append(f"URL to optimize: {url_info}")

        # Add file content if found
        if file_content:
            enhancement_parts.append(f"\n\n📁 File Context (Temporary Enhancement):\n{file_content}")

        # Add file analysis if issues found
        if file_analysis_results:
            file_analysis = "\n\n🔍 FILE ANALYSIS (Issues Found):"
            for analysis in file_analysis_results:
                file_analysis += f"\n\n📄 {os.path.basename(analysis['file_path'])}:"
                file_analysis += f"\n   • {analysis['total_issues']} issues detected"
                file_analysis += f"\n   {analysis['summary']}"
                # Add top 3 issues
                top_issues = analysis['issues_found'][:3]
                for issue in top_issues:
                    line_num = issue.get('line', 'N/A')
                    file_analysis += f"\n   • Line {line_num}: {issue['description']}"
            enhancement_parts.append(file_analysis)

        # Add pattern context if found
        if similar_patterns:
            pattern_context = "\n\n💾 Relevant Past Solutions:"
            for i, pattern in enumerate(similar_patterns[:2], 1):
                success_rate = pattern.get('success_rate', 0) * 100
                similarity = pattern.get('similarity', 0) * 100
                pattern_context += f"\n{i}. Pattern ID: {pattern['id']} ({similarity:.0f} similar, {success_rate:.0f} success rate)"
                pattern_context += f"\n   Solution: {pattern.get('solution', 'No solution recorded')[:200]}..."
            enhancement_parts.append(pattern_context)

        # Get traditional knowledge
        knowledge_items = []
        if self.vector_db:
            knowledge_items = self.vector_db.find_knowledge(
                query_text=text,
                categories=['programming_pattern', 'productivity_technique'],
                max_results=2
            )

        if knowledge_items:
            knowledge_context = "\n\n🧠 Knowledge (from ChromaDB Memory):"
            for i, item in enumerate(knowledge_items[:2], 1):
                knowledge_context += f"\n{i}. {item.get('text', 'Unknown')} ({item.get('category', 'general')})"
            enhancement_parts.append(knowledge_context)

        # Build final response
        if enhancement_parts:
            # If we have URL info, provide a clean optimization prompt
            if url_info:
                return f"Need to analyze and optimize this page for better performance and dynamic data\nTarget URL: {url_info}"

            # Otherwise, provide basic enhancement
            context_joined = "".join(enhancement_parts)
            return f"""{context_joined}

Current Request: {text}

Based on the relevant solutions and knowledge above, provide targeted advice."""

        # Return original text if no enhancement
        return text

    def _get_base_enhancement(self, text: str, text_lower: str, time_context: str) -> str:
        """Get base enhancement without pattern learning"""

        # Check for combined mood + creativity
        if any(mood in text_lower for mood in ['mood', 'feel', 'emotion', 'happy', 'sad', 'energized']) and \
           any(creative in text_lower for creative in ['creative', 'ideas', 'inspire', 'foster', 'new']):
            mood_suggestions = self.knowledge['mood_enhancers'].get(time_context, [])
            mood_suggestions.extend(self.knowledge['mood_enhancers'].get('anytime', []))
            creative_suggestions = self.knowledge['creativity_boosters']['for_new_ideas']

            return f"""Based on your request for mood enhancement and creativity boost:

Mood Enhancement Strategies:
{chr(10).join(f"• {s}" for s in mood_suggestions[:2])}

Creativity Boosting Methods:
{chr(10).join(f"• {s}" for s in creative_suggestions[:2])}

Current Context: {time_context}
User Request: {text}

Provide actionable advice combining these approaches for both mood and creativity."""

        # Mood enhancement only
        elif any(keyword in text_lower for keyword in ['mood', 'feel', 'emotion', 'happy', 'sad', 'motivated', 'depressed', 'anxious', 'unstuck']):
            suggestions = self.knowledge['mood_enhancers'].get(time_context, [])
            suggestions.extend(self.knowledge['mood_enhancers'].get('anytime', []))

            return f"""Based on your current mood enhancement needs, here are personalized suggestions:

Relevant Strategies:
{chr(10).join(f"• {s}" for s in suggestions[:3])}

Current Context: {time_context}
User Request: {text}

Provide specific, actionable advice based on these strategies."""

        # Creativity boost only
        elif any(keyword in text_lower for keyword in ['creative', 'ideas', 'stuck', 'innovation', 'inspire', 'brainstorm']):
            if 'stuck' in text_lower:
                suggestions = self.knowledge['creativity_boosters']['when_stuck']
            elif any(kw in text_lower for kw in ['new', 'foster', 'generate']):
                suggestions = self.knowledge['creativity_boosters']['for_new_ideas']
            else:
                suggestions = self.knowledge['creativity_boosters']['for_innovation']

            return f"""To enhance your creativity, consider these proven techniques:

{chr(10).join(f"• {s}" for s in suggestions[:3])}

User Request: {text}

Provide specific actions using these creativity enhancement methods."""

        # Productivity techniques
        elif any(keyword in text_lower for keyword in ['productive', 'focus', 'motivated', 'unmotivated', 'procrastinate', 'productivity']):
            if 'unmotivated' in text_lower or 'procrastinate' in text_lower:
                suggestions = self.knowledge['productivity_techniques']['when_unmotivated']
            else:
                suggestions = self.knowledge['productivity_techniques']['for_focus']

            return f"""For better productivity, try these techniques:

{chr(10).join(f"• {s}" for s in suggestions[:3])}

User Request: {text}

Provide practical productivity advice."""

        # Default - no specific enhancement
        return text

    def process_with_context(self, text: str, context: Dict = None) -> Tuple[str, Dict]:
        """Process text with context enhancement and pattern learning"""
        enhanced = self.enhance_prompt(text, context)

        # Prepare response metadata
        metadata = {
            'simple_rag_used': enhanced != text,
            'suggestions_added': enhanced != text,
            'pattern_learning_active': self.vector_db is not None
        }

        # Add learning stats if available
        if self.vector_db:
            stats = self.get_learning_stats()
            metadata['learning_stats'] = stats

        # Log the interaction
        self.success_log.append({
            'input': text,
            'enhanced': enhanced != text,
            'timestamp': datetime.now().isoformat(),
            'patterns_found': len(self.find_similar_patterns(text))
        })

        self.save_history()

        return enhanced, metadata

    def store_successful_interaction(self, user_input: str, ai_response: str, user_feedback: str = None):
        """Store successful interaction for pattern learning"""
        if self.vector_db and self.vectorizer:
            # Categorize success based on user feedback or response quality
            success_category = 'neutral'
            if user_feedback:
                if any(positive in user_feedback.lower() for positive in ['good', 'helpful', 'perfect', 'thanks', 'solved']):
                    success_category = 'positive'
                elif any(negative in user_feedback.lower() for negative in ['bad', 'wrong', 'unhelpful', 'fix']):
                    success_category = 'negative'

            # Store pattern with success information
            self.store_pattern(
                user_input=user_input,
                solution=ai_response,
                metadata={
                    'user_feedback': user_feedback,
                    'success_category': success_category,
                    'timestamp': datetime.now().isoformat()
                }
            )

            # Update pattern success rates
            if success_category == 'positive':
                similar_patterns = self.find_similar_patterns(user_input)
                for pattern in similar_patterns:
                    self.update_pattern_success(pattern.get('id', 0), True)