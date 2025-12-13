#!/usr/bin/env python3
"""
Qwen AI processor for multi-dictate.
Provides Qwen model integration through Ollama.
"""

import logging
import subprocess
import json
import time
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class QwenProcessor:
    """Qwen model processor using Ollama."""

    # Available Qwen models
    MODELS = {
        "qwen-turbo": {
            "name": "Qwen Turbo",
            "size": "7b",
            "speed": "fast",
            "context": 8192
        },
        "qwen-plus": {
            "name": "Qwen Plus",
            "size": "14b",
            "speed": "medium",
            "context": 32768
        },
        "qwen-max": {
            "name": "Qwen Max",
            "size": "72b",
            "speed": "slow",
            "context": 32768
        }
    }

    def __init__(self, model: str = "qwen-turbo"):
        self.model = model
        self.model_info = self.MODELS.get(model, self.MODELS["qwen-turbo"])
        self.available = self._check_availability()

        if self.available:
            logger.info(f"✅ Qwen processor initialized with {self.model_info['name']}")
        else:
            logger.warning(f"⚠️ Qwen {model} not available")

    def _check_availability(self) -> bool:
        """Check if qwen CLI is available."""
        try:
            # Check if qwen CLI is installed
            result = subprocess.run(
                ["qwen", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                logger.warning("qwen CLI not found")
                return False
            
            logger.info("✅ qwen CLI tool is available")
            return True

        except FileNotFoundError:
            logger.warning("qwen command not found")
            return False
        except Exception as e:
            logger.error(f"Error checking qwen availability: {e}")
            return False

    def _download_model(self) -> bool:
        """No-op for CLI tool which manages its own models."""
        return True

    def process_dictation(self, text: str, clipboard_context: str = None) -> str:
        """
        Process text through Qwen model.
        Args:
            text: Input text to process
            clipboard_context: Optional clipboard context
        Returns:
            Processed text from Qwen
        """
        if not text or not text.strip():
            return text

        if not self.available:
            logger.warning("Qwen not available, returning original text")
            return f"[Qwen unavailable] {text}"

        # For the CLI, we just use the text as prompt since it's already a meta-prompt
        # But if there's clipboard context separately, we can append it
        prompt = text
        if clipboard_context:
            prompt += f"\n\nCONTEXT:\n{clipboard_context}"

        try:
            # Call Qwen model
            response = self._call_qwen(prompt)
            if response:
                logger.info(f"Qwen processed: '{text[:30]}...' -> Response length: {len(response)}")
                return response
            else:
                logger.warning("Qwen returned empty response")
                return text

        except Exception as e:
            logger.error(f"Error processing with Qwen: {e}")
            return f"[Qwen error: {e}] {text}"

    def _call_qwen(self, prompt: str) -> Optional[str]:
        """Call qwen CLI with the given prompt."""
        try:
            # Use qwen CLI to call the model
            # We use --output-format text to get clean output
            logger.debug(f"Calling qwen CLI with prompt length: {len(prompt)}")
            
            result = subprocess.run(
                ["qwen", prompt, "-o", "text"],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if result.returncode == 0:
                # The CLI output might contain some header/footer, but -o text should be relatively clean
                return result.stdout.strip()
            else:
                logger.error(f"qwen CLI call failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("qwen CLI call timed out")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling qwen CLI: {e}")
            return None

    def get_available_models(self) -> List[str]:
        """Get list of available Qwen models."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Parse available models
                models = []
                for model_id in self.MODELS.keys():
                    if model_id in result.stdout:
                        models.append(model_id)
                return models
            else:
                logger.error("Failed to list available models")
                return []

        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    def get_model_info(self) -> Dict:
        """Get information about the current model."""
        return {
            "model": self.model,
            "name": self.model_info["name"],
            "size": self.model_info["size"],
            "speed": self.model_info["speed"],
            "context": self.model_info["context"],
            "available": self.available
        }

# Global instance
qwen_processor = QwenProcessor()