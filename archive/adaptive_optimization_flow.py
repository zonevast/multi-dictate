#!/usr/bin/env python3
"""
Adaptive Optimization Flow Detection System
Creates step-by-step optimization strategies that work with any AI model.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class OptimizationStep(Enum):
    """Different types of optimization steps."""
    CONTEXT_ANALYSIS = "context_analysis"
    INTENT_DETECTION = "intent_detection"
    DOMAIN_IDENTIFICATION = "domain_identification"
    CLARITY_ENHANCEMENT = "clarity_enhancement"
    STRUCTURE_FORMATTING = "structure_formatting"
    CONSTRAINT_DEFINITION = "constraint_definition"
    OUTPUT_SPECIFICATION = "output_specification"
    QUALITY_ENRICHMENT = "quality_enrichment"
    MODEL_ADAPTATION = "model_adaptation"

class ModelType(Enum):
    """Types of AI models for optimization."""
    GENERAL_PURPOSE = "general_purpose"  # GPT-4, Claude, Gemini
    SPECIALIZED = "specialized"           # Code models, specific domains
    LIGHTWEIGHT = "lightweight"           # Smaller, faster models
    RULE_BASED = "rule_based"             # Traditional systems

@dataclass
class OptimizationStepResult:
    """Result of a single optimization step."""
    step: OptimizationStep
    success: bool
    input_text: str
    output_text: str
    improvements_made: List[str]
    confidence: float  # 0-1
    processing_time: float

@dataclass
class OptimizationFlow:
    """Complete optimization flow with steps."""
    model_type: ModelType
    steps: List[OptimizationStep]
    step_results: List[OptimizationStepResult] = field(default_factory=list)
    overall_improvement_ratio: float = 0.0
    total_processing_time: float = 0.0
    final_confidence: float = 0.0

class AdaptiveOptimizationFlow:
    """Intelligent optimization flow that adapts to any AI model."""

    def __init__(self):
        self.step_strategies = self._initialize_step_strategies()
        self.model_profiles = self._initialize_model_profiles()
        self.flow_patterns = self._initialize_flow_patterns()

    def _initialize_step_strategies(self) -> Dict[OptimizationStep, callable]:
        """Initialize strategies for each optimization step."""
        return {
            OptimizationStep.CONTEXT_ANALYSIS: self._analyze_context_step,
            OptimizationStep.INTENT_DETECTION: self._detect_intent_step,
            OptimizationStep.DOMAIN_IDENTIFICATION: self._identify_domain_step,
            OptimizationStep.CLARITY_ENHANCEMENT: self._enhance_clarity_step,
            OptimizationStep.STRUCTURE_FORMATTING: self._format_structure_step,
            OptimizationStep.CONSTRAINT_DEFINITION: self._define_constraints_step,
            OptimizationStep.OUTPUT_SPECIFICATION: self._specify_output_step,
            OptimizationStep.QUALITY_ENRICHMENT: self._enrich_quality_step,
            OptimizationStep.MODEL_ADAPTATION: self._adapt_for_model_step
        }

    def _initialize_model_profiles(self) -> Dict[ModelType, Dict]:
        """Initialize optimization profiles for different model types."""
        return {
            ModelType.GENERAL_PURPOSE: {
                "strengths": ["reasoning", "complex_tasks", "natural_language"],
                "weaknesses": ["might_need_structured_input", "prefers_clear_instructions"],
                "optimal_steps": [
                    OptimizationStep.CONTEXT_ANALYSIS,
                    OptimizationStep.INTENT_DETECTION,
                    OptimizationStep.CLARITY_ENHANCEMENT,
                    OptimizationStep.STRUCTURE_FORMATTING,
                    OptimizationStep.OUTPUT_SPECIFICATION
                ],
                "complexity_threshold": 0.3
            },
            ModelType.SPECIALIZED: {
                "strengths": ["domain_knowledge", "specific_tasks"],
                "weaknesses": ["limited_scope", "needs_precise_context"],
                "optimal_steps": [
                    OptimizationStep.DOMAIN_IDENTIFICATION,
                    OptimizationStep.CONTEXT_ANALYSIS,
                    OptimizationStep.CONSTRAINT_DEFINITION,
                    OptimizationStep.OUTPUT_SPECIFICATION
                ],
                "complexity_threshold": 0.6
            },
            ModelType.LIGHTWEIGHT: {
                "strengths": ["speed", "simplicity"],
                "weaknesses": ["limited_reasoning", "simple_structure_preference"],
                "optimal_steps": [
                    OptimizationStep.INTENT_DETECTION,
                    OptimizationStep.CLARITY_ENHANCEMENT,
                    OptimizationStep.OUTPUT_SPECIFICATION
                ],
                "complexity_threshold": 0.2
            },
            ModelType.RULE_BASED: {
                "strengths": ["predictable", "structured"],
                "weaknesses": ["no_reasoning", "literal_interpretation"],
                "optimal_steps": [
                    OptimizationStep.STRUCTURE_FORMATTING,
                    OptimizationStep.CONSTRAINT_DEFINITION,
                    OptimizationStep.OUTPUT_SPECIFICATION
                ],
                "complexity_threshold": 0.1
            }
        }

    def _initialize_flow_patterns(self) -> Dict[str, List[OptimizationStep]]:
        """Initialize pre-defined flow patterns."""
        return {
            "simple_task": [
                OptimizationStep.INTENT_DETECTION,
                OptimizationStep.CLARITY_ENHANCEMENT,
                OptimizationStep.OUTPUT_SPECIFICATION
            ],
            "complex_analysis": [
                OptimizationStep.CONTEXT_ANALYSIS,
                OptimizationStep.INTENT_DETECTION,
                OptimizationStep.DOMAIN_IDENTIFICATION,
                OptimizationStep.CLARITY_ENHANCEMENT,
                OptimizationStep.STRUCTURE_FORMATTING,
                OptimizationStep.CONSTRAINT_DEFINITION,
                OptimizationStep.OUTPUT_SPECIFICATION
            ],
            "creative_task": [
                OptimizationStep.INTENT_DETECTION,
                OptimizationStep.CLARITY_ENHANCEMENT,
                OptimizationStep.QUALITY_ENRICHMENT,
                OptimizationStep.OUTPUT_SPECIFICATION
            ],
            "technical_problem": [
                OptimizationStep.CONTEXT_ANALYSIS,
                OptimizationStep.DOMAIN_IDENTIFICATION,
                OptimizationStep.STRUCTURE_FORMATTING,
                OptimizationStep.CONSTRAINT_DEFINITION,
                OptimizationStep.OUTPUT_SPECIFICATION
            ]
        }

    def detect_optimization_flow(self, input_text: str, context: Dict = None,
                               model_type: ModelType = ModelType.GENERAL_PURPOSE) -> OptimizationFlow:
        """
        Detect and apply the optimal optimization flow for the given input.

        Args:
            input_text: Original user input
            context: Additional context (clipboard, etc.)
            model_type: Target AI model type

        Returns:
            OptimizationFlow with complete step-by-step optimization
        """
        import time
        start_time = time.time()

        logger.info(f"🔄 Starting adaptive optimization flow for {model_type.value}")

        # Determine flow pattern
        flow_pattern = self._determine_flow_pattern(input_text, context)
        logger.info(f"📋 Flow pattern detected: {flow_pattern}")

        # Get model-specific optimization steps
        model_profile = self.model_profiles[model_type]
        base_steps = self.flow_patterns.get(flow_pattern, self.flow_patterns["simple_task"])

        # Combine with model-specific steps
        optimization_steps = self._combine_model_and_flow_steps(
            base_steps,
            model_profile["optimal_steps"],
            model_profile["complexity_threshold"]
        )

        # Create flow object
        flow = OptimizationFlow(
            model_type=model_type,
            steps=optimization_steps
        )

        # Execute optimization steps
        current_text = input_text
        step_results = []

        for step in optimization_steps:
            step_start = time.time()

            try:
                step_strategy = self.step_strategies[step]
                result = step_strategy(current_text, context, model_type)

                if result.success:
                    current_text = result.output_text
                    step_results.append(result)
                    logger.info(f"✅ {step.value}: {', '.join(result.improvements_made[:3])}")
                else:
                    logger.warning(f"⚠️ {step.value}: No improvement made")
                    # Still add the result but keep original text
                    step_results.append(OptimizationStepResult(
                        step=step,
                        success=False,
                        input_text=current_text,
                        output_text=current_text,
                        improvements_made=[],
                        confidence=0.0,
                        processing_time=time.time() - step_start
                    ))

            except Exception as e:
                logger.error(f"❌ {step.value} failed: {e}")
                step_results.append(OptimizationStepResult(
                    step=step,
                    success=False,
                    input_text=current_text,
                    output_text=current_text,
                    improvements_made=[],
                    confidence=0.0,
                    processing_time=time.time() - step_start
                ))

        # Calculate final metrics
        total_time = time.time() - start_time
        improvement_ratio = len(current_text) / max(len(input_text), 1)
        avg_confidence = sum(r.confidence for r in step_results) / len(step_results) if step_results else 0

        flow.step_results = step_results
        flow.overall_improvement_ratio = improvement_ratio
        flow.total_processing_time = total_time
        flow.final_confidence = avg_confidence

        logger.info(f"🎯 Optimization complete: {improvement_ratio:.1f}x improvement in {total_time*1000:.1f}ms")

        return flow

    def _determine_flow_pattern(self, input_text: str, context: Dict = None) -> str:
        """Determine the optimal flow pattern based on input analysis."""
        text_lower = input_text.lower()

        # Check for technical/problem-solving indicators
        technical_indicators = [
            'debug', 'error', 'fix', 'implement', 'optimize', 'performance',
            'database', 'api', 'code', 'function', 'algorithm', 'system'
        ]

        # Check for creative/complex task indicators
        creative_indicators = [
            'design', 'create', 'develop', 'build', 'architect', 'plan',
            'strategy', 'analyze', 'evaluate', 'recommend'
        ]

        # Check for complex analysis indicators
        analysis_indicators = [
            'analyze', 'evaluate', 'compare', 'assess', 'review', 'audit',
            'comprehensive', 'detailed', 'in-depth', 'thorough'
        ]

        # Count indicators
        technical_count = sum(1 for indicator in technical_indicators if indicator in text_lower)
        creative_count = sum(1 for indicator in creative_indicators if indicator in text_lower)
        analysis_count = sum(1 for indicator in analysis_indicators if indicator in text_lower)

        # Check context complexity
        context_score = 0
        if context:
            if 'clipboard' in context and context['clipboard']:
                context_score += 1
            if any(path in str(context).lower() for path in ['/', '\\', 'project']):
                context_score += 1
            if len(str(context)) > 100:
                context_score += 1

        # Determine pattern
        if technical_count > 2 or (technical_count > 0 and context_score > 1):
            return "technical_problem"
        elif analysis_count > 2 or (analysis_count > 0 and context_score > 0):
            return "complex_analysis"
        elif creative_count > 1:
            return "creative_task"
        else:
            return "simple_task"

    def _combine_model_and_flow_steps(self, flow_steps: List[OptimizationStep],
                                     model_steps: List[OptimizationStep],
                                     complexity_threshold: float) -> List[OptimizationStep]:
        """Combine flow-specific steps with model-specific optimization steps."""
        # Start with flow steps
        combined = flow_steps.copy()

        # Add model-specific steps that aren't already included
        for model_step in model_steps:
            if model_step not in combined:
                combined.append(model_step)

        # Add final model adaptation
        combined.append(OptimizationStep.MODEL_ADAPTATION)

        return combined

    def _analyze_context_step(self, text: str, context: Dict = None,
                            model_type: ModelType = ModelType.GENERAL_PURPOSE) -> OptimizationStepResult:
        """Step 1: Analyze and integrate context."""
        import time
        start_time = time.time()

        improvements = []
        result_text = text
        confidence = 0.0

        if context and context.get('clipboard'):
            clipboard = context['clipboard']

            # Check if clipboard contains a file path
            if any(indicator in clipboard for indicator in ['/', '\\', '~/', './', '../']):
                # Extract project information
                path_parts = clipboard.replace('\\', '/').split('/')
                if len(path_parts) > 1:
                    project_name = path_parts[-1] if path_parts[-1] else path_parts[-2]

                    context_info = f"""
