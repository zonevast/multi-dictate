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
        """Check if Ollama and the model are available."""
        try:
            # Check if Ollama is installed
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                logger.warning("Ollama not found - Qwen processor requires Ollama")
                logger.info("To install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
                logger.info("To download Qwen Turbo: ollama pull qwen-turbo")
                return False

            # Check if model is available
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                logger.error("Failed to list Ollama models")
                return False

            # Check if specific model is listed
            if self.model not in result.stdout:
                logger.info(f"Model {self.model} not found, attempting to download...")
                return self._download_model()

            logger.info(f"✅ Qwen model {self.model} is available")
            return True

        except FileNotFoundError:
            logger.warning("Ollama command not found")
            return False
        except Exception as e:
            logger.error(f"Error checking Qwen availability: {e}")
            return False

    def _download_model(self) -> bool:
        """Download the Qwen model if not available."""
        try:
            logger.info(f"📥 Downloading {self.model} model...")
            print(f"Downloading {self.model} model (this may take a few minutes)...")

            result = subprocess.run(
                ["ollama", "pull", self.model],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )

            if result.returncode == 0:
                logger.info(f"✅ Successfully downloaded {self.model}")
                return True
            else:
                logger.error(f"❌ Failed to download {self.model}: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"❌ Download of {self.model} timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error downloading {self.model}: {e}")
            return False

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

        # Build enhanced prompt
        prompt = self._build_prompt(text, clipboard_context)

        try:
            # Call Qwen model
            response = self._call_qwen(prompt)
            if response:
                logger.info(f"Qwen processed: '{text[:30]}...' → '{response[:50]}...'")
                return response
            else:
                logger.warning("Qwen returned empty response")
                return text

        except Exception as e:
            logger.error(f"Error processing with Qwen: {e}")
            return f"[Qwen error: {e}] {text}"

    def _build_prompt(self, text: str, clipboard_context: str = None) -> str:
        """Build an enhanced prompt for Qwen."""
        prompt_parts = [
            "You are a helpful AI assistant.",
            "Please process the following input and provide a clear, helpful response."
        ]

        if clipboard_context and clipboard_context.strip():
            prompt_parts.append(f"\nContext: {clipboard_context}")

        prompt_parts.append(f"\nInput: {text}")

        prompt_parts.append(
            "\nProvide a clear, structured response that directly addresses the request above."
        )

        return "\n".join(prompt_parts)

    def _call_qwen(self, prompt: str) -> Optional[str]:
        """Call Qwen model with the given prompt."""
        try:
            # Use Ollama to call the model
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"Qwen call failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("Qwen call timed out")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling Qwen: {e}")
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