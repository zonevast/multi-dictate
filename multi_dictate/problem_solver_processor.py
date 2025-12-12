#!/usr/bin/env python3
"""
Problem Solver AI processor - analyzes clipboard problems and generates solutions
"""

import logging
import traceback
import requests
import json
from typing import Optional

logger = logging.getLogger(__name__)


class ProblemSolverProcessor:
    """Specialized processor for solving problems from clipboard context"""

    def __init__(self, api_keys, model: str = "gemini-2.5-flash"):
        self.api_keys = api_keys if isinstance(api_keys, list) else [api_keys]
        self.current_key_index = 0
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        logger.info(f"Problem Solver using Gemini model: {model} with {len(self.api_keys)} key(s)")

    def _make_request(self, prompt: str) -> Optional[str]:
        """Make request to Gemini API with key rotation"""
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048
            }
        }

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

                elif response.status_code == 429:
                    logger.warning(f"❌ Key #{key_num} quota exceeded")
                    self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
                    continue

            except Exception as e:
                logger.error(f"❌ Key #{key_num} error: {e}")
                self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)

        return None

    def process_problem(self, user_input: str, clipboard_context: str) -> str:
        """
        Process user input about a problem and generate a solution

        Args:
            user_input: User's speech/request about the problem
            clipboard_context: The problem description from clipboard

        Returns:
            Professional solution/fix for the problem
        """

        if not clipboard_context:
            return "Please copy the problem description to clipboard first."

        # Detect if it's asking for a solution/fix
        solution_keywords = [
            'fix', 'solve', 'solution', 'how to', 'implement', 'create',
            'address', 'handle', 'resolve', 'deal with', 'approach',
            'propose', 'suggest', 'recommend', 'plan'
        ]

        is_asking_solution = any(keyword in user_input.lower() for keyword in solution_keywords)

        if not is_asking_solution:
            # Just regular enhancement without problem-solving
            return user_input

        # Build problem-solving prompt
        prompt = f"""You are a senior software architect and problem solver.

PROBLEM CONTEXT (from clipboard):
'''
{clipboard_context[:3000]}
'''

USER REQUEST: "{user_input}"

TASK: Analyze the problem and provide a clear, actionable solution.

GUIDELINES:
- Provide specific implementation steps or approaches
- Reference the components mentioned in the problem
- Suggest practical solutions that can be implemented
- Use professional, clear language
- Be concise but comprehensive
- Focus on actionable solutions, not just descriptions

FORMAT YOUR RESPONSE AS:
1. **Immediate Action**: Quick fix or temporary solution
2. **Implementation Plan**: Step-by-step approach
3. **Key Components**: What needs to be created/modified

SOLUTION:"""

        try:
            solution = self._make_request(prompt)
            if solution:
                logger.info(f"Generated solution for: {user_input[:50]}...")
                return solution
            else:
                return "Failed to generate solution. Please try again."

        except Exception as e:
            logger.error(f"Error processing problem: {e}")
            return "Error generating solution."