Context Analysis:
- Target Project: {clipboard}
- Project Name: {project_name}
- Context Type: File/Directory Path
"""

                    result_text = context_info + f"\nOriginal Request: {text}"
                    improvements.append(f"Added project context: {project_name}")
                    confidence += 0.7

            # Add general context
            elif len(clipboard) > 10:
                context_info = f"""
Context Analysis:
- Available Context: {clipboard[:100]}{'...' if len(clipboard) > 100 else ''}
- Context Type: General Information
"""

                result_text = context_info + f"\nOriginal Request: {text}"
                improvements.append("Integrated context information")
                confidence += 0.5

        if not improvements:
            confidence = 0.1  # Low confidence if no context found
        else:
            confidence = min(confidence, 1.0)

        return OptimizationStepResult(
            step=OptimizationStep.CONTEXT_ANALYSIS,
            success=len(improvements) > 0,
            input_text=text,
            output_text=result_text,
            improvements_made=improvements,
            confidence=confidence,
            processing_time=time.time() - start_time
        )

    def _detect_intent_step(self, text: str, context: Dict = None,
                         model_type: ModelType = ModelType.GENERAL_PURPOSE) -> OptimizationStepResult:
        """Step 2: Detect and clarify user intent."""
        import time
        start_time = time.time()

        improvements = []
        result_text = text
        confidence = 0.0

        # Intent detection patterns
        intent_patterns = {
            'create': ['create', 'make', 'build', 'develop', 'write', 'implement'],
            'analyze': ['analyze', 'examine', 'review', 'evaluate', 'assess'],
            'fix': ['fix', 'debug', 'solve', 'resolve', 'correct', 'repair'],
            'optimize': ['optimize', 'improve', 'enhance', 'make better', 'speed up'],
            'explain': ['explain', 'describe', 'tell me about', 'what is', 'how does'],
            'compare': ['compare', 'difference', 'versus', 'vs', 'better than']
        }

        text_lower = text.lower()
        detected_intents = []

        for intent, indicators in intent_patterns.items():
            if any(indicator in text_lower for indicator in indicators):
                detected_intents.append(intent)

        if detected_intents:
            primary_intent = detected_intents[0]  # Take the first detected intent

            intent_info = f"""
