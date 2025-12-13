#!/usr/bin/env python3
"""RAG-Enhanced AI processor for context-aware dictation"""

import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .database.vector_store import LocalVectorStore
from .database.knowledge_base import KnowledgeBase
from .utils.context_collector import ContextCollector

logger = logging.getLogger(__name__)


class RAGEnhancedProcessor:
    """Enhanced AI processor with RAG capabilities"""

    def __init__(self, ai_processor, config):
        """Initialize with existing AI processor and config"""
        self.ai_processor = ai_processor
        self.config = config

        # Initialize RAG components
        storage_path = config.general.get('storage_path', '~/.config/multi-dictate')
        self.knowledge_base = KnowledgeBase(storage_path)
        self.context_collector = ContextCollector()

        # RAG settings
        self.rag_enabled = config.general.get('rag_enabled', True)
        self.max_context_items = config.general.get('max_context_items', 5)
        self.similarity_threshold = config.general.get('similarity_threshold', 0.7)

        logger.info("✅ RAG-Enhanced processor initialized")
        logger.info(f"Knowledge base stats: {self.knowledge_base.get_stats()}")

    def process_with_rag(self, text: str, user_intent: str = None) -> Tuple[str, Dict]:
        """Process text with RAG enhancement"""
        if not self.rag_enabled:
            # Fall back to regular processing
            result = self.ai_processor.process_dictation(text)
            return result, {'rag_used': False, 'context_items': []}

        # Collect context
        context = self.context_collector.collect_all_context()

        # Determine user intent
        if not user_intent:
            user_intent = self._classify_intent(text, context)

        # Get relevant knowledge
        relevant_knowledge = self._retrieve_relevant_knowledge(text, context, user_intent)

        # Build enhanced prompt
        enhanced_prompt = self._build_rag_prompt(text, context, relevant_knowledge, user_intent)

        # Process with AI
        try:
            result = self._process_with_ai(enhanced_prompt, user_intent)

            # Learn from interaction
            self._learn_from_interaction(text, context, relevant_knowledge, result)

            return result, {
                'rag_used': True,
                'context_items': relevant_knowledge,
                'user_intent': user_intent,
                'context_summary': self.context_collector.get_context_summary()
            }

        except Exception as e:
            logger.error(f"RAG processing failed: {e}")
            # Fall back to regular processing
            result = self.ai_processor.process_dictation(text)
            return result, {'rag_used': False, 'error': str(e)}

    def _classify_intent(self, text: str, context: Dict) -> str:
        """Classify user intent from text and context"""
        text_lower = text.lower()

        # Mood enhancement indicators
        mood_keywords = [
            'mood', 'feel', 'feeling', 'emotional', 'happy', 'sad', 'anxious',
            'depressed', 'energized', 'motivated', 'unstuck', 'boost'
        ]

        # Creativity indicators
        creativity_keywords = [
            'creative', 'ideas', 'inspiration', 'stuck', 'block', 'innovation',
            'think differently', 'new perspective', 'brainstorm'
        ]

        # Problem-solving indicators
        problem_keywords = [
            'fix', 'solve', 'how to', 'help with', 'issue', 'problem', 'error',
            'debug', 'implement', 'create'
        ]

        # Task management indicators
        task_keywords = [
            'organize', 'plan', 'schedule', 'reminder', 'track', 'manage',
            'routine', 'habit', 'productivity'
        ]

        # Check for each intent type
        if any(keyword in text_lower for keyword in mood_keywords):
            return 'mood_enhancement'
        elif any(keyword in text_lower for keyword in creativity_keywords):
            return 'creativity_boost'
        elif any(keyword in text_lower for keyword in problem_keywords):
            return 'problem_solving'
        elif any(keyword in text_lower for keyword in task_keywords):
            return 'task_management'

        # Check context for clues
        clipboard = context.get('clipboard_content', {})
        if clipboard.get('type') == 'mood_related':
            return 'mood_enhancement'
        elif context.get('active_window', {}).get('type') in ['editor', 'terminal']:
            return 'problem_solving'

        return 'general_enhancement'

    def _retrieve_relevant_knowledge(self, text: str, context: Dict, user_intent: str) -> List[Dict]:
        """Retrieve relevant knowledge based on intent and context"""
        relevant_items = []

        if user_intent == 'mood_enhancement':
            # Get mood suggestions based on current state
            current_state = self._extract_mood_state(text, context)
            relevant_items = self.knowledge_base.get_mood_suggestions(current_state)

        elif user_intent == 'creativity_boost':
            # Get creativity boosters
            current_block = self._extract_creativity_block(text, context)
            available_resources = self._get_available_resources(context)
            relevant_items = self.knowledge_base.get_creativity_boosters(current_block, available_resources)

        elif user_intent == 'problem_solving':
            # Check if problem is in clipboard
            if context.get('clipboard_content', {}).get('type') == 'error':
                problem_text = context['clipboard_content']['content']
                relevant_items = self.knowledge_base.search_knowledge(problem_text, n_results=3)

        else:
            # General search
            relevant_items = self.knowledge_base.search_knowledge(text, n_results=3)

        # Filter by similarity threshold
        relevant_items = [
            item for item in relevant_items
            if item.get('relevance_score', 0) >= self.similarity_threshold
        ]

        return relevant_items[:self.max_context_items]

    def _extract_mood_state(self, text: str, context: Dict) -> str:
        """Extract current mood state from text and context"""
        text_lower = text.lower()
        time_context = context.get('time_context', {})

        # Direct mood mentions
        if 'tired' in text_lower or 'fatigue' in text_lower:
            return 'low_energy'
        elif 'stressed' in text_lower or 'anxious' in text_lower:
            return 'stressed'
        elif 'unmotivated' in text_lower or 'procrastinate' in text_lower:
            return 'unmotivated'
        elif 'stuck' in text_lower or 'blocked' in text_lower:
            return 'stuck'

        # Time-based mood inference
        if time_context.get('day_part') == 'late_night':
            return 'night_owl'

        return 'general'

    def _extract_creativity_block(self, text: str, context: Dict) -> str:
        """Extract creativity block description"""
        text_lower = text.lower()

        if 'new ideas' in text_lower:
            return 'idea_generation'
        elif 'different perspective' in text_lower:
            return 'perspective_shift'
        elif 'inspiration' in text_lower:
            return 'seeking_inspiration'
        else:
            return 'creative_block'

    def _get_available_resources(self, context: Dict) -> List[str]:
        """Get available resources for creativity enhancement"""
        resources = []

        # Check location
        if context.get('active_window', {}).get('type') == 'browser':
            resources.append('internet_access')

        # Check time
        time_context = context.get('time_context', {})
        if time_context.get('day_part') in ['morning', 'afternoon']:
            resources.append('daylight')

        # Check environment
        if not context.get('environment_state', {}).get('system_load', {}).get('is_high'):
            resources.append('low_system_load')

        return resources

    def _build_rag_prompt(self, text: str, context: Dict, knowledge: List[Dict], user_intent: str) -> str:
        """Build enhanced prompt with RAG context"""
        prompt_parts = []

        # Add role and context
        prompt_parts.append(f"""You are an empathetic AI assistant specializing in {user_intent.replace('_', ' ')}.
Consider the user's current situation and provide personalized, actionable advice.""")

        # Add time and environmental context
        time_context = context.get('time_context', {})
        prompt_parts.append(f"""
CURRENT CONTEXT:
- Time: {time_context.get('day_part', 'unknown')} ({time_context.get('hour', 'unknown')}:00)
- Day: {time_context.get('day_of_week', 'unknown')}
- Active in: {context.get('active_window', {}).get('type', 'unknown')}
""")

        # Add retrieved knowledge
        if knowledge:
            prompt_parts.append("\nRELEVANT INSIGHTS:")
            for i, item in enumerate(knowledge[:3], 1):
                prompt_parts.append(f"{i}. {item['text']}")

        # Add user input
        prompt_parts.append(f"\nUSER REQUEST: {text}")

        # Add specific instructions based on intent
        if user_intent == 'mood_enhancement':
            prompt_parts.append("""
TASK: Provide mood enhancement strategies that:
1. Work for the current time and energy level
2. Are practical and immediately actionable
3. Promote emotional independence from environment
4. Include both quick fixes and sustainable practices

Format as numbered steps with specific actions.""")
        elif user_intent == 'creativity_boost':
            prompt_parts.append("""
TASK: Suggest creativity enhancement methods that:
1. Work with current resources and constraints
2. Stimulate new ways of thinking
3. Are practical to implement immediately
4. Encourage innovative problem-solving

Format as actionable techniques with brief explanations.""")
        else:
            prompt_parts.append("\nTASK: Provide helpful, actionable response based on the context.")

        return "\n".join(prompt_parts)

    def _process_with_ai(self, prompt: str, user_intent: str) -> str:
        """Process prompt through AI with intent-specific handling"""
        # Use the underlying AI processor
        # Note: We might need to adapt this based on the AI processor interface
        if hasattr(self.ai_processor, 'process_dictation'):
            # For smart router or direct processors
            # Extract the user request part for processing
            lines = prompt.split('\n')
            user_request = None
            for line in lines:
                if line.startswith('USER REQUEST:'):
                    user_request = line.replace('USER REQUEST:', '').strip()
                    break

            if user_request:
                return self.ai_processor.process_dictation(user_request, prompt)

        # Fallback: return the prompt processed as-is
        return prompt

    def _learn_from_interaction(self, user_input: str, context: Dict, knowledge_used: List[Dict], result: str):
        """Learn from successful interactions"""
        # Extract feedback implicitly (can be enhanced with explicit feedback)
        feedback_score = None  # Could be collected from user

        # Create learning entry
        context_summary = {
            'time': context.get('time_context', {}).get('day_part'),
            'environment': context.get('active_window', {}).get('type'),
            'intent': self._classify_intent(user_input, context)
        }

        # Add to knowledge base if result was helpful
        if feedback_score is None or feedback_score > 0:
            learning_text = f"User: {user_input}\nContext: {context_summary}\nSolution: {result}"
            metadata = {
                'category': 'user_interaction',
                'intent': context_summary['intent'],
                'context_time': context_summary['time'],
                'helpfulness': 'unknown'  # Could be updated with user feedback
            }

            self.knowledge_base.add_knowledge(learning_text, metadata, source="interaction")

    def add_user_feedback(self, session_id: str, rating: int, comment: str = None):
        """Add user feedback for learning improvement"""
        # Find the most recent interaction for this session
        # Update knowledge based on feedback
        self.knowledge_base.learn_from_interaction(
            user_input="",  # Would need to track this
            context="",
            ai_response="",
            feedback=rating
        )

    def get_personalized_suggestions(self, intent: str = None) -> List[Dict]:
        """Get personalized suggestions based on learned patterns"""
        if intent:
            filters = {'intent': intent}
        else:
            filters = {'category': 'user_interaction'}

        return self.knowledge_base.vector_store.get_by_metadata(filters, limit=5)

    def save_state(self):
        """Save RAG state to disk"""
        self.knowledge_base.save_learning()
        logger.info("💾 RAG state saved")

    def get_rag_stats(self) -> Dict:
        """Get RAG system statistics"""
        stats = self.knowledge_base.get_stats()
        stats['rag_enabled'] = self.rag_enabled
        stats['max_context_items'] = self.max_context_items
        stats['similarity_threshold'] = self.similarity_threshold
        return stats