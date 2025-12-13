#!/usr/bin/env python3
"""
Advanced prompt optimization quality scoring and tuning system.
Provides comprehensive metrics for evaluating prompt engineering effectiveness.
"""

import re
import time
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """Different dimensions of prompt quality."""
    CLARITY = "clarity"
    SPECIFICITY = "specificity"
    CONTEXTUALIZATION = "contextualization"
    ACTIONABILITY = "actionability"
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"

@dataclass
class QualityScore:
    """Individual quality dimension score."""
    dimension: QualityDimension
    score: float  # 0-100
    details: str
    suggestions: List[str]

@dataclass
class OptimizationResult:
    """Complete optimization analysis result."""
    overall_score: float  # 0-100
    dimension_scores: List[QualityScore]
    improvement_ratio: float
    processing_time: float
    enhancement_detected: bool
    recommendations: List[str]

class PromptQualityScorer:
    """Advanced system for scoring and tuning prompt optimization quality."""

    def __init__(self):
        self.quality_weights = {
            QualityDimension.CLARITY: 0.20,
            QualityDimension.SPECIFICITY: 0.20,
            QualityDimension.CONTEXTUALIZATION: 0.25,
            QualityDimension.ACTIONABILITY: 0.15,
            QualityDimension.COMPLETENESS: 0.10,
            QualityDimension.RELEVANCE: 0.10
        }

        # Optimization patterns that indicate high quality
        self.high_quality_patterns = {
            "structured_context": [
                r"Target Project:", r"Project Name:", r"Technical Context:",
                r"Domain:", r"Complexity:", r"Technologies:"
            ],
            "expert_roles": [
                r"Act as an expert", r"specialist", r"consultant", r"architect"
            ],
            "actionoriented": [
                r"Analyze", r"Implement", r"Design", r"Optimize", r"Develop",
                r"Test", r"Deploy", r"Create", r"Build", r"Evaluate"
            ],
            "structured_output": [
                r"steps", r"criteria", r"metrics", r"timeline", r"deliverables"
            ],
            "context_integration": [
                r"clipboard", r"path", r"project", r"domain", r"technologies"
            ]
        }

        # Negative patterns that reduce quality
        self.low_quality_patterns = [
            r"Please share your opinion", r"What do you think", r"Can you help",
            r"I need help with", r"tell me about", r"simple response",
            r"brief", r"short", r"quick"
        ]

    def score_prompt_quality(self, original_text: str, optimized_text: str,
                           context: Dict = None) -> OptimizationResult:
        """
        Comprehensive quality scoring of prompt optimization.

        Args:
            original_text: Original user input
            optimized_text: Optimized prompt
            context: Additional context (clipboard, etc.)

        Returns:
            OptimizationResult with detailed scoring
        """
        start_time = time.time()

        logger.info(f"🎯 Scoring prompt optimization: '{original_text[:30]}...'")

        # Calculate dimension scores
        dimension_scores = []

        # 1. Clarity Score
        clarity_score = self._score_clarity(original_text, optimized_text)
        dimension_scores.append(clarity_score)

        # 2. Specificity Score
        specificity_score = self._score_specificity(original_text, optimized_text)
        dimension_scores.append(specificity_score)

        # 3. Contextualization Score
        contextualization_score = self._score_contextualization(optimized_text, context)
        dimension_scores.append(contextualization_score)

        # 4. Actionability Score
        actionability_score = self._score_actionability(optimized_text)
        dimension_scores.append(actionability_score)

        # 5. Completeness Score
        completeness_score = self._score_completeness(optimized_text)
        dimension_scores.append(completeness_score)

        # 6. Relevance Score
        relevance_score = self._score_relevance(original_text, optimized_text)
        dimension_scores.append(relevance_score)

        # Calculate overall weighted score
        overall_score = sum(
            score.score * self.quality_weights[score.dimension]
            for score in dimension_scores
        )

        # Calculate improvement ratio
        improvement_ratio = len(optimized_text) / max(len(original_text), 1)

        # Check if optimization was detected
        enhancement_detected = self._detect_optimization_enhancement(optimized_text)

        # Generate recommendations
        recommendations = self._generate_recommendations(dimension_scores, overall_score)

        processing_time = time.time() - start_time

        result = OptimizationResult(
            overall_score=round(overall_score, 2),
            dimension_scores=dimension_scores,
            improvement_ratio=round(improvement_ratio, 2),
            processing_time=round(processing_time * 1000, 2),  # Convert to ms
            enhancement_detected=enhancement_detected,
            recommendations=recommendations
        )

        logger.info(f"📊 Overall Score: {overall_score}/100 (improvement: {improvement_ratio:.1f}x)")
        return result

    def _score_clarity(self, original: str, optimized: str) -> QualityScore:
        """Score prompt clarity and structure."""
        score = 50  # Base score

        # Check for structured format
        if re.search(r'Task:|Context:|Requirements:|Steps:', optimized, re.I):
            score += 20

        # Check for clear sections
        sections = len(re.findall(r'\n\n|\n\s*-', optimized))
        if sections > 2:
            score += 15

        # Penalty for ambiguous language
        ambiguous_terms = ['maybe', 'perhaps', 'possibly', 'might', 'could']
        ambiguous_count = sum(1 for term in ambiguous_terms if term in optimized.lower())
        score -= min(ambiguous_count * 5, 20)

        # Check for professional language
        professional_terms = ['analyze', 'implement', 'design', 'optimize', 'develop']
        professional_count = sum(1 for term in professional_terms if term in optimized.lower())
        score += min(professional_count * 3, 15)

        details = f"Structured format: {'✅' if sections > 2 else '❌'}, Professional terms: {professional_count}"
        suggestions = []
        if score < 70:
            suggestions.append("Add structured sections (Task:, Context:, Requirements:)")
            suggestions.append("Use more professional, specific language")

        return QualityScore(
            dimension=QualityDimension.CLARITY,
            score=max(0, min(100, score)),
            details=details,
            suggestions=suggestions
        )

    def _score_specificity(self, original: str, optimized: str) -> QualityScore:
        """Score prompt specificity and detail level."""
        score = 40  # Base score

        # Check for specific metrics and criteria
        metrics = re.findall(r'\b(kpi|metrics|criteria|benchmark|target\s+\d+%|performance|success)\b', optimized, re.I)
        score += len(metrics) * 10

        # Check for specific technologies or domains
        tech_terms = re.findall(r'\b(python|javascript|react|docker|aws|api|database|frontend|backend)\b', optimized, re.I)
        score += len(tech_terms) * 5

        # Check for specific numbers or measurements
        numbers = re.findall(r'\b\d+%|\b\d+\s+(seconds|minutes|hours|days|steps|items)\b', optimized, re.I)
        score += len(numbers) * 8

        # Penalty for vague terms
        vague_terms = ['good', 'better', 'nice', 'cool', 'awesome', 'great']
        vague_count = sum(1 for term in vague_terms if term in optimized.lower())
        score -= min(vague_count * 8, 25)

        details = f"Metrics: {len(metrics)}, Technologies: {len(tech_terms)}, Numbers: {len(numbers)}"
        suggestions = []
        if score < 70:
            suggestions.append("Add specific success criteria and metrics")
            suggestions.append("Include concrete numbers and measurements")

        return QualityScore(
            dimension=QualityDimension.SPECIFICITY,
            score=max(0, min(100, score)),
            details=details,
            suggestions=suggestions
        )

    def _score_contextualization(self, optimized: str, context: Dict = None) -> QualityScore:
        """Score how well context is integrated."""
        score = 30  # Base score

        # Check for project path integration
        if re.search(r'Target\s+Project:|Project\s+Name:|/[\w\-/]+', optimized):
            score += 25

        # Check for technology context
        if re.search(r'Technical\s+Context:|Technologies:', optimized):
            score += 20

        # Check for domain-specific context
        domains = re.findall(r'\b(engineering|medical|plumbing|development|design|marketing)\b', optimized, re.I)
        score += len(domains) * 10

        # Check for clipboard integration
        if re.search(r'clipboard|context|provided\s+information', optimized, re.I):
            score += 15

        # Bonus for multi-dimensional context
        context_types = 0
        if re.search(r'project|path', optimized, re.I):
            context_types += 1
        if re.search(r'technolog|framework', optimized, re.I):
            context_types += 1
        if re.search(r'domain|field', optimized, re.I):
            context_types += 1

        score += context_types * 10

        details = f"Context types: {context_types}, Domains: {len(domains)}"
        suggestions = []
        if score < 70:
            suggestions.append("Integrate project path and file context")
            suggestions.append("Include domain-specific terminology")

        return QualityScore(
            dimension=QualityDimension.CONTEXTUALIZATION,
            score=max(0, min(100, score)),
            details=details,
            suggestions=suggestions
        )

    def _score_actionability(self, optimized: str) -> QualityScore:
        """Score how actionable the prompt is."""
        score = 40  # Base score

        # Check for action verbs
        action_verbs = re.findall(r'\b(analyze|implement|create|design|develop|test|deploy|optimize|build|evaluate|generate|write|code)\b', optimized, re.I)
        score += len(action_verbs) * 8

        # Check for numbered steps
        numbered_steps = len(re.findall(r'\b\d+\.\s+\w+', optimized))
        score += numbered_steps * 12

        # Check for deliverables
        deliverables = re.findall(r'\b(deliverable|output|result|artifact|product)\b', optimized, re.I)
        score += len(deliverables) * 10

        # Check for clear instructions
        instructions = re.findall(r'\b(provide|generate|create|produce|develop|implement)\b', optimized, re.I)
        score += len(instructions) * 6

        details = f"Action verbs: {len(action_verbs)}, Steps: {numbered_steps}, Deliverables: {len(deliverables)}"
        suggestions = []
        if score < 70:
            suggestions.append("Add clear action verbs and numbered steps")
            suggestions.append("Specify expected deliverables and outputs")

        return QualityScore(
            dimension=QualityDimension.ACTIONABILITY,
            score=max(0, min(100, score)),
            details=details,
            suggestions=suggestions
        )

    def _score_completeness(self, optimized: str) -> QualityScore:
        """Score prompt completeness and coverage."""
        score = 50  # Base score

        # Check for key components
        components = []
        if re.search(r'task|objective|goal', optimized, re.I):
            components.append('task')
        if re.search(r'context|background', optimized, re.I):
            components.append('context')
        if re.search(r'requirements|constraints|criteria', optimized, re.I):
            components.append('requirements')
        if re.search(r'steps|process|methodology', optimized, re.I):
            components.append('steps')
        if re.search(r'output|deliverable|result', optimized, re.I):
            components.append('output')

        score += len(components) * 10

        # Check for quality indicators
        quality_indicators = re.findall(r'\b(best\s+practice|industry\s+standard|professional|expert|optimized|efficient)\b', optimized, re.I)
        score += len(quality_indicators) * 5

        # Check length (reasonable prompt length)
        word_count = len(optimized.split())
        if 50 <= word_count <= 200:
            score += 10
        elif word_count > 200:
            score += 5  # Still good but might be too long

        details = f"Components: {len(components)}/5, Quality indicators: {len(quality_indicators)}, Words: {word_count}"
        suggestions = []
        if len(components) < 3:
            suggestions.append("Include task, context, requirements, and output sections")
        if word_count < 30:
            suggestions.append("Add more detail and specificity")

        return QualityScore(
            dimension=QualityDimension.COMPLETENESS,
            score=max(0, min(100, score)),
            details=details,
            suggestions=suggestions
        )

    def _score_relevance(self, original: str, optimized: str) -> QualityScore:
        """Score how relevant the optimization is to the original request."""
        score = 60  # Base score

        # Extract key concepts from original
        original_words = set(re.findall(r'\b\w{3,}\b', original.lower()))
        optimized_words = set(re.findall(r'\b\w{3,}\b', optimized.lower()))

        # Calculate concept overlap
        if original_words:
            overlap = len(original_words & optimized_words)
            score += min(overlap * 10, 30)

        # Check for preserved intent
        intent_preserved = True
        if any(word in original.lower() for word in ['help', 'how', 'what', 'why']):
            if not re.search(r'\b(how|what|why|explain|describe|analyze)\b', optimized, re.I):
                intent_preserved = False

        if intent_preserved:
            score += 10
        else:
            score -= 20

        # Check for enhancement vs distortion
        if len(optimized) < len(original) * 0.5:
            score -= 30  # Too much lost

        details = f"Concept overlap: {overlap if 'overlap' in locals() else 0}, Intent preserved: {'✅' if intent_preserved else '❌'}"
        suggestions = []
        if score < 70:
            suggestions.append("Preserve key concepts from original request")
            suggestions.append("Ensure original intent is maintained")

        return QualityScore(
            dimension=QualityDimension.RELEVANCE,
            score=max(0, min(100, score)),
            details=details,
            suggestions=suggestions
        )

    def _detect_optimization_enhancement(self, optimized: str) -> bool:
        """Detect if the prompt shows signs of optimization enhancement."""
        enhancement_indicators = [
            r"Act as an expert",
            r"Target Project:",
            r"Technical Context:",
            r"Domain:",
            r"complexity",
            r"Requirements:",
            r"Success Criteria:",
            r"Implementation Steps:",
            r"best practices",
            r"following industry standards"
        ]

        return any(re.search(pattern, optimized, re.I) for pattern in enhancement_indicators)

    def _generate_recommendations(self, dimension_scores: List[QualityScore], overall_score: float) -> List[str]:
        """Generate improvement recommendations based on scores."""
        recommendations = []

        # Priority recommendations based on lowest scoring dimensions
        low_scoring = sorted(dimension_scores, key=lambda x: x.score)[:2]

        for score in low_scoring:
            if score.score < 70:
                recommendations.extend(score.suggestions[:2])  # Top 2 suggestions per dimension

        # Overall recommendations
        if overall_score < 60:
            recommendations.append("Consider rewriting with more structure and specificity")
            recommendations.append("Focus on integrating context and making it actionable")
        elif overall_score < 80:
            recommendations.append("Good foundation - enhance with more specific metrics and criteria")

        return list(set(recommendations))  # Remove duplicates

    def create_score_report(self, result: OptimizationResult) -> str:
        """Generate a comprehensive score report."""
        report = []
        report.append("🎯 PROMPT OPTIMIZATION QUALITY REPORT")
        report.append("=" * 50)

        # Overall score
        grade = self._get_grade(result.overall_score)
        report.append(f"📊 Overall Score: {result.overall_score}/100 ({grade})")
        report.append(f"📈 Improvement Ratio: {result.improvement_ratio}x")
        report.append(f"⚡ Processing Time: {result.processing_time}ms")
        report.append(f"✨ Enhancement Detected: {'Yes' if result.enhancement_detected else 'No'}")
        report.append("")

        # Dimension scores
        report.append("📋 Dimension Scores:")
        for score in result.dimension_scores:
            status = "🟢" if score.score >= 80 else "🟡" if score.score >= 60 else "🔴"
            report.append(f"  {status} {score.dimension.value.title()}: {score.score}/100")
            report.append(f"      → {score.details}")
            if score.suggestions:
                for suggestion in score.suggestions:
                    report.append(f"      💡 {suggestion}")
        report.append("")

        # Recommendations
        if result.recommendations:
            report.append("🚀 Improvement Recommendations:")
            for i, rec in enumerate(result.recommendations, 1):
                report.append(f"  {i}. {rec}")

        return "\n".join(report)

    def _get_grade(self, score: float) -> str:
        """Convert numerical score to grade."""
        if score >= 90:
            return "A+ (Excellent)"
        elif score >= 85:
            return "A (Very Good)"
        elif score >= 80:
            return "A- (Good)"
        elif score >= 75:
            return "B+ (Above Average)"
        elif score >= 70:
            return "B (Average)"
        elif score >= 65:
            return "B- (Below Average)"
        elif score >= 60:
            return "C (Needs Improvement)"
        elif score >= 50:
            return "D (Poor)"
        else:
            return "F (Very Poor)"

# Global instance
prompt_scorer = PromptQualityScorer()