Intent Analysis:
- Primary Intent: {primary_intent.title()}
- All Detected Intents: {', '.join(detected_intents)}
- User Goal: {' '.join(text.split()[:5])}...
"""

            result_text = intent_info + f"\n{result_text}"
            improvements.append(f"Clarified intent: {primary_intent}")
            confidence = 0.8
        else:
            # Add general intent clarification
            intent_info = """
Intent Analysis:
- Primary Intent: General Request
- User Goal: Needs clarification from context
- Recommendation: Focus on providing clear, actionable response
"""

            result_text = intent_info + f"\n{result_text}"
            improvements.append("Added general intent analysis")
            confidence = 0.4

        return OptimizationStepResult(
            step=OptimizationStep.INTENT_DETECTION,
            success=True,
            input_text=text,
            output_text=result_text,
            improvements_made=improvements,
            confidence=confidence,
            processing_time=time.time() - start_time
        )

    def _identify_domain_step(self, text: str, context: Dict = None,
                           model_type: ModelType = ModelType.GENERAL_PURPOSE) -> OptimizationStepResult:
        """Step 3: Identify domain and specialized knowledge requirements."""
        import time
        start_time = time.time()

        improvements = []
        result_text = text
        confidence = 0.0

        # Domain detection patterns
        domain_patterns = {
            'software_development': [
                'code', 'programming', 'software', 'application', 'api',
                'database', 'frontend', 'backend', 'debug', 'deploy'
            ],
            'data_science': [
                'data', 'analysis', 'machine learning', 'ai', 'model',
                'statistics', 'visualization', 'dataset', 'algorithm'
            ],
            'system_administration': [
                'server', 'network', 'security', 'infrastructure',
                'deployment', 'monitoring', 'linux', 'cloud', 'devops'
            ],
            'business': [
                'business', 'strategy', 'marketing', 'sales', 'finance',
                'revenue', 'customer', 'market', 'competition'
            ],
            'creative': [
                'design', 'creative', 'art', 'visual', 'user interface',
                'user experience', 'branding', 'content', 'writing'
            ]
        }

        text_lower = text.lower()
        detected_domains = []

        for domain, indicators in domain_patterns.items():
            if any(indicator in text_lower for indicator in indicators):
                detected_domains.append(domain)

        if detected_domains:
            domain_info = f"""
