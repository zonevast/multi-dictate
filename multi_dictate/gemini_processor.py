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
        self.model_name = self.MODELS.get(model, self.MODELS["flash"])
        logger.info(f"Using Gemini model: {self.model_name} with {len(self.api_keys)} API key(s)")
        
        # Try to import SDK
        try:
            import google.generativeai as genai
            self.genai = genai
        except ImportError:
            logger.error("❌ google-generativeai SDK not found! Please install with 'pip install google-generativeai'")
            self.genai = None

    def _configure_client(self, api_key):
        """Configure the GenAI client with a specific key"""
        if self.genai:
            self.genai.configure(api_key=api_key)

    def _make_request(self, prompt: str) -> Optional[str]:
        """
        Make request to Gemini. 
        Priority:
        1. SDK (if api_keys present)
        2. CLI (if no keys, attempt `gemini "prompt"`)
        """
        
        # 1. SDK Mode
        if self.api_keys and self.api_keys[0]:
             if not self.genai:
                 logger.error("SDK not initialized/installed.")
                 return None

             for attempt in range(len(self.api_keys)):
                 api_key = self.api_keys[self.current_key_index]
                 key_num = self.current_key_index + 1
                 
                 try:
                     self._configure_client(api_key)
                     model = self.genai.GenerativeModel(self.model_name)
                     
                     response = model.generate_content(
                         prompt,
                         generation_config=self.genai.types.GenerationConfig(
                             temperature=0.1, max_output_tokens=2048
                         )
                     )
                     
                     if response.text:
                         logger.info(f"✅ API key #{key_num} success")
                         return response.text.strip()
                     
                 except Exception as e:
                     logger.warning(f"❌ API key #{key_num} failed: {e}")
                     self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
                     continue
             
             logger.error("❌ All API keys failed")
             return None

        # 2. CLI Mode (Fallback if no keys)
        else:
             logger.info("🔧 No API keys found. Attempting CLI mode: `gemini \"prompt\"`")
             try:
                 import subprocess
                 # User confirmed `gemini` is installed and works directly
                 cli_cmd = ["gemini", prompt]

                 result = subprocess.run(
                     cli_cmd,
                     capture_output=True,
                     text=True,
                     timeout=45 # Increased timeout for npx startup
                 )
                 
                 if result.returncode == 0 and result.stdout:
                     return result.stdout.strip()
                 else:
                     logger.error(f"❌ CLI failed: {result.stderr}")
                     return None
             except FileNotFoundError:
                 logger.error("❌ 'gemini' CLI command not found.")
                 return None
             except Exception as e:
                 logger.error(f"❌ CLI execution error: {e}")
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

        # Check if this is already an optimized prompt - if so, execute it directly
        is_optimized_prompt = any(indicator in text for indicator in [
            "Act as an expert", "Target Project:", "Project Name:", "Technical Context:",
            "Task:", "Context:", "Issues to Address:", "Requirements:", "Implementation Steps:"
        ])

        if is_optimized_prompt:
            # This is already an optimized prompt, execute it directly
            prompt = f"""You are an AI assistant. Execute the following optimized prompt and provide a comprehensive response.

{text}

Provide a detailed, actionable response that directly addresses the request above.
Include specific steps, examples, and practical advice where relevant."""
            logger.info("✨ Processing optimized prompt directly")
        else:
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
            logger.info("🔧 Processing raw speech input")

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