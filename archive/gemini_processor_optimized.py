#!/usr/bin/env python3
"""
OPTIMIZED Gemini AI text processor with:
- Better prompt engineering
- Rate limiting
- Request caching
- Better error handling
- Exponential backoff
"""

import logging
import traceback
import requests
import json
import time
import hashlib
from typing import Optional, Dict
from functools import lru_cache

logger = logging.getLogger(__name__)


class GeminiProcessorOptimized:
    """Optimized processor with better quota management and quality."""

    MODELS = {
        "flash": "gemini-2.0-flash",           # Better quota limits
        "flash-25": "gemini-2.5-flash",        # Newer but rate limited
        "pro": "gemini-2.5-pro",               # Best quality but slow
        "thinking": "gemini-2.0-flash-thinking-exp",
    }

    def __init__(self, api_keys, model: str = "flash"):
        self.api_keys = api_keys if isinstance(api_keys, list) else [api_keys]
        self.current_key_index = 0
        self.model = self.MODELS.get(model, self.MODELS["flash"])
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
        self.request_cache: Dict[str, str] = {}  # Simple cache
        self.cache_ttl = 300  # 5 minutes
        self.cache_timestamps: Dict[str, float] = {}

        logger.info(f"✨ Optimized processor using: {self.model} with {len(self.api_keys)} key(s)")

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
            # Remove oldest entry
            oldest_key = min(self.cache_timestamps, key=self.cache_timestamps.get)
            del self.request_cache[oldest_key]
            del self.cache_timestamps[oldest_key]

    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"⏱️  Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _make_request(self, prompt: str, retry_count: int = 0) -> Optional[str]:
        """Make request with exponential backoff and better error handling"""
        self._rate_limit()

        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,  # Increased from 0.1 for better creativity
                "maxOutputTokens": 2048,
                "topP": 0.95,
                "topK": 40
            }
        }

        # Try each API key
        for attempt in range(len(self.api_keys)):
            api_key = self.api_keys[self.current_key_index]
            key_num = self.current_key_index + 1

            try:
                response = requests.post(
                    f"{self.base_url}?key={api_key}",
                    headers=headers,
                    json=data,
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    if "candidates" in result and result["candidates"]:
                        candidate = result["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            content = candidate["content"]["parts"][0]["text"]
                            logger.info(f"✅ Key #{key_num} success")
                            return content.strip()
                        else:
                            reason = candidate.get('finishReason', 'unknown')
                            logger.warning(f"⚠️  Key #{key_num} no content: {reason}")

                elif response.status_code == 429:
                    # Quota exceeded - try next key
                    logger.warning(f"❌ Key #{key_num} quota exceeded → trying next")
                    self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)

                    # Exponential backoff before trying next key
                    if retry_count < 3:
                        backoff = 2 ** retry_count
                        logger.info(f"⏳ Backing off {backoff}s before retry...")
                        time.sleep(backoff)
                        return self._make_request(prompt, retry_count + 1)
                    continue

                elif response.status_code == 503:
                    # Service unavailable - retry with backoff
                    if retry_count < 2:
                        backoff = 2 ** retry_count
                        logger.warning(f"⚠️  Service unavailable, retrying in {backoff}s...")
                        time.sleep(backoff)
                        return self._make_request(prompt, retry_count + 1)

                else:
                    logger.error(f"❌ Key #{key_num} error {response.status_code}: {response.text[:200]}")

            except requests.Timeout:
                logger.error(f"⏱️  Key #{key_num} timeout")
            except Exception as e:
                logger.error(f"❌ Key #{key_num} exception: {e}")
                logger.debug(traceback.format_exc())

            # Try next key
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)

        logger.error("💥 All API keys failed")
        return None

    def _build_optimized_prompt(self, text: str, clipboard_context: Optional[str]) -> str:
        """Build better prompt for higher quality output"""

        if clipboard_context and clipboard_context.strip():
            # With context - more specific
            return f"""You are an expert prompt engineer and technical writing assistant. Transform casual speech into professional, actionable instructions.

**Context** (user's current work):
```
{clipboard_context[:2000]}
```

**User's Speech**: "{text}"

**Task**: Transform the speech into a clear, professional request that:

1. **If it's a coding task**: Break into numbered implementation steps (1. 2. 3.)
2. **If it's a bug fix**: Describe the problem and solution approach clearly
3. **If it's a feature**: Outline what needs to be built
4. **If it's a question**: Reformulate as a clear technical question

**Requirements**:
✓ Use professional language (avoid "this", "that", "it" - be specific)
✓ Be concise but complete (1-3 sentences or numbered steps)
✓ Use technical terms when appropriate
✓ Reference the context when relevant
✓ Add specificity where speech was vague
✗ Do NOT add explanations or meta-commentary
✗ Do NOT make it overly long

**Output**:"""

        else:
            # Without context - more general
            return f"""You are an expert prompt engineer. Transform this casual speech into a clear, professional instruction.

**User's Speech**: "{text}"

**Transform it to**:
- **Code task** → Numbered steps (1. Do X, 2. Then Y, 3. Finally Z)
- **Request** → Clear, specific, professional statement
- **Question** → Well-formed technical question
- **Bug report** → Problem description + expected behavior

**Requirements**:
✓ Professional language (replace "make it", "fix this", "do that" with specific terms)
✓ Add technical precision
✓ Use active voice
✓ Be concise (2-4 lines maximum)
✗ No explanations
✗ No meta-commentary

**Output**:"""

    def process_dictation(self, text: str, clipboard_context: str = None) -> str:
        """
        Process dictated text with optimizations.

        Features:
        - Caching to reduce API calls
        - Rate limiting to avoid quota issues
        - Better prompts for higher quality
        - Exponential backoff on errors
        """
        if not text or not text.strip():
            return text

        # Check cache first
        cache_key = self._get_cache_key(text, clipboard_context)
        cached_result = self._check_cache(cache_key)
        if cached_result:
            logger.info(f"📦 Using cached result")
            return cached_result

        # Build optimized prompt
        prompt = self._build_optimized_prompt(text, clipboard_context)

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
        """Get detailed help (existing method for compatibility)"""
        prompt = f"""The user needs help with: "{text}"

Provide step-by-step guidance:
- For technical questions: Give specific troubleshooting steps
- For tasks: Break down into actionable steps
- For problems: Provide solution approaches

Be concise but thorough. Use numbered lists."""

        try:
            response = self._make_request(prompt)
            return response if response else f"I'll help with: {text}"
        except Exception as e:
            logger.error(f"Error getting assistance: {e}")
            return f"Let me help with: {text}"