Domain Identification:
- Primary Domain: {detected_domains[0].replace('_', ' ').title()}
- Related Domains: {', '.join(d.replace('_', ' ').title() for d in detected_domains[1:])}
- Specialized Knowledge Required: Yes
"""

            result_text = domain_info + f"\n{result_text}"
            improvements.append(f"Identified domain: {detected_domains[0]}")
            confidence = 0.7
        else:
            domain_info = """
Domain Identification:
- Primary Domain: General
- Specialized Knowledge Required: No
- Approach: Use general problem-solving methods
"""

            result_text = domain_info + f"\n{result_text}"
            improvements.append("Marked as general domain")
            confidence = 0.3

        return OptimizationStepResult(
            step=OptimizationStep.DOMAIN_IDENTIFICATION,
            success=True,
            input_text=text,
            output_text=result_text,
            improvements_made=improvements,
            confidence=confidence,
            processing_time=time.time() - start_time
        )

    def _enhance_clarity_step(self, text: str, context: Dict = None,
                           model_type: ModelType = ModelType.GENERAL_PURPOSE) -> OptimizationStepResult:
        """Step 4: Enhance clarity and remove ambiguity."""
        import time
        start_time = time.time()

        improvements = []
        result_text = text
        confidence = 0.5

        # Remove ambiguous language
        ambiguous_phrases = [
            'maybe', 'perhaps', 'possibly', 'might', 'could',
            'sort of', 'kind of', 'like', 'something'
        ]

        text_lower = text.lower()
        for phrase in ambiguous_phrases:
            if phrase in text_lower:
                # Replace with more definitive language
                if phrase in ['maybe', 'perhaps', 'possibly']:
                    result_text = result_text.replace(phrase, 'consider')
                    improvements.append("Replaced ambiguous language with definitive terms")
                elif phrase in ['sort of', 'kind of']:
                    result_text = result_text.replace(phrase, '')
                    improvements.append("Removed filler words")

        # Add structure indicators
        if 'step' not in text_lower and len(text.split()) < 10:
            if any(action in text_lower for action in ['how', 'what', 'why', 'explain']):
                result_text = f"Please provide clear, structured explanation for:\n{result_text}"
                improvements.append("Added structured format request")

        # Check for clear objectives
        if not any(obj in text_lower for obj in ['goal', 'objective', 'purpose', 'achieve']):
            result_text = f"Objective: {result_text}"
            improvements.append("Added clear objective statement")

        confidence = min(len(improvements) * 0.3 + 0.2, 0.9)

        return OptimizationStepResult(
            step=OptimizationStep.CLARITY_ENHANCEMENT,
            success=len(improvements) > 0,
            input_text=text,
            output_text=result_text,
            improvements_made=improvements,
            confidence=confidence,
            processing_time=time.time() - start_time
        )

    def _format_structure_step(self, text: str, context: Dict = None,
                             model_type: ModelType = ModelType.GENERAL_PURPOSE) -> OptimizationStepResult:
        """Step 5: Format with optimal structure for the model."""
        import time
        start_time = time.time()

        improvements = []
        result_text = text
        confidence = 0.0

        # Check current structure
        has_sections = any(section in text.lower() for section in [
            'task:', 'objective:', 'context:', 'requirements:', 'steps:'
        ])

        has_numbering = bool(re.search(r'\b\d+\.', text))

        # Format based on model type
        if model_type == ModelType.GENERAL_PURPOSE:
            if not has_sections:
                # Add structured sections
                sections = [
                    "Task:",
                    "Context:",
                    "Requirements:",
                    "Expected Output:"
                ]

                structured_text = "\n".join(sections) + f"\n\n{text}"
                result_text = structured_text
                improvements.append("Added structured sections for general-purpose model")
                confidence = 0.8

        elif model_type == ModelType.LIGHTWEIGHT:
            # Simple structure for lightweight models
            if not has_numbering and len(text.split()) > 5:
                # Break into numbered points
                sentences = re.split(r'[.!?]+', text)
                numbered_text = "\n".join(f"{i+1}. {s.strip()}"
                                      for i, s in enumerate(sentences) if s.strip())
                result_text = numbered_text
                improvements.append("Converted to numbered list for lightweight model")
                confidence = 0.7

        elif model_type == ModelType.RULE_BASED:
            # Very structured format for rule-based systems
            if 'INPUT:' not in text.upper():
                rule_based_format = f"""
