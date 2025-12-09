#!/usr/bin/env python3
"""
Gemini AI text processor for enhanced dictation.
Processes speech recognition output through Gemini API before typing.
"""

import logging
import traceback
import requests
import json
from typing import Optional

logger = logging.getLogger(__name__)


class GeminiProcessor:
    """Process text through Gemini API for enhancement, assistance, and optimization."""

    # Available models for different use cases
    MODELS = {
        "flash": "gemini-2.0-flash",           # Fast, stable, good for most tasks
        "flash-25": "gemini-2.5-flash",        # Newer flash (may have rate limits)
        "pro": "gemini-2.5-pro",               # More accurate, better reasoning (rate limited)
        "thinking": "gemini-2.0-flash-thinking-exp",  # Deep thinking for complex tasks
    }

    def __init__(self, api_keys, model: str = "flash"):
        # Support both single key (string) and multiple keys (list)
        self.api_keys = api_keys if isinstance(api_keys, list) else [api_keys]
        self.current_key_index = 0
        self.model = self.MODELS.get(model, self.MODELS["flash"])
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        logger.info(f"Using Gemini model: {self.model} with {len(self.api_keys)} API key(s)")
        
    def _make_request(self, prompt: str) -> Optional[str]:
        """Make request to Gemini API with automatic fallback to next key on quota error."""
        headers = {"Content-Type": "application/json"}

        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 2048
            }
        }

        # Try each API key in rotation
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
                            logger.info(f"✅ API key #{key_num} success")
                            return content.strip()
                        else:
                            logger.warning(f"No content in response: {candidate.get('finishReason', 'unknown')}")

                elif response.status_code == 429:
                    # Quota exceeded - try next key
                    logger.warning(f"❌ API key #{key_num} quota exceeded, trying next key...")
                    self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
                    continue
                else:
                    logger.error(f"API key #{key_num} error: {response.status_code} - {response.text[:200]}")

            except Exception as e:
                logger.error(f"API key #{key_num} request failed: {e}")
                logger.debug(traceback.format_exc())

            # Try next key on any error
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)

        logger.error("❌ All API keys failed or quota exceeded")
        return None
    
    def process_dictation(self, text: str, clipboard_context: str = None) -> str:
        """
        Process dictated text through Gemini for enhancement and assistance.

        Args:
            text: Raw speech recognition output
            clipboard_context: Optional clipboard content for context

        Returns:
            Enhanced/processed text ready for typing
        """
        if not text or not text.strip():
            return text

        # Build prompt with optional clipboard context
        if clipboard_context and clipboard_context.strip():
            prompt = f"""You are a prompt engineer. Convert this speech into a clear, professional request.

Context (from clipboard):
\"\"\"
{clipboard_context[:2000]}
\"\"\"

Speech Input: "{text}"

Rules:
- Use the clipboard context to understand what the user is working on
- If it's a task: Create numbered steps (1. 2. 3.)
- If it's a request: Make it clear and professional
- Keep same length or slightly longer, NOT too long
- Output ONLY the improved text, no explanations

Output:"""
        else:
            prompt = f"""You are a prompt engineer. Convert this speech into a clear, professional request.

Input: "{text}"

Rules:
- If it's a task: Create numbered steps (1. 2. 3.)
- If it's a request: Make it clear and professional
- Keep same length or slightly longer, NOT too long
- Use professional language
- Output ONLY the improved text, no explanations

Output:"""

        try:
            processed = self._make_request(prompt)
            if processed:
                logger.info(f"Original: '{text}' -> Enhanced: '{processed}'")
                return processed
            else:
                logger.warning("Gemini processing failed, returning original text")
                return text
                
        except Exception as e:
            logger.error(f"Error processing with Gemini: {e}")
            return text
    
    def get_assistance(self, text: str) -> str:
        """
        Get step-by-step assistance for user requests.
        
        Args:
            text: User's question or request
            
        Returns:
            Detailed step-by-step assistance
        """
        prompt = f"""The user said: "{text}"

Provide clear, step-by-step assistance. If it's:
- A technical question: Give specific steps to solve it
- A task request: Break it down into actionable steps
- A problem: Provide troubleshooting steps
- General help: Give organized guidance

Format as numbered steps when appropriate. Be concise but thorough."""

        try:
            response = self._make_request(prompt)
            return response if response else f"I'll help with: {text}"
        except Exception as e:
            logger.error(f"Error getting assistance: {e}")
            return f"Let me help with: {text}"