#!/usr/bin/env python3
"""
Complete 9-Stage Prompt Generation Pipeline
Implements step-by-step prompt optimization that works with any AI model.
"""

import re
import json
import time
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Types of tasks the pipeline can handle."""
    CODING = "coding"
    DEBUGGING = "debugging"
    WRITING = "writing"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    OPTIMIZATION = "optimization"
    EXPLANATION = "explanation"

class OutputType(Enum):
    """Types of expected outputs."""
    CODE = "code"
    EXPLANATION = "explanation"
    STEPS = "steps"
    DIAGRAM = "diagram"
    FILE = "file"
    MARKDOWN = "markdown"
    JSON = "json"
    LIST = "list"

class UrgencyLevel(Enum):
    """Urgency/Depth levels."""
    QUICK = "quick"
    DETAILED = "detailed"
    EXPERT = "expert"

class PromptSkeleton(Enum):
    """Pre-defined prompt structures."""
    EXPLAIN_STEPS = "explain_steps"
    THINK_DECIDE_ACT = "think_decide_act"
    ANALYZE_FIX_VALIDATE = "analyze_fix_validate"
    PLAN_EXECUTE_REVIEW = "plan_execute_review"
    COMPARE_RECOMMEND = "compare_recommend"
    DEBUG_SOLVE = "debug_solve"
    OPTIMIZE_ANALYZE = "optimize_analyze"

@dataclass
class RawIntent:
    """Stage 0: Raw User Intent."""
    text: str
    language: str = "en"
    length: int = 0
    ambiguity_level: float = 0.0
    confidence: float = 0.0

@dataclass
class IntentClarification:
    """Stage 1: Clarified Intent."""
    task_type: TaskType
    domain: str
    depth: UrgencyLevel
    output_format: OutputType
    confidence: float = 0.0

@dataclass
class Constraints:
    """Stage 2: Extracted Constraints."""
    tech_stack: List[str] = field(default_factory=list)
    language: str = "en"
    constraints: List[str] = field(default_factory=list)
    style_preferences: List[str] = field(default_factory=list)
    forbidden_actions: List[str] = field(default_factory=list)

@dataclass
class ContextInjection:
    """Stage 3: Injected Context."""
    context_sources: List[str] = field(default_factory=list)
    key_facts: List[str] = field(default_factory=list)
    project_context: Dict = field(default_factory=dict)
    relevant_files: List[str] = field(default_factory=list)

@dataclass
class QualityGateResult:
    """Stage 8: Quality Gate Result."""
    passed: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    score: float = 0.0
    recommendations: List[str] = field(default_factory=list)

@dataclass
class PipelineResult:
    """Complete pipeline result."""
    final_prompt: str
    stage_results: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    quality_score: float = 0.0
    iterations: int = 0
    success: bool = False

class PromptGenerationPipeline:
    """Complete 9-stage prompt generation pipeline."""

    def __init__(self):
        self.skeleton_library = self._initialize_skeletons()
        self.quality_thresholds = {
            "min_confidence": 0.6,
            "max_ambiguity": 0.5,
            "min_constraints": 2,
            "max_context_items": 10
        }

    def _initialize_skeletons(self) -> Dict[PromptSkeleton, Dict]:
        """Initialize prompt skeleton templates."""
        return {
            PromptSkeleton.EXPLAIN_STEPS: {
                "role": "expert consultant",
                "structure": [
                    "Problem Understanding",
                    "Step-by-Step Explanation",
                    "Key Insights",
                    "Practical Examples",
                    "Summary"
                ],
                "reasoning": "Explain concepts clearly with practical examples"
            },
            PromptSkeleton.THINK_DECIDE_ACT: {
                "role": "strategic analyst",
                "structure": [
                    "Analysis & Thinking",
                    "Decision Rationale",
                    "Action Plan",
                    "Risk Assessment",
                    "Success Metrics"
                ],
                "reasoning": "Think carefully, decide logically, act deliberately"
            },
            PromptSkeleton.ANALYZE_FIX_VALIDATE: {
                "role": "technical expert",
                "structure": [
                    "Current State Analysis",
                    "Issue Identification",
                    "Solution Design",
                    "Implementation Strategy",
                    "Validation Checklist"
                ],
                "reasoning": "Analyze systematically, fix precisely, validate thoroughly"
            },
            PromptSkeleton.PLAN_EXECUTE_REVIEW: {
                "role": "project manager",
                "structure": [
                    "Project Planning",
                    "Execution Steps",
                    "Resource Requirements",
                    "Timeline & Milestones",
                    "Review & Optimization"
                ],
                "reasoning": "Plan carefully, execute systematically, review continuously"
            },
            PromptSkeleton.DEBUG_SOLVE: {
                "role": "debugging specialist",
                "structure": [
                    "Problem Description",
                    "Root Cause Analysis",
                    "Solution Options",
                    "Implementation",
                    "Testing & Verification"
                ],
                "reasoning": "Debug methodically, solve efficiently, test thoroughly"
            },
            PromptSkeleton.OPTIMIZE_ANALYZE: {
                "role": "performance engineer",
                "structure": [
                    "Performance Analysis",
                    "Bottleneck Identification",
                    "Optimization Strategies",
                    "Implementation Plan",
                    "Measurement & Validation"
                ],
                "reasoning": "Analyze performance, optimize strategically, measure results"
            }
        }

    def process_through_pipeline(self, user_input: str, context: Dict = None,
                                max_iterations: int = 3) -> PipelineResult:
        """
        Process user input through the complete 9-stage pipeline.

        Args:
            user_input: Raw user input (text, voice transcription, etc.)
            context: Additional context (clipboard, files, etc.)
            max_iterations: Maximum quality gate iterations

        Returns:
            PipelineResult with optimized prompt and metadata
        """
        start_time = time.time()
        logger.info("🚀 Starting 9-stage prompt generation pipeline")

        stage_results = {}
        iteration = 0

        try:
            # Stage 0: Raw Intent
            raw_intent = self._stage_0_raw_intent(user_input)
            stage_results["raw_intent"] = raw_intent

            # Stage 0.5: Intelligent Prompt Merging (NEW!)
            merged_intent = self._stage_0_5_prompt_merging(raw_intent, context)
            stage_results["merged_intent"] = merged_intent
            raw_intent = merged_intent  # Use merged intent for remaining stages

            # Quality Gate Loop (Stages 1-8)
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"🔄 Pipeline iteration {iteration}")

                # Stage 1: Intent Clarification
                intent_clarification = self._stage_1_intent_clarification(raw_intent, context)
                stage_results["intent_clarification"] = intent_clarification

                # Stage 2: Constraint Extraction
                constraints = self._stage_2_constraint_extraction(raw_intent, context)
                stage_results["constraints"] = constraints

                # Stage 3: Context Injection
                context_injection = self._stage_3_context_injection(context, intent_clarification)
                stage_results["context_injection"] = context_injection

                # Stage 4: Prompt Skeleton Selection
                skeleton = self._stage_4_skeleton_selection(intent_clarification, constraints)
                stage_results["skeleton"] = skeleton

                # Stage 5: Instruction Engineering
                instructions = self._stage_5_instruction_engineering(
                    intent_clarification, constraints, skeleton)
                stage_results["instructions"] = instructions

                # Stage 6: Output Specification
                output_spec = self._stage_6_output_specification(
                    intent_clarification, constraints)
                stage_results["output_spec"] = output_spec

                # Stage 7: Prompt Assembly
                assembled_prompt = self._stage_7_prompt_assembly(
                    raw_intent, intent_clarification, constraints,
                    context_injection, skeleton, instructions, output_spec)

                # Stage 8: Quality Gate
                quality_result = self._stage_8_quality_gate(
                    raw_intent, assembled_prompt, intent_clarification, constraints)

                if quality_result.passed:
                    # Quality gate passed, proceed to execution
                    stage_results["assembled_prompt"] = assembled_prompt
                    stage_results["quality_gate"] = quality_result
                    break
                else:
                    # Quality gate failed, adjust and retry
                    logger.warning(f"⚠️ Quality gate failed: {quality_result.issues}")
                    # Adjust intent based on quality feedback
                    raw_intent = self._adjust_intent_based_on_quality(
                        raw_intent, quality_result)
                    stage_results[f"quality_gate_attempt_{iteration}"] = quality_result

            # Stage 9: Prepare for execution (set up feedback capture)
            execution_context = self._stage_9_execution_prep(
                assembled_prompt, stage_results)
            stage_results["execution_context"] = execution_context

            processing_time = time.time() - start_time
            logger.info(f"✅ Pipeline completed in {processing_time:.2f}s, {iteration} iterations")

            return PipelineResult(
                final_prompt=assembled_prompt,
                stage_results=stage_results,
                processing_time=processing_time,
                quality_score=quality_result.score if quality_result else 0.0,
                iterations=iteration,
                success=True
            )

        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            return PipelineResult(
                final_prompt=user_input,
                stage_results=stage_results,
                processing_time=time.time() - start_time,
                quality_score=0.0,
                iterations=iteration,
                success=False
            )

    def _stage_0_raw_intent(self, user_input: str) -> RawIntent:
        """Stage 0: Capture and analyze raw user intent."""
        logger.info("📝 Stage 0: Raw Intent Capture")

        # Analyze input characteristics
        text = user_input.strip()
        word_count = len(text.split())

        # Detect language (simple detection)
        language = self._detect_language(text)

        # Calculate ambiguity level
        ambiguity = self._calculate_ambiguity_level(text)

        # Calculate confidence based on clarity
        confidence = max(0.1, 1.0 - ambiguity)

        logger.info(f"   Language: {language}, Length: {word_count} words, Ambiguity: {ambiguity:.2f}")

        return RawIntent(
            text=text,
            language=language,
            length=word_count,
            ambiguity_level=ambiguity,
            confidence=confidence
        )

    def _stage_1_intent_clarification(self, raw_intent: RawIntent,
                                     context: Dict = None) -> IntentClarification:
        """Stage 1: Clarify intent and detect task characteristics."""
        logger.info("🎯 Stage 1: Intent Clarification")

        text = raw_intent.text.lower()

        # Detect task type
        task_type = self._detect_task_type(text, context)

        # Detect domain
        domain = self._detect_domain(text, context)

        # Determine depth/urgency
        depth = self._determine_depth(text, context)

        # Detect expected output format
        output_format = self._detect_output_format(text, task_type)

        logger.info(f"   Task: {task_type.value}, Domain: {domain}, Depth: {depth.value}")

        return IntentClarification(
            task_type=task_type,
            domain=domain,
            depth=depth,
            output_format=output_format,
            confidence=0.8  # Would be refined with ML in production
        )

    def _stage_2_constraint_extraction(self, raw_intent: RawIntent,
                                      context: Dict = None) -> Constraints:
        """Stage 2: Extract constraints and preferences."""
        logger.info("⚖️ Stage 2: Constraint Extraction")

        text = raw_intent.text + " " + str(context.get('clipboard', '') if context else '')

        # Extract tech stack
        tech_stack = self._extract_tech_stack(text, context)

        # Extract explicit constraints
        constraints = self._extract_constraints(text)

        # Extract style preferences
        style_preferences = self._extract_style_preferences(text)

        # Extract forbidden actions
        forbidden_actions = self._extract_forbidden_actions(text)

        logger.info(f"   Tech Stack: {tech_stack}, Constraints: {len(constraints)}")

        return Constraints(
            tech_stack=tech_stack,
            constraints=constraints,
            style_preferences=style_preferences,
            forbidden_actions=forbidden_actions
        )

    def _stage_3_context_injection(self, context: Dict = None,
                                  intent_clarification: IntentClarification = None) -> ContextInjection:
        """Stage 3: Inject relevant context with filtering."""
        logger.info("📚 Stage 3: Context Injection")

        context_sources = []
        key_facts = []
        project_context = {}
        relevant_files = []

        if context:
            # Extract project path context
            clipboard = context.get('clipboard', '')
            if clipboard and any(indicator in clipboard for indicator in ['/', '\\', 'project']):
                # Parse file path
                path_parts = clipboard.replace('\\', '/').split('/')
                if len(path_parts) > 1:
                    project_name = path_parts[-1] if path_parts[-1] else path_parts[-2]

                    project_context = {
                        "target_path": clipboard,
                        "project_name": project_name,
                        "context_type": "file_path"
                    }

                    key_facts.append(f"Working with project: {project_name}")
                    key_facts.append(f"Target location: {clipboard}")

                    context_sources.append("clipboard_path")

            # Extract domain-specific context
            if intent_clarification:
                if intent_clarification.domain == "api":
                    key_facts.append("API/Backend development context")
                elif intent_clarification.domain == "frontend":
                    key_facts.append("Frontend/UI development context")
                elif intent_clarification.domain == "database":
                    key_facts.append("Database design context")

        # Filter context by relevance
        if len(key_facts) > self.quality_thresholds["max_context_items"]:
            key_facts = key_facts[:self.quality_thresholds["max_context_items"]]

        logger.info(f"   Context sources: {len(context_sources)}, Key facts: {len(key_facts)}")

        return ContextInjection(
            context_sources=context_sources,
            key_facts=key_facts,
            project_context=project_context,
            relevant_files=relevant_files
        )

    def _stage_4_skeleton_selection(self, intent_clarification: IntentClarification,
                                  constraints: Constraints) -> PromptSkeleton:
        """Stage 4: Select appropriate prompt skeleton."""
        logger.info("🏗️ Stage 4: Prompt Skeleton Selection")

        # Selection logic based on task type and domain
        if intent_clarification.task_type == TaskType.DEBUGGING:
            skeleton = PromptSkeleton.DEBUG_SOLVE
        elif intent_clarification.task_type == TaskType.OPTIMIZATION:
            skeleton = PromptSkeleton.OPTIMIZE_ANALYZE
        elif intent_clarification.task_type == TaskType.PLANNING:
            skeleton = PromptSkeleton.PLAN_EXECUTE_REVIEW
        elif intent_clarification.task_type == TaskType.ANALYSIS:
            skeleton = PromptSkeleton.ANALYZE_FIX_VALIDATE
        elif intent_clarification.task_type == TaskType.CODING:
            skeleton = PromptSkeleton.THINK_DECIDE_ACT
        else:
            skeleton = PromptSkeleton.EXPLAIN_STEPS

        logger.info(f"   Selected skeleton: {skeleton.value}")

        return skeleton

    def _stage_5_instruction_engineering(self, intent_clarification: IntentClarification,
                                       constraints: Constraints,
                                       skeleton: PromptSkeleton) -> Dict:
        """Stage 5: Engineering specific instructions."""
        logger.info("🔧 Stage 5: Instruction Engineering")

        skeleton_info = self.skeleton_library[skeleton]

        # Base instructions from skeleton
        instructions = {
            "role": skeleton_info["role"],
            "reasoning_style": skeleton_info["reasoning"],
            "approach": self._determine_approach(intent_clarification),
            "safety_rules": self._generate_safety_rules(constraints)
        }

        # Add task-specific instructions
        if intent_clarification.depth == UrgencyLevel.EXPERT:
            instructions["depth"] = "expert level analysis with comprehensive coverage"
        elif intent_clarification.depth == UrgencyLevel.DETAILED:
            instructions["depth"] = "detailed explanation with examples"
        else:
            instructions["depth"] = "quick, focused response"

        # Add constraints to instructions
        if constraints.constraints:
            instructions["additional_constraints"] = constraints.constraints

        logger.info(f"   Role: {instructions['role']}, Approach: {instructions['approach']}")

        return instructions

    def _stage_6_output_specification(self, intent_clarification: IntentClarification,
                                     constraints: Constraints) -> Dict:
        """Stage 6: Specify output format and requirements."""
        logger.info("📄 Stage 6: Output Specification")

        # Base format selection
        format_mapping = {
            OutputType.CODE: {"format": "code_blocks", "language": "markdown"},
            OutputType.MARKDOWN: {"format": "markdown", "sections": True},
            OutputType.STEPS: {"format": "numbered_list", "sections": False},
            OutputType.JSON: {"format": "json", "schema": "structured"},
            OutputType.EXPLANATION: {"format": "narrative", "examples": True},
            OutputType.LIST: {"format": "bullet_points", "sections": False}
        }

        output_spec = format_mapping.get(
            intent_clarification.output_format,
            format_mapping[OutputType.MARKDOWN]
        )

        # Add verbosity level
        verbosity_mapping = {
            UrgencyLevel.QUICK: "concise",
            UrgencyLevel.DETAILED: "medium",
            UrgencyLevel.EXPERT: "comprehensive"
        }
        output_spec["verbosity"] = verbosity_mapping[intent_clarification.depth]

        # Add required sections based on task type
        if intent_clarification.task_type in [TaskType.DEBUGGING, TaskType.OPTIMIZATION]:
            output_spec["required_sections"] = ["Problem", "Solution", "Validation"]
        elif intent_clarification.task_type == TaskType.PLANNING:
            output_spec["required_sections"] = ["Plan", "Steps", "Resources"]

        logger.info(f"   Format: {output_spec['format']}, Verbosity: {output_spec['verbosity']}")

        return output_spec

    def _stage_7_prompt_assembly(self, raw_intent: RawIntent,
                               intent_clarification: IntentClarification,
                               constraints: Constraints,
                               context_injection: ContextInjection,
                               skeleton: PromptSkeleton,
                               instructions: Dict,
                               output_spec: Dict) -> str:
        """Stage 7: Assemble final prompt."""
        logger.info("🔗 Stage 7: Prompt Assembly")

        prompt_parts = []

        # [ROLE]
        prompt_parts.append(f"You are a {instructions['role']}.")
        prompt_parts.append("")

        # [TASK]
        prompt_parts.append("TASK:")
        prompt_parts.append(f"Original request: {raw_intent.text}")
        prompt_parts.append(f"Task type: {intent_clarification.task_type.value}")
        prompt_parts.append(f"Domain: {intent_clarification.domain}")
        prompt_parts.append("")

        # [CONTEXT]
        if context_injection.key_facts:
            prompt_parts.append("CONTEXT:")
            for fact in context_injection.key_facts:
                prompt_parts.append(f"- {fact}")
            if context_injection.project_context:
                prompt_parts.append(f"Project: {context_injection.project_context.get('project_name', 'Unknown')}")
            prompt_parts.append("")

        # [CONSTRAINTS]
        if constraints.tech_stack or constraints.constraints:
            prompt_parts.append("CONSTRAINTS:")
            if constraints.tech_stack:
                prompt_parts.append(f"Tech Stack: {', '.join(constraints.tech_stack)}")
            for constraint in constraints.constraints:
                prompt_parts.append(f"- {constraint}")
            if constraints.forbidden_actions:
                prompt_parts.append(f"Forbidden: {', '.join(constraints.forbidden_actions)}")
            prompt_parts.append("")

        # [INSTRUCTIONS]
        prompt_parts.append("INSTRUCTIONS:")
        prompt_parts.append(f"Reasoning style: {instructions['reasoning_style']}")
        prompt_parts.append(f"Approach: {instructions['approach']}")
        prompt_parts.append(f"Depth: {instructions['depth']}")
        if instructions.get('safety_rules'):
            prompt_parts.append(f"Safety rules: {', '.join(instructions['safety_rules'])}")
        prompt_parts.append("")

        # [STEPS/THINKING MODE]
        skeleton_info = self.skeleton_library[skeleton]
        prompt_parts.append("THINKING PROCESS:")
        for i, step in enumerate(skeleton_info["structure"], 1):
            prompt_parts.append(f"{i}. {step}")
        prompt_parts.append("")

        # [OUTPUT FORMAT]
        prompt_parts.append("OUTPUT FORMAT:")
        prompt_parts.append(f"Format: {output_spec['format']}")
        prompt_parts.append(f"Verbosity: {output_spec['verbosity']}")
        if output_spec.get('required_sections'):
            prompt_parts.append(f"Required sections: {', '.join(output_spec['required_sections'])}")
        if output_spec.get('examples'):
            prompt_parts.append("Include practical examples")
        prompt_parts.append("")

        # Final assembly
        final_prompt = "\n".join(prompt_parts)

        logger.info(f"   Assembled prompt length: {len(final_prompt)} characters")

        return final_prompt

    def _stage_8_quality_gate(self, raw_intent: RawIntent, assembled_prompt: str,
                             intent_clarification: IntentClarification,
                             constraints: Constraints) -> QualityGateResult:
        """Stage 8: Quality gate validation."""
        logger.info("🚪 Stage 8: Quality Gate")

        issues = []
        warnings = []
        recommendations = []
        score = 100.0

        # Check ambiguity
        if raw_intent.ambiguity_level > self.quality_thresholds["max_ambiguity"]:
            issues.append("High ambiguity in original input")
            recommendations.append("Request clarification from user")
            score -= 20

        # Check constraints
        if len(constraints.constraints) < self.quality_thresholds["min_constraints"]:
            warnings.append("Few constraints extracted")
            recommendations.append("Consider adding more specific requirements")
            score -= 10

        # Check prompt length
        if len(assembled_prompt) < 100:
            issues.append("Prompt too short")
            recommendations.append("Add more context and detail")
            score -= 15
        elif len(assembled_prompt) > 2000:
            warnings.append("Prompt very long, may reduce model effectiveness")
            score -= 5

        # Check for clarity
        if not any(keyword in assembled_prompt.lower()
                  for keyword in ['task:', 'context:', 'constraints:', 'format:']):
            issues.append("Missing clear prompt structure")
            recommendations.append("Add structured sections")
            score -= 25

        # Check for role clarity
        if 'you are a' not in assembled_prompt.lower():
            warnings.append("No clear role specified")
            recommendations.append("Define expert role for better results")
            score -= 10

        passed = len(issues) == 0 and score >= self.quality_thresholds["min_confidence"] * 100

        logger.info(f"   Quality Score: {score:.1f}, Passed: {passed}")

        return QualityGateResult(
            passed=passed,
            issues=issues,
            warnings=warnings,
            score=score,
            recommendations=recommendations
        )

    def _stage_9_execution_prep(self, final_prompt: str,
                               stage_results: Dict) -> Dict:
        """Stage 9: Prepare for execution and feedback capture."""
        logger.info("🚀 Stage 9: Execution Preparation")

        execution_context = {
            "prompt_id": f"prompt_{int(time.time())}",
            "timestamp": time.time(),
            "prompt_length": len(final_prompt),
            "stage_metadata": {
                "intent_confidence": stage_results.get("intent_clarification", IntentClarification(TaskType.EXPLANATION, "general", UrgencyLevel.DETAILED, OutputType.MARKDOWN)).confidence,
                "skeleton_used": stage_results.get("skeleton", PromptSkeleton.EXPLAIN_STEPS).value if stage_results.get("skeleton") else None,
                "quality_score": stage_results.get("quality_gate", QualityGateResult(True)).score
            },
            "feedback_capture": {
                "user_satisfaction": None,
                "corrections_needed": None,
                "follow_up_questions": [],
                "response_quality": None
            }
        }

        return execution_context

    # Helper methods
    def _detect_language(self, text: str) -> str:
        """Simple language detection."""
        # Simplified - would use proper language detection in production
        if any(word in text.lower() for word in ['the', 'and', 'is', 'to', 'of']):
            return "en"
        elif any(word in text.lower() for word in ['el', 'la', 'es', 'en', 'un']):
            return "es"
        else:
            return "unknown"

    def _calculate_ambiguity_level(self, text: str) -> float:
        """Calculate how ambiguous the input is."""
        ambiguity_indicators = [
            'maybe', 'perhaps', 'possibly', 'might', 'could',
            'something', 'anything', 'somehow', 'someway',
            'like', 'kind of', 'sort of'
        ]

        word_count = len(text.split())
        ambiguity_count = sum(1 for word in ambiguity_indicators if word in text.lower())

        # Normalize by word count
        return min(ambiguity_count / max(word_count, 1), 1.0)

    def _detect_task_type(self, text: str, context: Dict = None) -> TaskType:
        """Detect the type of task."""
        task_indicators = {
            TaskType.CODING: ['code', 'implement', 'function', 'class', 'api', 'write', 'create'],
            TaskType.DEBUGGING: ['debug', 'fix', 'error', 'broken', 'not working', 'issue'],
            TaskType.WRITING: ['write', 'explain', 'describe', 'document', 'summarize'],
            TaskType.RESEARCH: ['research', 'find', 'look up', 'information', 'learn about'],
            TaskType.ANALYSIS: ['analyze', 'review', 'examine', 'evaluate', 'assess'],
            TaskType.PLANNING: ['plan', 'design', 'architecture', 'strategy', 'roadmap'],
            TaskType.OPTIMIZATION: ['optimize', 'improve', 'enhance', 'make faster', 'performance'],
            TaskType.EXPLANATION: ['explain', 'how', 'why', 'what is', 'tell me about']
        }

        text_lower = text.lower()
        task_scores = {}

        for task_type, indicators in task_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            task_scores[task_type] = score

        # Return task type with highest score
        if task_scores:
            return max(task_scores.items(), key=lambda x: x[1])[0]
        return TaskType.EXPLANATION

    def _detect_domain(self, text: str, context: Dict = None) -> str:
        """Detect the domain/field."""
        domain_indicators = {
            'api': ['api', 'endpoint', 'rest', 'graphql', 'server'],
            'frontend': ['frontend', 'ui', 'react', 'vue', 'css', 'html', 'javascript'],
            'backend': ['backend', 'server', 'database', 'python', 'java', 'nodejs'],
            'database': ['database', 'sql', 'nosql', 'query', 'schema'],
            'devops': ['deploy', 'docker', 'kubernetes', 'ci/cd', 'infrastructure'],
            'security': ['security', 'auth', 'authentication', 'jwt', 'oauth'],
            'performance': ['performance', 'optimization', 'speed', 'latency', 'throughput']
        }

        text_lower = text.lower()
        if context and context.get('clipboard'):
            text_lower += " " + context['clipboard'].lower()

        for domain, indicators in domain_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return domain

        return "general"

    def _determine_depth(self, text: str, context: Dict = None) -> UrgencyLevel:
        """Determine the depth/urgency level."""
        text_lower = text.lower()

        quick_indicators = ['quick', 'fast', 'simple', 'brief', 'summary']
        expert_indicators = ['expert', 'detailed', 'comprehensive', 'thorough', 'in-depth']
        detailed_indicators = ['explain', 'analyze', 'review', 'detailed', 'step by step']

        if any(indicator in text_lower for indicator in quick_indicators):
            return UrgencyLevel.QUICK
        elif any(indicator in text_lower for indicator in expert_indicators):
            return UrgencyLevel.EXPERT
        elif any(indicator in text_lower for indicator in detailed_indicators):
            return UrgencyLevel.DETAILED
        else:
            return UrgencyLevel.DETAILED  # Default to detailed

    def _detect_output_format(self, text: str, task_type: TaskType) -> OutputType:
        """Detect expected output format."""
        format_indicators = {
            OutputType.CODE: ['code', 'function', 'class', 'script', 'implement'],
            OutputType.STEPS: ['steps', 'step by step', 'process', 'procedure'],
            OutputType.JSON: ['json', 'format', 'structure', 'schema'],
            OutputType.LIST: ['list', 'bullet points', 'items'],
            OutputType.MARKDOWN: ['markdown', 'format', 'document'],
            OutputType.DIAGRAM: ['diagram', 'chart', 'graph', 'visual']
        }

        text_lower = text.lower()

        # Task type specific defaults
        if task_type == TaskType.CODING:
            return OutputType.CODE
        elif task_type in [TaskType.DEBUGGING, TaskType.OPTIMIZATION]:
            return OutputType.STEPS

        # Check for explicit format requests
        for output_type, indicators in format_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return output_type

        return OutputType.MARKDOWN

    def _extract_tech_stack(self, text: str, context: Dict = None) -> List[str]:
        """Extract technology stack information."""
        tech_indicators = {
            'Python': ['python', 'django', 'flask', 'pandas', 'numpy'],
            'JavaScript': ['javascript', 'nodejs', 'react', 'vue', 'angular'],
            'Java': ['java', 'spring', 'maven', 'gradle'],
            'Go': ['golang', 'go'],
            'Rust': ['rust'],
            'Database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis'],
            'Cloud': ['aws', 'azure', 'gcp', 'lambda', 'ec2'],
            'Docker': ['docker', 'kubernetes', 'k8s', 'container'],
            'API': ['api', 'rest', 'graphql', 'endpoint'],
            'Frontend': ['react', 'vue', 'angular', 'css', 'html'],
            'Testing': ['test', 'pytest', 'jest', 'unit test']
        }

        text_lower = text.lower()
        if context and context.get('clipboard'):
            text_lower += " " + context['clipboard'].lower()

        tech_stack = []
        for tech, indicators in tech_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                tech_stack.append(tech)

        return list(set(tech_stack))

    def _extract_constraints(self, text: str) -> List[str]:
        """Extract explicit constraints."""
        constraint_patterns = [
            r'no\s+([a-z\s]+)',
            r'don\'?t\s+([a-z\s]+)',
            r'avoid\s+([a-z\s]+)',
            r'must\s+([a-z\s]+)',
            r'should\s+([a-z\s]+)',
            r'only\s+([a-z\s]+)'
        ]

        constraints = []
        for pattern in constraint_patterns:
            matches = re.findall(pattern, text.lower())
            constraints.extend(matches)

        # Clean and deduplicate
        return list(set(c.strip() for c in constraints if len(c.strip()) > 2))

    def _extract_style_preferences(self, text: str) -> List[str]:
        """Extract style preferences."""
        style_indicators = {
            'teaching': ['teach', 'explain', 'learn', 'educational'],
            'professional': ['professional', 'formal', 'business'],
            'casual': ['casual', 'informal', 'simple'],
            'step_by_step': ['step by step', 'stepwise', 'gradual'],
            'examples': ['examples', 'sample', 'demo', 'illustration']
        }

        text_lower = text.lower()
        preferences = []

        for style, indicators in style_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                preferences.append(style)

        return preferences

    def _extract_forbidden_actions(self, text: str) -> List[str]:
        """Extract forbidden actions."""
        forbidden_patterns = [
            r'don\'?t\s+(run|execute|write|create|delete)',
            r'no\s+(bash|shell|script|commands)',
            r'avoid\s+(changing|modifying|editing)',
            r'only\s+(explain|describe|analyze)'
        ]

        forbidden = []
        for pattern in forbidden_patterns:
            matches = re.findall(pattern, text.lower())
            forbidden.extend(matches)

        return list(set(forbidden))

    def _determine_approach(self, intent_clarification: IntentClarification) -> str:
        """Determine the approach based on intent."""
        approach_mapping = {
            TaskType.ANALYSIS: "Systematic analytical approach with clear methodology",
            TaskType.CODING: "Practical implementation focus with best practices",
            TaskType.DEBUGGING: "Methodical troubleshooting with root cause analysis",
            TaskType.OPTIMIZATION: "Data-driven approach with performance metrics",
            TaskType.PLANNING: "Strategic thinking with risk assessment",
            TaskType.EXPLANATION: "Clear communication with examples and analogies",
            TaskType.WRITING: "Structured narrative with logical flow",
            TaskType.RESEARCH: "Evidence-based approach with source validation"
        }

        return approach_mapping.get(
            intent_clarification.task_type,
            "Clear, structured approach appropriate to the task"
        )

    def _generate_safety_rules(self, constraints: Constraints) -> List[str]:
        """Generate safety rules based on constraints."""
        safety_rules = [
            "Ensure all suggestions are safe and secure",
            "Follow industry best practices",
            "Consider potential risks and edge cases"
        ]

        if constraints.forbidden_actions:
            safety_rules.append(f"Do not: {', '.join(constraints.forbidden_actions)}")

        if 'production' in constraints.constraints:
            safety_rules.append("Be extra careful with production system changes")

        return safety_rules

    def _adjust_intent_based_on_quality(self, raw_intent: RawIntent,
                                      quality_result: QualityGateResult) -> RawIntent:
        """Adjust raw intent based on quality gate feedback."""
        # Simple adjustment - in production would be more sophisticated
        adjusted_text = raw_intent.text

        if quality_result.recommendations:
            # Add clarification request to input
            adjusted_text += f"\nAdditional requirements: {', '.join(quality_result.recommendations[:2])}"

        return RawIntent(
            text=adjusted_text,
            language=raw_intent.language,
            length=len(adjusted_text.split()),
            ambiguity_level=max(0.1, raw_intent.ambiguity_level - 0.1),  # Assume slight improvement
            confidence=min(1.0, raw_intent.confidence + 0.1)
        )

    def _stage_0_5_prompt_merging(self, raw_intent: RawIntent, context: Dict[str, Any]) -> RawIntent:
        """
        Intelligently merge user prompt with clipboard content for better prompt generation.
        Analyzes whether clipboard context should be integrated into the main prompt.
        """
        # Extract clipboard content
        clipboard_content = context.get('clipboard', '') if context else ''
        if not clipboard_content:
            return raw_intent  # No clipboard to merge

        original_text = raw_intent.text
        merged_text = original_text

        # Analyze if merging is beneficial
        should_merge = self._should_merge_prompts(original_text, clipboard_content)

        if should_merge:
            # Different merging strategies based on content types
            merge_strategy = self._detect_merge_strategy(original_text, clipboard_content)

            if merge_strategy == "file_path_context":
                # Add file path context to the request
                merged_text = f"{original_text} (working with: {clipboard_content})"
                logger.info(f"📂 Merged file path context: {clipboard_content}")

            elif merge_strategy == "code_context":
                # Integrate code context into the prompt
                merged_text = f"{original_text}\n\nContext: {clipboard_content}"
                logger.info(f"💻 Merged code context from clipboard")

            elif merge_strategy == "project_context":
                # Add project/directory context
                merged_text = f"{original_text} (project: {clipboard_content})"
                logger.info(f"🏗️ Merged project context: {clipboard_content}")

            elif merge_strategy == "enhanced_request":
                # Create enhanced prompt combining both
                merged_text = f"{original_text}\n\nAdditional Context: {clipboard_content}"
                logger.info(f"✨ Created enhanced prompt with clipboard context")

            elif merge_strategy == "unified_prompt":
                # Create a unified, comprehensive prompt
                merged_text = self._create_unified_prompt(original_text, clipboard_content)
                logger.info(f"🎯 Created unified prompt combining user input and clipboard")

        # Return new RawIntent with merged text
        merged_intent = RawIntent(
            text=merged_text,
            language=raw_intent.language,
            length=len(merged_text.split()),
            ambiguity_level=raw_intent.ambiguity_level,
            confidence=raw_intent.confidence
        )

        logger.info(f"🔗 Prompt merging: '{original_text[:50]}...' + '{clipboard_content[:30]}...' → '{merged_text[:60]}...'")
        return merged_intent

    def _should_merge_prompts(self, user_text: str, clipboard_content: str) -> bool:
        """Determine if clipboard content should be merged with user prompt."""
        # Don't merge if clipboard is too short or too long
        if len(clipboard_content.strip()) < 3:
            return False
        if len(clipboard_content) > 2000:  # Too much content
            return False

        # Don't merge if user text is already very specific and complete
        user_text_lower = user_text.lower()
        complete_indicators = [
            "step by step", "detailed analysis", "comprehensive review",
            "full implementation", "complete guide", "detailed instructions"
        ]
        if any(indicator in user_text_lower for indicator in complete_indicators):
            return False

        # Merge if clipboard looks like a file path
        if clipboard_content.startswith('/') or '\\' in clipboard_content:
            return True

        # Merge if clipboard contains code-like content
        code_indicators = ['def ', 'class ', 'function', 'import ', 'from ']
        if any(indicator in clipboard_content for indicator in code_indicators):
            return True

        # Merge if user text is asking for analysis/optimization
        analysis_keywords = ['analyze', 'optimize', 'review', 'improve', 'fix', 'debug']
        if any(keyword in user_text_lower for keyword in analysis_keywords):
            return True

        return False

    def _detect_merge_strategy(self, user_text: str, clipboard_content: str) -> str:
        """Detect the best strategy for merging user text with clipboard content."""
        # File path strategy
        if clipboard_content.startswith('/') or '\\' in clipboard_content:
            return "file_path_context"

        # Code context strategy
        code_indicators = ['def ', 'class ', 'function', 'import ', 'from ', '{', '}']
        if any(indicator in clipboard_content for indicator in code_indicators):
            return "code_context"

        # Project context strategy (directory paths)
        if '.' in clipboard_content and not ' ' in clipboard_content.strip():
            return "project_context"

        # Check if clipboard contains structured data
        if '\n' in clipboard_content and len(clipboard_content.split('\n')) > 3:
            return "unified_prompt"

        # Default to enhanced request
        return "enhanced_request"

    def _create_unified_prompt(self, user_text: str, clipboard_content: str) -> str:
        """Create a unified prompt that intelligently combines user input and clipboard."""
        # Clean up clipboard content
        clipboard_lines = clipboard_content.strip().split('\n')

        # Take first few relevant lines from clipboard
        relevant_lines = []
        for line in clipboard_lines[:5]:  # Max 5 lines
            line = line.strip()
            if line and len(line) > 5:  # Skip very short lines
                relevant_lines.append(line)

        if relevant_lines:
            context_snippet = '\n'.join(relevant_lines)
            return f"""{user_text}

Context Information:
{context_snippet}"""
        else:
            return f"{user_text}\n\nAdditional Context: {clipboard_content}"

# Global pipeline instance
prompt_pipeline = PromptGenerationPipeline()