INPUT: {text}
CONTEXT: {context.get('clipboard', '')[:100] if context else 'None'}
TYPE: REQUEST
EXPECTED: DETAILED_RESPONSE
"""
                result_text = rule_based_format.strip()
                improvements.append("Formatted for rule-based system")
                confidence = 0.9

        return OptimizationStepResult(
            step=OptimizationStep.STRUCTURE_FORMATTING,
            success=len(improvements) > 0,
            input_text=text,
            output_text=result_text,
            improvements_made=improvements,
            confidence=confidence,
            processing_time=time.time() - start_time
        )

    def _define_constraints_step(self, text: str, context: Dict = None,
                              model_type: ModelType = ModelType.GENERAL_PURPOSE) -> OptimizationStepResult:
        """Step 6: Define constraints and boundaries."""
        import time
        start_time = time.time()

        improvements = []
        result_text = text
        confidence = 0.0

        # Add standard constraints based on model type
        if model_type == ModelType.GENERAL_PURPOSE:
            constraints = [
                "- Provide specific, actionable advice",
                "- Include examples where relevant",
                "- Consider best practices and industry standards",
                "- Maintain professional tone"
            ]
        elif model_type == ModelType.SPECIALIZED:
            constraints = [
                "- Focus on domain-specific expertise",
                "- Use precise terminology",
                "- Include relevant standards or regulations",
                "- Provide technical depth"
            ]
        elif model_type == ModelType.LIGHTWEIGHT:
            constraints = [
                "- Keep response concise",
                "- Focus on main points",
                "- Use simple language",
                "- Provide clear next steps"
            ]
        else:
            constraints = [
                "- Follow exact instructions",
                "- Provide structured response",
                "- Be comprehensive but concise"
            ]

        constraints_section = "\n".join(constraints)
        result_text += f"\n\nConstraints:\n{constraints_section}"
        improvements.append(f"Added {len(constraints)} constraints for {model_type.value}")
        confidence = 0.6

        return OptimizationStepResult(
            step=OptimizationStep.CONSTRAINT_DEFINITION,
            success=True,
            input_text=text,
            output_text=result_text,
            improvements_made=improvements,
            confidence=confidence,
            processing_time=time.time() - start_time
        )

    def _specify_output_step(self, text: str, context: Dict = None,
                           model_type: ModelType = ModelType.GENERAL_PURPOSE) -> OptimizationStepResult:
        """Step 7: Specify expected output format."""
        import time
        start_time = time.time()

        improvements = []
        result_text = text
        confidence = 0.0

        # Determine optimal output format based on model and content
        output_formats = {
            ModelType.GENERAL_PURPOSE: """
