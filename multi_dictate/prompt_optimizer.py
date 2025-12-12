#!/usr/bin/env python3
"""
Prompt Optimizer Pipeline
Transforms raw messy input → Step 1 → Step 2 → Final Optimized Prompt
"""

import re
import json
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PromptOptimizer:
    """Optimizes user prompts through multi-step pipeline"""

    def __init__(self):
        self.optimization_patterns = {
            # Common messy patterns to fix
            'messy_input': [
                r'i\s+have\s+issue\s+in\s+my\s+(\w+)',  # "i have issue in my api"
                r'it\s+give\s+me\s+(\w+\s+\w+)',       # "it give me missing authentication"
                r'(\w+)\s+not\s+working',                # "api not working"
                r'i\s+think\s+the\s+problem\s+in',          # "i think the problem in"
                r'(\w+)\s+is\s+broken',                   # "login is broken"
            ],
            'grammar_fixes': [
                (r'\bi\s+have\b', 'I have'),
                (r'\bgive\s+me\b', 'gives me'),
                (r'\bit\s+give\s+me\b', 'it gives me'),
                (r'\bi\s+want\s+fix\b', 'I want to fix'),
                (r'\bi\s+need\s+your\s+help\b', 'I need your help'),
                (r'\bmy\s+(\w+)\s+not\s+working\b', r'My \1 is not working'),
            ],
            'clarification_patterns': [
                r'(\w+\s+error)',                         # "missing authentication token"
                r'(\w+\s+not\s+working)',                   # "api not working"
                r'(issue\s+in\s+\w+)',                       # "issue in my login"
                r'problem\s+in\s+(\w+)',                    # "problem in api gateway"
            ]
        }

        self.context_keywords = [
            'api', 'gateway', 'endpoint', 'route', 'service',
            'authentication', 'token', 'login', 'auth', 'security',
            'database', 'config', 'configuration', 'debug',
            'error', 'issue', 'problem', 'fix', 'optimize'
        ]

    def optimize_prompt(self, raw_input: str, context: Dict = None) -> Dict:
        """Apply the full prompt optimization pipeline"""

        optimization_steps = {
            'raw_input': raw_input.strip(),
            'step1_basic': None,
            'step2_improved': None,
            'final_optimized': None,
            'metadata': {
                'original_length': len(raw_input),
                'optimization_timestamp': datetime.now().isoformat(),
                'context_detected': False
            }
        }

        try:
            # Step 1: Basic Clean Improvement
            optimization_steps['step1_basic'] = self._apply_basic_improvement(raw_input)

            # Step 2: Enhanced with Context and Goals
            context_enriched = self._enrich_with_context(
                optimization_steps['step1_basic'],
                context
            )
            optimization_steps['step2_improved'] = context_enriched

            # Step 3: Final Optimized Prompt
            optimization_steps['final_optimized'] = self._generate_final_prompt(
                context_enriched,
                raw_input,
                context
            )

            # Add metadata
            optimization_steps['metadata']['context_detected'] = self._detect_context(raw_input)
            optimization_steps['metadata']['improvements_applied'] = self._get_improvements_applied(
                raw_input,
                optimization_steps['final_optimized']
            )

        except Exception as e:
            logger.error(f"Prompt optimization failed: {e}")
            # Fallback to basic improvement
            optimization_steps['step1_basic'] = self._apply_basic_improvement(raw_input)
            optimization_steps['step2_improved'] = optimization_steps['step1_basic']
            optimization_steps['final_optimized'] = optimization_steps['step1_basic']

        return optimization_steps

    def _apply_basic_improvement(self, text: str) -> str:
        """Apply basic grammar and structure improvements"""

        # Clean up the text
        text = text.strip()

        # Apply grammar fixes
        for pattern, replacement in self.optimization_patterns['grammar_fixes']:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # Fix common messy patterns
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\b(\w+)\s*\.', lambda m: m.group(1) + '.', text)  # Fix punctuation spacing
        text = re.sub(r'^i\s+', 'I ', text, flags=re.IGNORECASE)  # Capitalize 'I' at start

        # Fix sentence fragments
        if not text.endswith(('.', '?', '!')):
            text += '.'

        return text.strip()

    def _enrich_with_context(self, text: str, context: Dict = None) -> str:
        """Add context and purpose to the prompt"""

        if not context:
            # Add general purpose when no context provided
            return f"{text}\n\nPlease explain the problem clearly and provide actionable solutions."

        context_parts = []

        # Add file context if available
        if context.get('clipboard'):
            context_parts.append(f"Using the files from: {context['clipboard']}")

        # Add goal/purpose
        text_lower = text.lower()
        if any(word in text_lower for word in ['fix', 'debug', 'solve']):
            context_parts.append("Please provide clear steps to diagnose and resolve the issue.")
        elif any(word in text_lower for word in ['optimize', 'improve', 'enhance']):
            context_parts.append("Please suggest specific improvements with measurable results.")
        elif any(word in text_lower for word in ['explain', 'understand', 'learn']):
            context_parts.append("Please explain in simple terms with practical examples.")

        if context_parts:
            return f"{text}\n\n{'. '.join(context_parts)}"

        return text

    def _generate_final_prompt(self, improved_text: str, original_text: str, context: Dict = None) -> str:
        """Generate the final optimized prompt"""

        # Identify the main issue
        main_issue = self._extract_main_issue(improved_text)

        # Determine the action needed
        action_type = self._determine_action_type(improved_text)

        # Build structured prompt
        final_prompt_parts = []

        # Clear problem statement
        final_prompt_parts.append(f"**Problem:** {main_issue}")

        # Add context if available
        if context:
            final_prompt_parts.append(f"**Context:** Using files from {context.get('clipboard', 'unknown location')}")

        # Add specific requirements based on action type
        requirements = self._get_requirements_for_action(action_type, improved_text, context)
        final_prompt_parts.append(f"**Requirements:** {requirements}")

        # Add desired output format
        output_format = self._get_output_format(action_type)
        final_prompt_parts.append(f"**Output Format:** {output_format}")

        # Add expected outcome
        expected_outcome = self._get_expected_outcome(action_type, main_issue)
        final_prompt_parts.append(f"**Expected Outcome:** {expected_outcome}")

        return "\n\n".join(final_prompt_parts)

    def _extract_main_issue(self, text: str) -> str:
        """Extract the main issue from the text"""

        # Look for error messages
        error_patterns = [
            r'["\']([^"\']+)["\']',  # Quoted error messages
            r'(\w+\s+error)',         # "authentication error"
            r'(\w+\s+not\s+working)',   # "api not working"
            r'(issue\s+in\s+\w+)',      # "issue in login"
        ]

        for pattern in error_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        # Look for main subject
        subject_patterns = [
            r'(\w+)\s+is\s+not\s+working',
            r'(\w+)\s+has\s+issue',
            r'problem\s+in\s+(\w+)',
            r'(\w+)\s+not\s+working'
        ]

        for pattern in subject_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                subject = match.group(1)
                return f"Issue with {subject}"

        return "Unidentified issue"

    def _determine_action_type(self, text: str) -> str:
        """Determine the type of action needed"""

        text_lower = text.lower()

        if any(word in text_lower for word in ['debug', 'diagnose', 'troubleshoot']):
            return 'debug'
        elif any(word in text_lower for word in ['fix', 'resolve', 'solve']):
            return 'fix'
        elif any(word in text_lower for word in ['optimize', 'improve', 'enhance']):
            return 'optimize'
        elif any(word in text_lower for word in ['explain', 'understand', 'clarify']):
            return 'explain'
        elif any(word in text_lower for word in ['create', 'make', 'build']):
            return 'create'
        else:
            return 'general'

    def _get_requirements_for_action(self, action_type: str, text: str, context: Dict) -> str:
        """Get specific requirements based on action type"""

        requirements_map = {
            'debug': [
                "1. Identify the root cause of the issue",
                "2. Provide systematic troubleshooting steps",
                "3. Suggest debugging tools and techniques",
                "4. Include ways to verify the fix"
            ],
            'fix': [
                "1. Provide clear, step-by-step solution",
                "2. Include code examples when applicable",
                "3. Suggest testing procedures",
                "4. Mention potential side effects or considerations"
            ],
            'optimize': [
                "1. Identify performance bottlenecks",
                "2. Suggest specific optimizations",
                "3. Provide measurable improvements",
                "4. Include before/after comparisons when possible"
            ],
            'explain': [
                "1. Explain the concept in simple terms",
                "2. Provide practical examples",
                "3. Include relevant context and use cases",
                "4. Suggest further learning resources"
            ],
            'create': [
                "1. Provide a clear structure and outline",
                "2. Include specific implementation details",
                "3. Suggest best practices and guidelines",
                "4. Mention testing and validation approaches"
            ],
            'general': [
                "1. Provide clear and actionable advice",
                "2. Include relevant examples",
                "3. Suggest next steps or follow-up actions",
                "4. Keep the explanation concise and focused"
            ]
        }

        requirements = requirements_map.get(action_type, requirements_map['general'])

        # Add context-specific requirements
        if context and context.get('clipboard'):
            requirements.insert(0, "1. Analyze the provided files and configurations")

        return "\n".join(requirements)

    def _get_output_format(self, action_type: str) -> str:
        """Get the desired output format"""

        format_map = {
            'debug': "Structured analysis with sections: Problem, Diagnosis, Solution, Verification",
            'fix': "Step-by-step solution with clear actions and examples",
            'optimize': "Optimization plan with before/after comparisons and metrics",
            'explain': "Clear explanation with examples and practical applications",
            'create': "Well-structured plan with implementation details and examples"
        }

        return format_map.get(action_type, "Clear, structured response with actionable advice")

    def _get_expected_outcome(self, action_type: str, issue: str) -> str:
        """Get the expected outcome"""

        outcome_map = {
            'debug': f"Clear understanding of the '{issue}' issue and steps to resolve it",
            'fix': f"Practical solution to fix the '{issue}' issue with implementation guidance",
            'optimize': f"Specific optimizations to improve performance and resolve '{issue}'",
            'explain': f"Clear explanation of '{issue}' with practical understanding",
            'create': f"Well-structured solution to address '{issue}' with implementation details"
        }

        return outcome_map.get(action_type, f"Clear guidance to address the '{issue}' issue")

    def _detect_context(self, text: str) -> bool:
        """Detect if text contains technical context"""
        return any(keyword in text.lower() for keyword in self.context_keywords)

    def _get_improvements_applied(self, original: str, optimized: str) -> List[str]:
        """Get list of improvements applied"""
        improvements = []

        if original.strip().endswith('.'):
            improvements.append("Added proper sentence ending")

        if re.search(r'\bi\s+', original, re.IGNORECASE):
            improvements.append("Capitalized 'I' and improved grammar")

        if len(optimized) > len(original) * 1.5:
            improvements.append("Added context and structure")

        if any(section in optimized for section in ['Problem:', 'Requirements:', 'Expected Outcome:']):
            improvements.append("Added structured prompt format")

        return improvements if improvements else ["Basic text improvements"]