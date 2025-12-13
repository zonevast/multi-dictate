#!/usr/bin/env python3
"""
Comprehensive benchmarking system for prompt optimization.
Tests various scenarios and provides performance metrics.
"""

import time
import json
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

from .prompt_quality_scorer import PromptQualityScorer, OptimizationResult

logger = logging.getLogger(__name__)

@dataclass
class BenchmarkCase:
    """Single benchmark test case."""
    name: str
    original_input: str
    clipboard_context: str = ""
    expected_keywords: List[str] = None
    min_expected_score: float = 70.0
    category: str = "general"

@dataclass
class BenchmarkResults:
    """Complete benchmark results."""
    total_tests: int
    passed_tests: int
    failed_tests: int
    average_score: float
    average_improvement_ratio: float
    total_processing_time: float
    test_results: List[Dict]
    passed: bool
    summary: str

class OptimizationBenchmark:
    """Comprehensive benchmarking system for prompt optimization."""

    def __init__(self):
        self.scorer = PromptQualityScorer()
        self.test_cases = self._create_test_cases()

    def _create_test_cases(self) -> List[BenchmarkCase]:
        """Create comprehensive test cases."""
        return [
            # Path-based optimization tests
            BenchmarkCase(
                name="Project Path Test 1",
                original_input="test this project and tell me summary",
                clipboard_context="/home/yousef/multi-dictate",
                expected_keywords=["multi-dictate", "python", "project"],
                min_expected_score=80.0,
                category="path_optimization"
            ),
            BenchmarkCase(
                name="Project Path Test 2",
                original_input="analyze this codebase",
                clipboard_context="/home/yousef/multi-dictate/multi_dictate/dictate.py",
                expected_keywords=["dictate.py", "python", "analyze"],
                min_expected_score=75.0,
                category="path_optimization"
            ),
            BenchmarkCase(
                name="Generic Path Test",
                original_input="optimize performance",
                clipboard_context="/var/www/html/react-app",
                expected_keywords=["react", "frontend", "performance"],
                min_expected_score=75.0,
                category="path_optimization"
            ),

            # Domain-specific tests
            BenchmarkCase(
                name="Medical Domain Test",
                original_input="help with patient data system",
                clipboard_context="hospital patient management system",
                expected_keywords=["medical", "patient", "healthcare"],
                min_expected_score=70.0,
                category="domain_specific"
            ),
            BenchmarkCase(
                name="Engineering Test",
                original_input="design plumbing system",
                clipboard_context="residential building plumbing",
                expected_keywords=["plumbing", "water", "system"],
                min_expected_score=70.0,
                category="domain_specific"
            ),

            # Complex scenario tests
            BenchmarkCase(
                name="Complex Migration Test",
                original_input="migrate monolith to microservices",
                clipboard_context="large enterprise application",
                expected_keywords=["microservices", "migration", "architecture"],
                min_expected_score=80.0,
                category="complex_scenario"
            ),
            BenchmarkCase(
                name="Performance Optimization Test",
                original_input="fix slow api responses",
                clipboard_context="e-commerce backend service",
                expected_keywords=["api", "performance", "optimization"],
                min_expected_score=75.0,
                category="complex_scenario"
            ),

            # Simple enhancement tests
            BenchmarkCase(
                name="Simple Task Test",
                original_input="write function to validate email",
                clipboard_context="",
                expected_keywords=["function", "email", "validate"],
                min_expected_score=65.0,
                category="simple_enhancement"
            ),
            BenchmarkCase(
                name="Debug Request Test",
                original_input="debug authentication error",
                clipboard_context="login system throwing 401",
                expected_keywords=["debug", "authentication", "error"],
                min_expected_score=70.0,
                category="simple_enhancement"
            ),

            # Edge cases
            BenchmarkCase(
                name="Very Short Input",
                original_input="help",
                clipboard_context="",
                expected_keywords=["help"],
                min_expected_score=50.0,
                category="edge_case"
            ),
            BenchmarkCase(
                name="No Clear Intent",
                original_input="the rock this a project",
                clipboard_context="/home/yousef/multi-dictate",
                expected_keywords=["project", "rock"],
                min_expected_score=60.0,
                category="edge_case"
            ),
        ]

    def run_benchmark(self, prompt_engineering_optimizer) -> BenchmarkResults:
        """
        Run comprehensive benchmark tests.

        Args:
            prompt_engineering_optimizer: The optimizer to test

        Returns:
            BenchmarkResults with comprehensive metrics
        """
        logger.info("🚀 Starting prompt optimization benchmark")
        start_time = time.time()

        test_results = []
        passed_tests = 0
        total_score = 0
        total_improvement = 0

        for i, test_case in enumerate(self.test_cases, 1):
            logger.info(f"📋 Running test {i}/{len(self.test_cases)}: {test_case.name}")

            # Run optimization
            try:
                optimization_start = time.time()
                result = prompt_engineering_optimizer.optimize_prompt(
                    test_case.original_input,
                    test_case.clipboard_context
                )
                optimization_time = (time.time() - optimization_start) * 1000

                # Score the result
                context = {"clipboard": test_case.clipboard_context}
                quality_result = self.scorer.score_prompt_quality(
                    test_case.original_input,
                    result["optimized_prompt"],
                    context
                )

                # Check if test passed
                test_passed = (
                    quality_result.overall_score >= test_case.min_expected_score and
                    all(keyword.lower() in result["optimized_prompt"].lower()
                        for keyword in (test_case.expected_keywords or []))
                )

                if test_passed:
                    passed_tests += 1

                total_score += quality_result.overall_score
                total_improvement += quality_result.improvement_ratio

                # Store detailed results
                test_result = {
                    "test_name": test_case.name,
                    "category": test_case.category,
                    "passed": test_passed,
                    "score": quality_result.overall_score,
                    "improvement_ratio": quality_result.improvement_ratio,
                    "processing_time": optimization_time,
                    "original_input": test_case.original_input,
                    "optimized_prompt": result["optimized_prompt"][:200] + "..." if len(result["optimized_prompt"]) > 200 else result["optimized_prompt"],
                    "min_expected_score": test_case.min_expected_score,
                    "expected_keywords_found": [
                        kw for kw in (test_case.expected_keywords or [])
                        if kw.lower() in result["optimized_prompt"].lower()
                    ],
                    "missing_keywords": [
                        kw for kw in (test_case.expected_keywords or [])
                        if kw.lower() not in result["optimized_prompt"].lower()
                    ]
                }
                test_results.append(test_result)

                # Log result
                status = "✅" if test_passed else "❌"
                logger.info(f"  {status} Score: {quality_result.overall_score}/100 (expected: {test_case.min_expected_score})")

            except Exception as e:
                logger.error(f"  ❌ Test failed with exception: {e}")
                test_results.append({
                    "test_name": test_case.name,
                    "category": test_case.category,
                    "passed": False,
                    "error": str(e),
                    "score": 0
                })

        # Calculate final metrics
        total_time = time.time() - start_time
        failed_tests = len(self.test_cases) - passed_tests
        average_score = total_score / len(self.test_cases)
        average_improvement = total_improvement / len(self.test_cases)

        # Generate summary
        success_rate = (passed_tests / len(self.test_cases)) * 100
        passed = success_rate >= 80  # 80% pass rate required

        if passed:
            summary = f"✅ BENCHMARK PASSED: {passed_tests}/{len(self.test_cases)} tests ({success_rate:.1f}%) - Average Score: {average_score:.1f}/100"
        else:
            summary = f"❌ BENCHMARK FAILED: {passed_tests}/{len(self.test_cases)} tests ({success_rate:.1f}%) - Average Score: {average_score:.1f}/100"

        results = BenchmarkResults(
            total_tests=len(self.test_cases),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            average_score=round(average_score, 2),
            average_improvement_ratio=round(average_improvement, 2),
            total_processing_time=round(total_time * 1000, 2),
            test_results=test_results,
            passed=passed,
            summary=summary
        )

        logger.info(summary)
        return results

    def create_benchmark_report(self, results: BenchmarkResults) -> str:
        """Generate comprehensive benchmark report."""
        report = []
        report.append("🎯 PROMPT OPTIMIZATION BENCHMARK REPORT")
        report.append("=" * 60)

        # Overall summary
        status = "✅ PASSED" if results.passed else "❌ FAILED"
        report.append(f"📊 Overall Status: {status}")
        report.append(f"📈 Success Rate: {results.passed_tests}/{results.total_tests} ({(results.passed_tests/results.total_tests)*100:.1f}%)")
        report.append(f"🎯 Average Score: {results.average_score}/100")
        report.append(f"📈 Average Improvement: {results.average_improvement_ratio}x")
        report.append(f"⚡ Total Time: {results.total_processing_time}ms")
        report.append("")

        # Category breakdown
        category_stats = {}
        for result in results.test_results:
            category = result.get("category", "unknown")
            if category not in category_stats:
                category_stats[category] = {"passed": 0, "total": 0, "scores": []}

            category_stats[category]["total"] += 1
            if result.get("passed", False):
                category_stats[category]["passed"] += 1
            if "score" in result:
                category_stats[category]["scores"].append(result["score"])

        report.append("📋 Category Performance:")
        for category, stats in sorted(category_stats.items()):
            success_rate = (stats["passed"] / stats["total"]) * 100
            avg_score = sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else 0
            status = "🟢" if success_rate >= 80 else "🟡" if success_rate >= 60 else "🔴"
            report.append(f"  {status} {category.replace('_', ' ').title()}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%) - Avg: {avg_score:.1f}/100")

        report.append("")

        # Failed tests details
        failed_tests = [r for r in results.test_results if not r.get("passed", False)]
        if failed_tests:
            report.append("❌ Failed Tests:")
            for test in failed_tests:
                report.append(f"  • {test['test_name']} ({test.get('category', 'unknown')})")
                if "score" in test:
                    report.append(f"      Score: {test['score']}/100 (expected: {test.get('min_expected_score', 'N/A')})")
                if "missing_keywords" in test and test["missing_keywords"]:
                    report.append(f"      Missing keywords: {', '.join(test['missing_keywords'])}")
                if "error" in test:
                    report.append(f"      Error: {test['error']}")

        report.append("")

        # Top performing tests
        top_tests = sorted([r for r in results.test_results if "score" in r],
                          key=lambda x: x["score"], reverse=True)[:3]
        if top_tests:
            report.append("🏆 Top Performing Tests:")
            for i, test in enumerate(top_tests, 1):
                report.append(f"  {i}. {test['test_name']}: {test['score']}/100")

        # Recommendations
        report.append("")
        report.append("💡 Recommendations:")
        if not results.passed:
            report.append("  • Overall benchmark performance below threshold")
            report.append("  • Review failed tests and improve optimization logic")

        if results.average_score < 75:
            report.append("  • Average score below optimal - enhance prompt quality")

        for category, stats in category_stats.items():
            success_rate = (stats["passed"] / stats["total"]) * 100
            if success_rate < 80:
                report.append(f"  • Improve performance in {category.replace('_', ' ').title()} category")

        return "\n".join(report)

    def save_benchmark_results(self, results: BenchmarkResults, filepath: str):
        """Save benchmark results to JSON file."""
        results_dict = asdict(results)
        with open(filepath, 'w') as f:
            json.dump(results_dict, f, indent=2)
        logger.info(f"📁 Benchmark results saved to {filepath}")

# Global benchmark instance
benchmark = OptimizationBenchmark()