Expected Output Format:
1. Summary of key points
2. Detailed explanation with examples
3. Actionable recommendations
4. Next steps or considerations
""",
            ModelType.SPECIALIZED: """
Expected Output Format:
- Executive Summary
- Technical Analysis
- Implementation Details
- References to Standards/Best Practices
""",
            ModelType.LIGHTWEIGHT: """
Expected Output Format:
• Main point
• Key steps (numbered)
• Important considerations
""",
            ModelType.RULE_BASED: """
Expected Output Format:
RESULT: [clear outcome]
REASONING: [step-by-step logic]
CONFIDENCE: [high/medium/low]
"""
        }

        output_format = output_formats.get(model_type, output_formats[ModelType.GENERAL_PURPOSE])
        result_text += f"\n{output_format}"

        improvements.append(f"Specified output format for {model_type.value}")
        confidence = 0.8

        return OptimizationStepResult(
            step=OptimizationStep.OUTPUT_SPECIFICATION,
            success=True,
            input_text=text,
            output_text=result_text,
            improvements_made=improvements,
            confidence=confidence,
            processing_time=time.time() - start_time
        )

    def _enrich_quality_step(self, text: str, context: Dict = None,
                          model_type: ModelType = ModelType.GENERAL_PURPOSE) -> OptimizationStepResult:
        """Step 8: Add quality enrichment factors."""
        import time
        start_time = time.time()

        improvements = []
        result_text = text
        confidence = 0.0

        # Add quality indicators
        quality_factors = [
            "Quality Requirements:",
            "- Accuracy: High priority",
            "- Completeness: Cover all aspects",
            "- Clarity: Easy to understand",
            "- Relevance: Directly addresses request"
        ]

        if model_type == ModelType.GENERAL_PURPOSE:
            quality_factors.extend([
                "- Depth: Provide comprehensive coverage",
                "- Practicality: Include real-world applications"
            ])
        elif model_type == ModelType.SPECIALIZED:
            quality_factors.extend([
                "- Precision: Use exact terminology",
                "- Validation: Reference authoritative sources"
            ])

        result_text += f"\n\n{chr(10).join(quality_factors)}"
        improvements.append("Added quality enhancement factors")
        confidence = 0.5

        return OptimizationStepResult(
            step=OptimizationStep.QUALITY_ENRICHMENT,
            success=True,
            input_text=text,
            output_text=result_text,
            improvements_made=improvements,
            confidence=confidence,
            processing_time=time.time() - start_time
        )

    def _adapt_for_model_step(self, text: str, context: Dict = None,
                           model_type: ModelType = ModelType.GENERAL_PURPOSE) -> OptimizationStepResult:
        """Step 9: Final adaptation for specific model."""
        import time
        start_time = time.time()

        improvements = []
        result_text = text
        confidence = 0.8

        # Model-specific final adaptations
        if model_type == ModelType.GENERAL_PURPOSE:
            # Add expertise activation for general models
            expertise_prompt = """
