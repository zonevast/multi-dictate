#!/usr/bin/env python3
"""
Smart AI Router - Automatically finds working API and remembers it
Features:
- Tests APIs to find working one
- Stores successful API choice
- Auto-switches when one fails
- Tracks success rates
"""

import logging
import json
import os
import time
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class SmartAIRouter:
    """
    Intelligent router that:
    1. Tries APIs in order of past success
    2. Remembers which one works
    3. Auto-switches on failure
    4. Tracks statistics
    """

    def __init__(self, config):
        self.config = config
        self.processors = {}
        self.success_db_path = Path.home() / ".config" / "multi-dictate" / "ai_success.json"
        self.success_db_path.parent.mkdir(parents=True, exist_ok=True)

        # Load success history
        self.success_data = self._load_success_db()

        # Initialize available processors
        self._initialize_processors()

        # Determine best processor based on history
        self.current_processor = self._get_best_processor()

        logger.info(f"🧠 Smart AI Router initialized")
        logger.info(f"📊 Current choice: {self.current_processor}")

    def _load_success_db(self) -> Dict:
        """Load success history from disk"""
        if self.success_db_path.exists():
            try:
                with open(self.success_db_path, 'r') as f:
                    data = json.load(f)
                    logger.debug(f"📂 Loaded success DB: {data}")
                    return data
            except Exception as e:
                logger.warning(f"⚠️  Could not load success DB: {e}")

        # Default structure
        return {
            "last_successful": None,
            "last_success_time": 0,
            "success_count": {
                "openai": 0,
                "gemini": 0
            },
            "failure_count": {
                "openai": 0,
                "gemini": 0
            },
            "last_test_time": {
                "openai": 0,
                "gemini": 0
            }
        }

    def _save_success_db(self):
        """Save success history to disk"""
        try:
            with open(self.success_db_path, 'w') as f:
                json.dump(self.success_data, f, indent=2)
            logger.debug(f"💾 Saved success DB")
        except Exception as e:
            logger.warning(f"⚠️  Could not save success DB: {e}")

    def _initialize_processors(self):
        """Initialize all available AI processors"""
        from multi_dictate.openai_processor import OpenAIProcessor
        from multi_dictate.gemini_processor import GeminiProcessor

        # Try OpenAI
        openai_key = self.config.general.get('openai_api_key')
        if openai_key:
            try:
                openai_model = self.config.general.get('openai_model', 'gpt-4o-mini')
                self.processors['openai'] = OpenAIProcessor(openai_key, openai_model)
                logger.info(f"✅ OpenAI processor available")
            except Exception as e:
                logger.warning(f"⚠️  Could not init OpenAI: {e}")

        # Try Gemini
        gemini_keys = None
        if hasattr(self.config.general, 'gemini_api_keys'):
            gemini_keys = self.config.general.gemini_api_keys
        elif hasattr(self.config.general, 'gemini_api_key'):
            gemini_keys = [self.config.general.gemini_api_key]

        if gemini_keys:
            try:
                gemini_model = self.config.general.get('gemini_model', 'flash')
                self.processors['gemini'] = GeminiProcessor(gemini_keys, gemini_model)
                logger.info(f"✅ Gemini processor available")
            except Exception as e:
                logger.warning(f"⚠️  Could not init Gemini: {e}")

        if not self.processors:
            logger.error("❌ No AI processors available!")

    def _get_best_processor(self) -> Optional[str]:
        """Determine best processor based on success history"""
        if not self.processors:
            return None

        # If we have a recent success (< 1 hour ago), use it
        last_success = self.success_data.get('last_successful')
        last_success_time = self.success_data.get('last_success_time', 0)

        if last_success and last_success in self.processors:
            time_since_success = time.time() - last_success_time
            if time_since_success < 3600:  # 1 hour
                logger.info(f"🎯 Using last successful: {last_success} ({time_since_success/60:.0f}m ago)")
                return last_success

        # Calculate success rates
        scores = {}
        for name in self.processors.keys():
            success = self.success_data['success_count'].get(name, 0)
            failure = self.success_data['failure_count'].get(name, 0)
            total = success + failure

            if total > 0:
                score = success / total
            else:
                score = 0.5  # Unknown, give benefit of doubt

            scores[name] = score
            logger.debug(f"📊 {name}: {success}✅ / {failure}❌ = {score:.2%}")

        # Choose best score
        if scores:
            best = max(scores, key=scores.get)
            logger.info(f"🏆 Best processor by history: {best} ({scores[best]:.0%} success)")
            return best

        # Fallback: prefer OpenAI if available
        if 'openai' in self.processors:
            return 'openai'
        return list(self.processors.keys())[0]

    def _record_success(self, processor_name: str):
        """Record successful API call"""
        self.success_data['last_successful'] = processor_name
        self.success_data['last_success_time'] = time.time()
        self.success_data['success_count'][processor_name] = \
            self.success_data['success_count'].get(processor_name, 0) + 1
        self.success_data['last_test_time'][processor_name] = time.time()

        self._save_success_db()

        success_count = self.success_data['success_count'][processor_name]
        logger.info(f"✅ Recorded success for {processor_name} (total: {success_count})")

    def _record_failure(self, processor_name: str):
        """Record failed API call"""
        self.success_data['failure_count'][processor_name] = \
            self.success_data['failure_count'].get(processor_name, 0) + 1
        self.success_data['last_test_time'][processor_name] = time.time()

        self._save_success_db()

        failure_count = self.success_data['failure_count'][processor_name]
        logger.warning(f"❌ Recorded failure for {processor_name} (total: {failure_count})")

    def _should_retry_processor(self, processor_name: str) -> bool:
        """Check if we should retry a failed processor"""
        last_test = self.success_data['last_test_time'].get(processor_name, 0)
        time_since_test = time.time() - last_test

        # Retry after 5 minutes
        if time_since_test > 300:
            logger.info(f"🔄 {processor_name} failed before, but retrying ({time_since_test/60:.0f}m ago)")
            return True

        logger.debug(f"⏭️  Skipping {processor_name} (tested {time_since_test:.0f}s ago)")
        return False

    def process_dictation(self, text: str, clipboard_context: str = None) -> str:
        """
        Smart processing with automatic failover and success tracking.

        Process:
        1. Try current best processor
        2. If fails, try others
        3. Remember which one worked
        4. Use it first next time
        """
        if not text or not text.strip():
            return text

        if not self.processors:
            logger.warning("⚠️  No AI processors available, returning original")
            return text

        # Try current processor first
        if self.current_processor and self.current_processor in self.processors:
            logger.info(f"🎯 Trying primary: {self.current_processor}")
            result = self._try_processor(self.current_processor, text, clipboard_context)
            if result and result != text:
                self._record_success(self.current_processor)
                return result
            else:
                self._record_failure(self.current_processor)

        # Try other processors
        for name, processor in self.processors.items():
            if name == self.current_processor:
                continue  # Already tried

            if not self._should_retry_processor(name):
                continue  # Skip recently failed

            logger.info(f"🔄 Trying fallback: {name}")
            result = self._try_processor(name, text, clipboard_context)
            if result and result != text:
                self._record_success(name)
                self.current_processor = name  # Switch to this one
                logger.info(f"🎯 Switched to {name} as primary")
                return result
            else:
                self._record_failure(name)

        # All failed
        logger.warning("⚠️  All AI processors failed, returning original")
        return text

    def _try_processor(self, name: str, text: str, clipboard_context: str = None) -> Optional[str]:
        """Try to process with specific processor"""
        try:
            processor = self.processors[name]
            result = processor.process_dictation(text, clipboard_context)
            return result
        except Exception as e:
            logger.error(f"❌ {name} exception: {e}")
            return None

    def get_stats(self) -> Dict:
        """Get success statistics"""
        stats = {
            "current_processor": self.current_processor,
            "available_processors": list(self.processors.keys()),
            "success_rates": {}
        }

        for name in self.processors.keys():
            success = self.success_data['success_count'].get(name, 0)
            failure = self.success_data['failure_count'].get(name, 0)
            total = success + failure

            if total > 0:
                rate = success / total
            else:
                rate = 0

            stats['success_rates'][name] = {
                "success": success,
                "failure": failure,
                "rate": f"{rate:.1%}"
            }

        return stats
