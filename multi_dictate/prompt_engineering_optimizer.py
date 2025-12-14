#!/usr/bin/env python3
"""
Advanced Prompt Engineering Optimizer
Implements structured prompt optimization with templates, references, and best practices
"""

import re
import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptEngineeringOptimizer:
    """
    Advanced prompt engineering system that transforms messy voice input
    into structured, powerful prompts with references and optimization techniques.
    """

    def __init__(self, config: Dict = None):
        """Initialize the prompt engineering optimizer."""
        self.config = config or {}
        self.templates = self._load_templates()
        self.optimization_patterns = self._load_optimization_patterns()
        self.reference_library = self._load_reference_library()
        self._examples = self._load_examples()

    def _load_templates(self) -> Dict:
        """Load structured prompt templates."""
        return {
            "task_context_constrained": {
                "sections": ["Task", "Context", "Constraints", "Output Format"],
                "template": """Task: {task}

Context: {context}

Constraints:
{constraints}

Output format:
{output_format}"""
            },
            "problem_solution": {
                "sections": ["Problem", "Analysis", "Solution Requirements", "Success Criteria", "Implementation Steps"],
                "template": """Problem: {problem}

Analysis: {analysis}

Solution Requirements: {requirements}

Success Criteria: {success_criteria}

Implementation Steps: {steps}"""
            },
            "code_optimization": {
                "sections": ["Current Issue", "Technical Context", "Optimization Goals", "Constraints", "Expected Outcome", "Testing Strategy"],
                "template": """Current Issue: {issue}

Technical Context: {context}

Optimization Goals: {goals}

Constraints: {constraints}

Expected Outcome: {outcome}

Testing Strategy: {testing}"""
            },
            "zero_shot_enhanced": {
                "pattern": "Act as an expert {role}. {task} Context: {context}. Provide {output_type} following best practices.",
                "roles": ["performance engineer", "security specialist", "database architect", "DevOps engineer", "full-stack developer"]
            },
            "few_shot_pattern": {
                "pattern": """I need help with {task_type}. Here are examples:

Example 1: {example1}
Solution: {solution1}

Example 2: {example2}
Solution: {solution2}

Now handle this case: {current_case}
Provide a structured solution following the same pattern.""",
                "examples": self._load_examples()
            }
        }

    def _load_optimization_patterns(self) -> Dict:
        """Load optimization patterns for different domains."""
        return {
            "performance": {
                "keywords": ["slow", "performance", "optimize", "lag", "speed"],
                "role": "performance engineer",
                "techniques": ["profiling", "caching", "lazy loading", "CDN", "database optimization"],
                "constraints": ["backward compatibility", "minimal downtime"],
                "metrics": ["response time", "throughput", "resource usage"]
            },
            "security": {
                "keywords": ["security", "auth", "vulnerability", "secure", "protect"],
                "role": "security specialist",
                "techniques": ["authentication", "authorization", "encryption", "input validation", "security headers"],
                "constraints": ["compliance requirements", "user experience"],
                "metrics": ["security score", "vulnerability count", "compliance status"]
            },
            "database": {
                "keywords": ["database", "query", "slow", "index", "db"],
                "role": "database architect",
                "techniques": ["query optimization", "indexing", "connection pooling", "caching", "schema design"],
                "constraints": ["data integrity", "consistency", "scalability"],
                "metrics": ["query time", "resource usage", "concurrency"]
            },
            "deployment": {
                "keywords": ["deploy", "production", "release", "ci/cd"],
                "role": "DevOps engineer",
                "techniques": ["containerization", "CI/CD", "monitoring", "backup", "rollback"],
                "constraints": ["zero downtime", "scalability", "monitoring"],
                "metrics": ["deployment time", "availability", "rollback success"]
            }
        }

    def _load_reference_library(self) -> Dict:
        """Load reference examples for different scenarios."""
        return {
            "performance_examples": [
                {
                    "input": "database slow optimize",
                    "reference": "Optimize database queries with indexing, query analysis, and connection pooling",
                    "optimized_prompt": """Task: Optimize database performance for slow queries

Context: Database experiencing performance issues with slow response times
- Query response time: >5 seconds
- High CPU usage on database server
- Reports showing degraded user experience

Constraints:
- Maintain data integrity
- Zero downtime during optimization
- Backward compatibility with existing applications

Output Format:
1. Root Cause Analysis
2. Optimization Strategy (prioritized)
3. Implementation Steps with timeline
4. Performance Metrics to Track
5. Risk Mitigation Plan"""
                },
                {
                    "input": "page loading slow fix",
                    "reference": "Frontend performance optimization with lazy loading and caching",
                    "optimized_prompt": """Task: Optimize page loading performance

Context: Web application with slow page load times (>3 seconds)
- User complaints about slow interface
- Analytics showing high bounce rates
- Mobile performance particularly affected

Constraints:
- Preserve all existing functionality
- Improve mobile experience
- Maintain SEO rankings

Output Format:
- Performance Audit Results
- Optimization Priorities
- Implementation Roadmap
- Expected Performance Gains
- Monitoring Strategy"""
                }
            ],
            "security_examples": [
                {
                    "input": "login not secure",
                    "reference": "Implement secure authentication with MFA and proper session management",
                    "optimized_prompt": """Task: Enhance authentication security system

Context: Current login system has security vulnerabilities
- Basic password-only authentication
- No session timeout
- Suspected brute force attempts
- Compliance requirements for data protection

Constraints:
- Must support existing user base
- Meet industry security standards (OAuth 2.0, MFA)
- Maintain usability

Output Format:
- Security Assessment
- Enhanced Authentication Flow
- Implementation Phases
- Security Testing Protocol
- Compliance Checklist"""
                }
            ],
            "deployment_examples": [
                {
                    "input": "deploy production server",
                    "reference": "Production deployment with CI/CD pipeline and monitoring",
                    "optimized_prompt": """Task: Deploy application to production environment

Context: Application ready for production deployment
- Development and testing complete
- Infrastructure requirements identified
- Team prepared for production support

Constraints:
- Zero downtime deployment
- Full monitoring and alerting
- Backup and rollback strategy
- Scalable infrastructure

Output Format:
- Pre-Deployment Checklist
- Deployment Strategy
- Infrastructure Configuration
- Monitoring Setup
- Rollback Procedure
- Post-Deployment Validation"""
                }
            ]
        }

    def _load_examples(self) -> Dict:
        """Load examples for few-shot learning."""
        return {
            "optimization": [
                {
                    "input": "slow database queries",
                    "solution": """Analysis: Database performance bottleneck detected
Optimization: Add indexes on frequently queried columns, implement query caching, optimize join operations
Expected Improvement: 70% reduction in query time"""
                },
                {
                    "input": "memory leak in application",
                    "solution": """Analysis: Memory leak identified in object cleanup
Optimization: Implement proper disposal patterns, fix circular references, add memory monitoring
Expected Improvement: Stable memory usage over time"""
                }
            ]
        }

    def detect_intent_and_domain(self, input_text: str) -> Tuple[str, str]:
        """Detect user intent and domain from messy input."""
        text_lower = input_text.lower()

        # Check for question/analysis intent
        if any(word in text_lower for word in ["why", "how", "what", "analyze", "explain", "review"]):
            intent = "analysis"
        elif any(word in text_lower for word in ["fix", "solve", "debug", "optimize", "improve", "enhance"]):
            intent = "optimization"
        elif any(word in text_lower for word in ["implement", "add", "create", "build", "deploy"]):
            intent = "implementation"
        else:
            intent = "general"

        # Detect domain
        domain = "general"
        for domain_name, pattern in self.optimization_patterns.items():
            if any(keyword in text_lower for keyword in pattern["keywords"]):
                domain = domain_name
                break

        return intent, domain

    def extract_technical_context(self, input_text: str, clipboard: str = None) -> Dict:
        """Extract technical context from input and clipboard."""
        context = {
            "technologies": [],
            "issues": [],
            "goals": [],
            "constraints": [],
            "metrics": []
        }

        # Ensure clipboard is string
        if isinstance(clipboard, dict):
            clipboard = str(clipboard.get('clipboard', ''))
        elif clipboard is None:
            clipboard = ''

        # Enhanced path detection and analysis
        if clipboard:
            project_context = self._analyze_clipboard_path(clipboard)
            if project_context:
                context.update(project_context)

        # Technology detection
        tech_patterns = {
            "database": r'\b(mysql|postgresql|mongodb|redis|database|db|sql|nosql)\b',
            "frontend": r'\b(react|vue|angular|javascript|typescript|css|html)\b',
            "backend": r'\b(nodejs|python|java|spring|django|flask|api|rest)\b',
            "cloud": r'\b(aws|azure|gcp|docker|kubernetes|serverless)\b',
            "security": r'\b(auth|oauth|jwt|ssl|https|security|vulnerability)\b'
        }

        for tech, pattern in tech_patterns.items():
            if re.search(pattern, input_text.lower()) or (clipboard and re.search(pattern, clipboard.lower())):
                context["technologies"].append(tech)

        # Add technologies detected from path analysis
        if "technologies_from_path" in context:
            context["technologies"].extend(context["technologies_from_path"])
            # Remove duplicates while preserving order
            seen = set()
            context["technologies"] = [x for x in context["technologies"] if not (x in seen or seen.add(x))]

        # Issue detection
        issue_patterns = {
            "performance": r'\b(slow|lag|performance|optimize|bottleneck)\b',
            "security": r'\b(security|vulnerability|auth|hack|breach)\b',
            "functionality": r'\b(broken|error|bug|not working|fail)\b',
            "scalability": r'\b(scale|load|traffic|concurrent)\b'
        }

        for issue, pattern in issue_patterns.items():
            if re.search(pattern, input_text.lower()):
                context["issues"].append(issue)

        return context

    def select_optimization_technique(self, intent: str, domain: str, complexity: int) -> str:
        """Select the best optimization technique based on intent, domain, and complexity."""
        if complexity >= 3:
            return "few_shot_pattern"
        elif intent == "analysis":
            return "zero_shot_enhanced"
        elif domain in ["performance", "security", "database"]:
            return "code_optimization"
        else:
            return "task_context_constrained"

    def enhance_prompt_with_references(self, optimized_prompt: str, domain: str, intent: str) -> str:
        """Enhance prompt with relevant references and examples."""
        references = []

        # Add domain-specific references
        if domain in self.reference_library:
            domain_examples = self.reference_library[f"{domain}_examples"]
            if domain_examples:
                # Select most relevant example
                best_example = domain_examples[0]  # Simplified selection
                references.append(f"Reference Example: {best_example['reference']}")

        # Add optimization techniques
        if domain in self.optimization_patterns:
            pattern = self.optimization_patterns[domain]
            techniques = ", ".join(pattern["techniques"][:3])  # Top 3 techniques
            references.append(f"Recommended Techniques: {techniques}")

        # Add success criteria
        if domain in self.optimization_patterns:
            metrics = self.optimization_patterns[domain]["metrics"]
            criteria = ", ".join(metrics[:3])
            references.append(f"Success Criteria: Improve {criteria}")

        if references:
            enhanced = optimized_prompt + "\n\n" + "\n".join(references)
            return enhanced

        return optimized_prompt

    def _analyze_clipboard_path(self, clipboard: str) -> Optional[Dict]:
        """Analyze clipboard content for file paths and extract project context."""
        import os

        # Check if clipboard contains a file path
        path_indicators = ['/', '\\', '~/', './', '../', '/home/', '/Users/', 'C:']
        if not any(indicator in clipboard for indicator in path_indicators):
            return None

        # Clean and normalize path
        clipboard = clipboard.strip()
        if clipboard.startswith('"') and clipboard.endswith('"'):
            clipboard = clipboard[1:-1]

        # Extract path patterns
        path_patterns = [
            r'([~/]?[^,\s"\']+)',  # Basic path
            r'([/][^,\s"\']+)',   # Absolute path
            r'(\.\/[^,\s"\']+)',   # Relative path
        ]

        for pattern in path_patterns:
            match = re.search(pattern, clipboard)
            if match:
                path = match.group(1)
                break
        else:
            path = clipboard

        # Analyze the path
        context = {
            "target_path": path,
            "project_info": {},
            "file_type": None,
            "technologies_from_path": [],
            "project_structure": {}
        }

        try:
            # Expand user path
            if path.startswith('~/'):
                path = os.path.expanduser(path)

            # Extract project name from path
            path_parts = path.replace('\\', '/').split('/')
            if len(path_parts) > 1:
                potential_project_names = [part for part in path_parts[-3:] if part and not part.startswith('.')]
                if potential_project_names:
                    context["project_info"]["name"] = potential_project_names[-1]
                    context["project_info"]["possible_names"] = potential_project_names

            # Detect file type if it's a file
            if '.' in path.split('/')[-1]:
                file_ext = path.split('.')[-1].lower()
                context["file_type"] = file_ext

                # Map file extensions to technologies
                tech_mapping = {
                    'py': 'python',
                    'js': 'javascript',
                    'ts': 'typescript',
                    'jsx': 'react',
                    'tsx': 'react/typescript',
                    'vue': 'vue',
                    'java': 'java',
                    'go': 'golang',
                    'rs': 'rust',
                    'cpp': 'cpp',
                    'c': 'c',
                    'cs': 'csharp',
                    'php': 'php',
                    'rb': 'ruby',
                    'html': 'html',
                    'css': 'css',
                    'scss': 'sass/scss',
                    'sql': 'sql',
                    'json': 'json',
                    'yaml': 'yaml',
                    'yml': 'yaml',
                    'xml': 'xml',
                    'md': 'markdown',
                    'dockerfile': 'docker',
                    'sh': 'shell/bash',
                    'bash': 'shell/bash'
                }

                if file_ext in tech_mapping:
                    context["technologies_from_path"].append(tech_mapping[file_ext])

            # Detect project type from path patterns
            path_lower = path.lower()

            # Web framework detection
            if any(indicator in path_lower for indicator in ['react', 'next', 'gatsby', 'vue', 'angular', 'svelte']):
                context["technologies_from_path"].append('frontend/web')

            # Backend framework detection
            if any(indicator in path_lower for indicator in ['django', 'flask', 'fastapi', 'express', 'spring', 'rails', 'laravel']):
                context["technologies_from_path"].append('backend/framework')

            # Database indicators
            if any(indicator in path_lower for indicator in ['models', 'migrations', 'database', 'db', 'sql', 'nosql']):
                context["technologies_from_path"].append('database')

            # DevOps/Infrastructure
            if any(indicator in path_lower for indicator in ['docker', 'kubernetes', 'k8s', 'deploy', 'ci', 'cd', 'terraform']):
                context["technologies_from_path"].append('devops')

            # Testing
            if any(indicator in path_lower for indicator in ['test', 'spec', '__tests__', 'tests', 'e2e', 'integration']):
                context["technologies_from_path"].append('testing')

            # Configuration/Build tools
            if any(indicator in path_lower for indicator in ['config', 'webpack', 'vite', 'parcel', 'build', 'compile']):
                context["technologies_from_path"].append('build-tools')

            # Remove duplicates
            context["technologies_from_path"] = list(set(context["technologies_from_path"]))

        except Exception as e:
            logger.debug(f"Error analyzing path: {e}")

        return context if any(context.values()) else None

    def select_optimization_technique(self, intent: str, domain: str, complexity: int) -> str:
        """
        Dynamically select the best prompt engineering strategy.
        Maps intent + complexity -> Advanced Techniques (CoT, etc.)
        """
        # high complexity analysis -> Chain of Thought
        if complexity >= 4 and domain == "analysis":
            return "chain_of_thought"
        
        # coding tasks with medium complexity -> Few Shot (Code)
        elif domain == "code_generation" and complexity >= 3:
            return "few_shot_code"
            
        # explanation or learning -> Role Prompting (Teacher/Expert)
        elif intent == "explanation":
            return "role_prompting"

        # debugging -> Systematic Debug Protocol
        elif intent == "debugging":
            return "debug_protocol"

        # default mappings
        if complexity <= 2:
            return "zero_shot_enhanced"
        elif complexity <= 4:
            return "few_shot_pattern"
        else:
            return "task_context_constrained"

        # Add complexity for technical terms
        technical_terms = len(set(context["technologies"]) | set(context["issues"]))
        if technical_terms > 3:
            complexity += 1

        # Add complexity for request length
        if len(input_text.split()) > 20:
            complexity += 1

        return min(complexity, 5)

    def construct_system_prompt_request(self, voice_input: str, clipboard: str = None, past_patterns: str = None) -> str:
        """
        Constructs the 'Voice-First' Meta-Prompt.
        This instructs the AI to treat the User Voice as the PRIMARY DIRECTIVE (The Captain),
        and use Clipboard/History only as supporting context (The Crew).
        """
        system_instruction = f"""You are an Expert Prompt Engineer and Solution Architect.

### 1. PRIMARY DIRECTIVE (THE CAPTAIN'S ORDER)
**Voice Command:** "{voice_input}"

Your Absolute Priority:
1. Understand the Intent of the Voice Command above.
2. If the Voice Command contradicts any Context below, **OBEY THE VOICE COMMAND**.
3. If the user asks to "Ignore docs" or "Use a different method", do exactly that.

### 2. SUPPORTING CONTEXT (THE CREW)
**Clipboard Content:**
{clipboard[:3000] + '... (truncated)' if clipboard and len(clipboard) > 3000 else (clipboard or "No clipboard context.")}

**Relevant Past Solutions:**
{past_patterns or "No relevant past solutions found."}

### 3. YOUR TASK
Based on the PRIMARY DIRECTIVE, generate a high-quality, structured response.
*   **Filter the Context**: Only use clipboard parts relevant to the Voice Command. Discard noise.
*   **Apply Best Practices**: Use the Past Solutions if they help the Voice Command, otherwise ignore them.
*   **Output**: Write the final, optimized prompt or code solution now.

**GOAL:** Transform the Voice Command into a perfect execution plan.
"""
        return system_instruction

    def optimize_prompt(self, raw_input: str, clipboard: str = None) -> Dict:
        """
        Main optimization pipeline that transforms messy input into structured prompt.
        """
        start_time = time.time()

        logger.info(f"🚀 Starting prompt optimization for: {raw_input[:50]}...")
        # ... rest of existing logic ...

        # Step 1: Clean and normalize input
        cleaned_input = self._clean_input(raw_input)

        # Step 2: Detect intent and domain
        intent, domain = self.detect_intent_and_domain(cleaned_input)
        logger.info(f"📊 Intent: {intent}, Domain: {domain}")

        # Step 3: Extract technical context
        context = self.extract_technical_context(cleaned_input, clipboard)

        # Step 4: Calculate complexity
        complexity = self.calculate_complexity(cleaned_input, context)

        # Step 5: Select optimization technique
        technique = self.select_optimization_technique(intent, domain, complexity)
        logger.info(f"🎯 Using technique: {technique} (complexity: {complexity})")

        # Step 6: Generate structured prompt
        structured_prompt = self._generate_structured_prompt(
            cleaned_input, intent, domain, context, technique
        )

        # Step 7: Enhance with references
        enhanced_prompt = self.enhance_prompt_with_references(structured_prompt, domain, intent)

        # Step 8: Add prompt engineering best practices
        final_prompt = self._add_engineering_best_practices(enhanced_prompt, intent, domain)

        optimization_time = time.time() - start_time

        result = {
            "original_input": raw_input,
            "cleaned_input": cleaned_input,
            "optimized_prompt": final_prompt,
            "intent": intent,
            "domain": domain,
            "complexity": complexity,
            "technique_used": technique,
            "context": context,
            "optimization_time": optimization_time,
            "improvement_ratio": len(final_prompt) / max(len(raw_input), 1)
        }

        logger.info(f"✅ Prompt optimization complete in {optimization_time:.2f}s")
        logger.info(f"📈 Improvement ratio: {result['improvement_ratio']:.1f}x")

        return result

    def _clean_input(self, raw_input: str) -> str:
        """Clean and normalize the raw input."""
        # Remove filler words
        filler_words = ["um", "uh", "like", "you know", "actually", "basically"]
        cleaned = raw_input.lower()

        for filler in filler_words:
            cleaned = cleaned.replace(filler, "")

        # Fix common speech-to-text issues
        cleaned = cleaned.replace("i have", "I have")
        cleaned = cleaned.replace("im", "I'm")
        cleaned = cleaned.replace("dont", "don't")
        cleaned = cleaned.replace("wanna", "want to")

        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]

        return cleaned.strip()

    def calculate_complexity(self, input_text: str, context: Dict) -> int:
        """Calculate complexity score (1-5) of the request."""
        complexity = 1
        if len(context.get("technologies", [])) > 2: complexity += 1
        if len(input_text.split()) > 20: complexity += 1
        return min(complexity, 5)

    def _generate_structured_prompt(self, input_text: str, intent: str, domain: str,
                                   context: Dict, technique: str) -> str:
        """Generate structured prompt using selected technique."""

        if technique == "chain_of_thought":
             return self._generate_cot_prompt(input_text, context)
        elif technique == "few_shot_code":
             return self._generate_few_shot_code_prompt(input_text, context)
        elif technique == "role_prompting":
             return self._generate_role_prompt(input_text, domain, context)
        elif technique == "debug_protocol":
             return self._generate_debug_protocol_prompt(input_text, context)
        
        # Original strategies
        elif technique == "zero_shot_enhanced":
            return self._generate_zero_shot_prompt(input_text, intent, domain, context)
        elif technique == "few_shot_pattern":
            return self._generate_few_shot_prompt(input_text, intent, domain, context)
        elif technique == "code_optimization":
            return self._generate_code_optimization_prompt(input_text, intent, domain, context)
        else:
            return self._generate_task_context_prompt(input_text, intent, domain, context)

    # --- NEW STRATEGY GENERATORS ---

    def _generate_cot_prompt(self, task: str, context: Dict) -> str:
        return f"""You are an Expert Analyst using Chain of Thought reasoning.

TASK: {task}
CONTEXT: {self._format_context(context)}

Think through this step-by-step:
1. First, analyze the input data and identify key components.
2. Second, evaluate potential causes or implications.
3. Third, propose a solution based on the evaluation.
4. Finally, synthesize the answer.

Let's think step by step:
"""

    def _generate_few_shot_code_prompt(self, task: str, context: Dict) -> str:
        return f"""You are a Senior Software Engineer.
        
TASK: {task}
CONTEXT: {self._format_context(context)}

Effectively use the following pattern:

Example Input: "Create a React Button"
Example Output:
```jsx
import React from 'react';
export const Button = ({{ label, onClick }}) => (
  <button onClick={{onClick}} className="px-4 py-2 bg-blue-500 text-white rounded">
    {{label}}
  </button>
);
```

Now, generate the code for the task above:
"""

    def _generate_role_prompt(self, task: str, domain: str, context: Dict) -> str:
        return f"""Act as a World-Class Expert in {domain}.
        
I want you to explain or solve: {task}

Context: {self._format_context(context)}

Use your deep expertise to provide a clear, authoritative answer.
"""

    def _generate_debug_protocol_prompt(self, task: str, context: Dict) -> str:
        return f"""Debug Protocol Initiated.

SYMPTOM: {task}
ENVIRONMENT: {self._format_context(context)}

Execute the following procedure:
1. ISOLATE the root cause.
2. REPRODUCE the issue mentally.
3. FIX validity check.
4. PROVIDE the corrected code.
"""

    def _generate_zero_shot_prompt(self, input_text: str, intent: str, domain: str, context: Dict) -> str:
        """Generate zero-shot enhanced prompt."""
        if domain in self.optimization_patterns:
            role = self.optimization_patterns[domain]["role"]
        else:
            role = "expert consultant"

        prompt = f"Act as an expert {role}.\n\n"
        prompt += f"Task: {input_text}\n\n"

        # Add project context from clipboard path analysis
        if "target_path" in context:
            prompt += f"Target Project: {context['target_path']}\n"

        if "project_info" in context and context["project_info"]:
            project_info = context["project_info"]
            if "name" in project_info:
                prompt += f"Project Name: {project_info['name']}\n"
            if "file_type" in context:
                prompt += f"File Type: {context['file_type']}\n"

        if context["technologies"]:
            prompt += f"Technical Context: Working with {', '.join(context['technologies'])}\n"

        if context["issues"]:
            prompt += f"Issues to Address: {', '.join(context['issues'])}\n"

        prompt += "\nProvide a comprehensive solution following industry best practices."
        prompt += "\nInclude specific implementation steps and success metrics."

        return prompt

    def _generate_few_shot_prompt(self, input_text: str, intent: str, domain: str, context: Dict) -> str:
        """Generate few-shot learning prompt."""
        examples = self._examples.get("optimization", [])[:2]

        prompt = "I need help with technical optimization tasks. Here are examples:\n\n"

        for i, example in enumerate(examples, 1):
            prompt += f"Example {i}: {example['input']}\n"
            prompt += f"Solution: {example['solution']}\n\n"

        prompt += f"Now handle this case: {input_text}\n"
        prompt += "Provide a structured solution following the same pattern."

        return prompt

    def _generate_code_optimization_prompt(self, input_text: str, intent: str, domain: str, context: Dict) -> str:
        """Generate code optimization specific prompt."""
        template = self.templates["code_optimization"]["template"]

        return template.format(
            issue=input_text,
            context=self._format_context(context),
            goals=self._generate_goals(domain, context),
            constraints=self._generate_constraints(domain),
            outcome=self._generate_expected_outcome(domain),
            testing=self._generate_testing_strategy(domain)
        )

    def _generate_task_context_prompt(self, input_text: str, intent: str, domain: str, context: Dict) -> str:
        """Generate task-context-constraints format prompt."""
        template = self.templates["task_context_constrained"]["template"]

        return template.format(
            task=input_text,
            context=self._format_context(context),
            constraints=self._generate_constraints(domain),
            output_format=self._generate_output_format(intent, domain)
        )

    def _format_context(self, context: Dict) -> str:
        """Format context dictionary into readable text."""
        parts = []

        # Add project context from clipboard path analysis
        if "target_path" in context:
            parts.append(f"Target Project: {context['target_path']}")

        if "project_info" in context and context["project_info"]:
            project_info = context["project_info"]
            if "name" in project_info:
                parts.append(f"Project Name: {project_info['name']}")
            if "possible_names" in project_info:
                parts.append(f"Related Project Components: {', '.join(project_info['possible_names'])}")

        if "file_type" in context:
            parts.append(f"File Type: {context['file_type']}")

        if context.get("technologies"):
            parts.append(f"Technologies: {', '.join(context['technologies'])}")

        if context.get("issues"):
            parts.append(f"Issues: {', '.join(context['issues'])}")

        if context.get("goals"):
            parts.append(f"Goals: {', '.join(context['goals'])}")

        return "\n".join(parts) if parts else "No specific context provided"

    def _generate_goals(self, domain: str, context: Dict) -> str:
        """Generate optimization goals based on domain."""
        goal_map = {
            "performance": "Reduce response time, improve throughput, optimize resource usage",
            "security": "Enhance security posture, reduce vulnerabilities, ensure compliance",
            "database": "Optimize query performance, improve data integrity, scale efficiently",
            "deployment": "Achieve zero-downtime deployment, ensure reliability, implement monitoring"
        }

        return goal_map.get(domain, "Improve system performance and reliability")

    def _generate_constraints(self, domain: str) -> str:
        """Generate constraints based on domain."""
        if domain in self.optimization_patterns:
            constraints = self.optimization_patterns[domain]["constraints"]
            return "\n".join(f"- {c}" for c in constraints)

        return "- Maintain backward compatibility\n- Ensure security\n- Preserve functionality"

    def _generate_expected_outcome(self, domain: str) -> str:
        """Generate expected outcome description."""
        outcome_map = {
            "performance": "50-80% improvement in response time, reduced resource usage",
            "security": "Reduced security vulnerabilities, compliance with standards",
            "database": "Improved query performance, better scalability",
            "deployment": "Successful production deployment with monitoring"
        }

        return outcome_map.get(domain, "Improved system performance and reliability")

    def _generate_testing_strategy(self, domain: str) -> str:
        """Generate testing strategy for the domain."""
        strategies = {
            "performance": "Load testing, performance profiling, benchmarking",
            "security": "Security audits, penetration testing, vulnerability scanning",
            "database": "Query performance testing, load testing, data integrity checks",
            "deployment": "Staging testing, rollback testing, monitoring validation"
        }

        return strategies.get(domain, "Unit testing, integration testing, user acceptance testing")

    def _generate_output_format(self, intent: str, domain: str) -> str:
        """Generate appropriate output format based on intent and domain."""
        base_format = """1. Analysis Summary
2. Recommended Solution
3. Implementation Steps (with priorities)
4. Risk Assessment
5. Success Metrics
6. Testing Recommendations"""

        if intent == "analysis":
            base_format = """1. Current State Analysis
2. Identified Issues
3. Root Cause Analysis
4. Impact Assessment
5. Recommendations"""
        elif intent == "implementation":
            base_format = """1. Implementation Plan
2. Step-by-Step Instructions
3. Resource Requirements
4. Timeline
5. Validation Criteria"""

        return base_format

    def _add_engineering_best_practices(self, prompt: str, intent: str, domain: str) -> str:
        """Add prompt engineering best practices to the final prompt."""
        enhancements = []

        # Add specificity requirements
        enhancements.append("Provide specific, actionable steps rather than general advice.")

        # Add reference requirement
        enhancements.append("Include references to best practices or industry standards where applicable.")

        # Add measurement requirement
        enhancements.append("Define clear metrics to measure success.")

        # Add domain-specific enhancements
        if domain == "performance":
            enhancements.append("Include benchmark comparisons and expected performance improvements.")
        elif domain == "security":
            enhancements.append("Reference relevant security standards (OWASP, NIST, etc.).")
        elif domain == "deployment":
            enhancements.append("Include rollback procedures and monitoring setup.")

        # Add final instructions
        enhancements.append("Think step-by-step before responding.")
        enhancements.append("If information is missing, ask for clarification rather than making assumptions.")

        return prompt + "\n\n" + "\n".join(f"- {e}" for e in enhancements)