Model Instructions:
- Act as an expert consultant with relevant domain knowledge
- Use analytical thinking and professional judgment
- Provide comprehensive, well-reasoned responses
- Consider multiple perspectives and approaches
"""
            result_text = expertise_prompt + f"\n{result_text}"
            improvements.append("Added expertise activation for general model")

        elif model_type == ModelType.LIGHTWEIGHT:
            # Simplify for lightweight models
            simplification_note = """
Note: Keep response concise and focused on main points.
Avoid complex jargon and use clear, simple language.
"""
            result_text += f"\n{simplification_note}"
            improvements.append("Added simplification for lightweight model")

        elif model_type == ModelType.SPECIALIZED:
            # Add domain expertise activation
            domain_note = """
Domain Expertise Required:
- Apply specialized knowledge from the identified domain
- Use industry-standard terminology and practices
- Reference relevant frameworks or methodologies
"""
            result_text += f"\n{domain_note}"
            improvements.append("Added domain expertise activation")

        return OptimizationStepResult(
            step=OptimizationStep.MODEL_ADAPTATION,
            success=True,
            input_text=text,
            output_text=result_text,
            improvements_made=improvements,
            confidence=confidence,
            processing_time=time.time() - start_time
        )

    def generate_flow_report(self, flow: OptimizationFlow) -> str:
        """Generate a comprehensive flow optimization report."""
        report = []
        report.append("🔄 ADAPTIVE OPTIMIZATION FLOW REPORT")
        report.append("=" * 50)

        # Summary
        report.append(f"🎯 Target Model: {flow.model_type.value.title()}")
        report.append(f"📈 Improvement Ratio: {flow.overall_improvement_ratio:.1f}x")
        report.append(f"⚡ Processing Time: {flow.total_processing_time*1000:.1f}ms")
        report.append(f"🔢 Final Confidence: {flow.final_confidence:.1%}")
        report.append(f"📋 Steps Executed: {len(flow.steps)}")
        report.append("")

        # Step-by-step breakdown
        report.append("📋 Step-by-Step Breakdown:")
        for i, step_result in enumerate(flow.step_results, 1):
            status = "✅" if step_result.success else "❌"
            step_name = step_result.step.value.replace('_', ' ').title()
            report.append(f"  {i}. {status} {step_name}")

            if step_result.success:
                report.append(f"     → Improvements: {', '.join(step_result.improvements_made[:2])}")
                report.append(f"     → Confidence: {step_result.confidence:.1%}")
                report.append(f"     → Time: {step_result.processing_time*1000:.1f}ms")
            else:
                report.append(f"     → Status: No improvement made")

        # Success rate
        successful_steps = sum(1 for r in flow.step_results if r.success)
        success_rate = (successful_steps / len(flow.step_results)) * 100
        report.append(f"\n📊 Overall Success Rate: {successful_steps}/{len(flow.step_results)} ({success_rate:.1f}%)")

        # Recommendations
        if success_rate < 80:
            report.append("\n💡 Optimization Recommendations:")
            if flow.final_confidence < 0.6:
                report.append("  • Consider providing more specific input")
            if flow.total_processing_time > 0.1:  # 100ms
                report.append("  • Consider using lightweight flow for faster processing")
            if flow.overall_improvement_ratio < 2:
                report.append("  • Input may already be well-structured")

        return "\n".join(report)

# Global instance
adaptive_flow = AdaptiveOptimizationFlow()