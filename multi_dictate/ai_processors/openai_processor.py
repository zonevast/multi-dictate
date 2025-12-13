#!/usr/bin/env python3
"""
OpenAI GPT processor for enhanced dictation.
Uses ChatGPT API for text enhancement - MUCH better quotas than Gemini!
"""

import logging
import traceback
import requests
import json
import time
import hashlib
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class OpenAIProcessor:
    """Process text through OpenAI ChatGPT API for enhancement."""

    # Available models
    MODELS = {
        "gpt-4o": "gpt-4o",                    # Best quality, faster, cheaper
        "gpt-4o-mini": "gpt-4o-mini",          # Fast and cheap
        "gpt-4-turbo": "gpt-4-turbo-preview",  # Good quality
        "gpt-3.5": "gpt-3.5-turbo",            # Fast and cheap (legacy)
    }

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = self.MODELS.get(model, self.MODELS["gpt-4o-mini"])
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.last_request_time = 0
        self.min_request_interval = 0.1  # OpenAI has much better rate limits
        self.request_cache: Dict[str, str] = {}
        self.cache_timestamps: Dict[str, float] = {}
        self.cache_ttl = 300  # 5 minutes

        logger.info(f"✨ OpenAI processor initialized with model: {self.model}")

    def _get_cache_key(self, text: str, clipboard: Optional[str]) -> str:
        """Generate cache key for request"""
        content = f"{text}|{clipboard or ''}"
        return hashlib.md5(content.encode()).hexdigest()

    def _check_cache(self, cache_key: str) -> Optional[str]:
        """Check if cached result is still valid"""
        if cache_key in self.request_cache:
            timestamp = self.cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < self.cache_ttl:
                logger.debug("✅ Cache hit")
                return self.request_cache[cache_key]
            else:
                # Expired
                del self.request_cache[cache_key]
                del self.cache_timestamps[cache_key]
        return None

    def _update_cache(self, cache_key: str, result: str):
        """Update cache with new result"""
        self.request_cache[cache_key] = result
        self.cache_timestamps[cache_key] = time.time()

        # Keep cache size reasonable (max 100 entries)
        if len(self.request_cache) > 100:
            oldest_key = min(self.cache_timestamps, key=self.cache_timestamps.get)
            del self.request_cache[oldest_key]
            del self.cache_timestamps[oldest_key]

    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _make_request(self, prompt: str, retry_count: int = 0) -> Optional[str]:
        """Make request to OpenAI API with retry logic"""
        self._rate_limit()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert prompt engineer and technical writing assistant. Transform casual speech into clear, professional instructions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 500,
            "top_p": 0.95
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    logger.info(f"✅ OpenAI success")
                    return content.strip()

            elif response.status_code == 429:
                # Rate limit - retry with backoff
                if retry_count < 3:
                    backoff = 2 ** retry_count
                    logger.warning(f"⏳ Rate limit, retrying in {backoff}s...")
                    time.sleep(backoff)
                    return self._make_request(prompt, retry_count + 1)
                else:
                    logger.error("❌ Rate limit exceeded after retries")

            elif response.status_code == 401:
                logger.error("❌ Invalid API key")

            elif response.status_code == 403:
                logger.error("❌ API key doesn't have access to this model")

            else:
                error_msg = response.json().get("error", {}).get("message", "Unknown error")
                logger.error(f"❌ API error {response.status_code}: {error_msg}")

        except requests.Timeout:
            logger.error("⏱️  Request timeout")
            if retry_count < 2:
                return self._make_request(prompt, retry_count + 1)

        except Exception as e:
            logger.error(f"❌ Exception: {e}")
            logger.debug(traceback.format_exc())

        return None

    def _build_prompt(self, text: str, clipboard_context: Optional[str]) -> str:
        """Build optimized prompt for ChatGPT"""

        if clipboard_context and clipboard_context.strip():
            return f"""Transform this casual speech into a clear, professional instruction.

**Context** (user's current work):
```
{clipboard_context[:2000]}
```

**User's Speech**: "{text}"

**Transform it to**:
- Code task → Numbered steps (1. 2. 3.)
- Bug fix → Clear problem + solution approach
- Feature request → What needs to be built
- Question → Well-formed technical question

**Requirements**:
✓ Professional language (avoid "this", "that", "it")
✓ Be specific and clear
✓ Reference context when relevant
✓ Use technical terms appropriately
✓ Keep concise (2-4 lines or numbered steps)
✗ No explanations or meta-commentary

**Output only the transformed text**:"""

        else:
            return f"""Transform this casual speech into a clear, professional instruction.

**User's Speech**: "{text}"

**Transform it to**:
- Code task → Numbered steps (1. Do X, 2. Then Y)
- Request → Clear, specific statement
- Question → Well-formed technical question
- Bug report → Problem + expected behavior

**Requirements**:
✓ Professional language
✓ Add technical precision
✓ Use active voice
✓ Be concise (2-4 lines max)
✗ No explanations

**Output only the transformed text**:"""

    def process_dictation(self, text: str, clipboard_context: str = None) -> str:
        """
        Process dictated text through ChatGPT.

        Features:
        - Much better rate limits than Gemini
        - Higher quality output
        - Caching to reduce API calls
        - Automatic retry with backoff

        Args:
            text: Raw speech recognition output
            clipboard_context: Optional clipboard content for context

        Returns:
            Enhanced/processed text ready for typing
        """
        if not text or not text.strip():
            return text

        # Check cache first
        cache_key = self._get_cache_key(text, clipboard_context)
        cached_result = self._check_cache(cache_key)
        if cached_result:
            logger.info(f"📦 Using cached result")
            return cached_result

        # Build prompt
        prompt = self._build_prompt(text, clipboard_context)

        try:
            processed = self._make_request(prompt)
            if processed:
                # Clean up output
                processed = processed.strip()

                # Remove common AI artifacts
                if processed.startswith('"') and processed.endswith('"'):
                    processed = processed[1:-1]
                if processed.startswith('Output:'):
                    processed = processed[7:].strip()

                logger.info(f"✨ '{text}' → '{processed}'")

                # Cache the result
                self._update_cache(cache_key, processed)

                return processed
            else:
                logger.warning("⚠️  Processing failed, returning original")
                return text

        except Exception as e:
            logger.error(f"💥 Error processing: {e}")
            logger.debug(traceback.format_exc())
            return text

    def get_assistance(self, text: str) -> str:
        """Get detailed help"""
        prompt = f"""The user needs help: "{text}"

Provide step-by-step guidance:
- Technical questions: Give specific troubleshooting steps
- Tasks: Break down into actionable steps
- Problems: Provide solution approaches

Be concise but thorough. Use numbered lists."""

        try:
            response = self._make_request(prompt)
            return response if response else f"I'll help with: {text}"
        except Exception as e:
            logger.error(f"Error getting assistance: {e}")
            return f"Let me help with: {text}"
