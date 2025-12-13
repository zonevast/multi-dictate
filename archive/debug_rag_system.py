#!/usr/bin/env python3
"""
Comprehensive RAG System Debugger and Tester
Tests scenarios, detects issues, and shows optimization steps
"""

import sys
import os
import time
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

from multi_dictate.simple_rag_processor import SimpleRAGProcessor
from multi_dictate.file_context_reader import FileContextReader

class MockConfig:
    def __init__(self):
        self.general = {
            'storage_path': '~/.config/multi-dictate',
            'rag_enabled': True,
            'embedding': 'onnx'
        }

class RAGDebugger:
    def __init__(self):
        self.config = MockConfig()
        self.processor = SimpleRAGProcessor(self.config)
        self.file_reader = FileContextReader()
        self.test_results = []
        self.optimization_steps = []

    def log_step(self, step_name: str, duration: float, details: str = "", success: bool = True):
        """Log optimization step"""
        step = {
            'step': step_name,
            'duration': duration,
            'details': details,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        self.optimization_steps.append(step)

        status = "✅" if success else "❌"
        print(f"{status} [{duration:.3f}s] {step_name}")
        if details:
            print(f"    → {details}")

    def run_comprehensive_debug(self):
        """Run comprehensive RAG debugging"""
        print("🔍 RAG SYSTEM COMPREHENSIVE DEBUGGER")
        print("=" * 80)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Initialize timing
        start_time = time.time()
        step_start = start_time

        # Scenario 1: Basic ChromaDB functionality
        print("🧪 SCENARIO 1: ChromaDB Memory System")
        print("-" * 50)
        step_start = time.time()

        try:
            stats = self.processor.get_learning_stats()
            self.log_step(
                "ChromaDB Initialization",
                time.time() - step_start,
                f"Patterns: {stats.get('total_patterns', 0)}, Knowledge: {stats.get('total_knowledge', 0)}",
                True
            )
        except Exception as e:
            self.log_step(
                "ChromaDB Initialization",
                time.time() - step_start,
                f"Error: {e}",
                False
            )

        # Scenario 2: Pattern matching test
        print(f"\n🧪 SCENARIO 2: Pattern Matching Test")
        print("-" * 50)
        step_start = time.time()

        test_query = "fix database connection timeout error"
        try:
            patterns = self.processor.find_similar_patterns(test_query, max_results=3)
            self.log_step(
                "Pattern Search",
                time.time() - step_start,
                f"Found {len(patterns)} similar patterns for '{test_query}'",
                True
            )

            # Test pattern quality
            if patterns:
                best_similarity = max(p.get('similarity', 0) for p in patterns)
                self.log_step(
                    "Pattern Quality Check",
                    0,
                    f"Best similarity: {best_similarity:.2f}",
                    best_similarity > 0.1
                )

        except Exception as e:
            self.log_step(
                "Pattern Search",
                time.time() - step_start,
                f"Error: {e}",
                False
            )

        # Scenario 3: File reading test
        print(f"\n🧪 SCENARIO 3: File Context Reading")
        print("-" * 50)
        step_start = time.time()

        test_path = "/home/yousef/Documents/workspace/zonevast/"
        try:
            file_result = self.file_reader.read_from_clipboard(test_path)
            self.log_step(
                "File Reading",
                time.time() - step_start,
                f"Read {file_result.get('files_found', 0)} files from '{test_path}'",
                file_result.get('success', False)
            )

            # Check if workflow rules found
            if file_result.get('success') and 'workflow_rules.md' in file_result.get('content', '').lower():
                self.log_step(
                    "Workflow Rules Detection",
                    0,
                    "WORKFLOW_RULES.md found and read",
                    True
                )
            else:
                self.log_step(
                    "Workflow Rules Detection",
                    0,
                    "WORKFLOW_RULES.md not found",
                    False
                )

        except Exception as e:
            self.log_step(
                "File Reading",
                time.time() - step_start,
                f"Error: {e}",
                False
            )

        # Scenario 4: End-to-end RAG enhancement
        print(f"\n🧪 SCENARIO 4: End-to-End RAG Enhancement")
        print("-" * 50)

        test_requests = [
            {
                'name': 'Programming Fix Request',
                'input': 'how to fix null pointer exception in python',
                'clipboard': '',
                'expected_enhancement': True
            },
            {
                'name': 'Workflow + File Context',
                'input': 'apply workflow rules for testing backend to frontend',
                'clipboard': test_path,
                'expected_enhancement': True
            },
            {
                'name': 'Productivity Enhancement',
                'input': 'feeling unmotivated and need creative ideas',
                'clipboard': '',
                'expected_enhancement': True
            },
            {
                'name': 'Generic Request',
                'input': 'tell me about artificial intelligence',
                'clipboard': '',
                'expected_enhancement': False  # No specific enhancement needed
            },
            {
                'name': 'Complex Multi-Context',
                'input': 'implement error handling following best practices',
                'clipboard': test_path,
                'expected_enhancement': True
            }
        ]

        for i, scenario in enumerate(test_requests, 1):
            print(f"\n📝 Test 4.{i}: {scenario['name']}")
            step_start = time.time()

            try:
                context = {'clipboard': scenario['clipboard']} if scenario['clipboard'] else {}
                enhanced, metadata = self.processor.process_with_context(scenario['input'], context)

                enhancement_applied = metadata.get('simple_rag_used', False)
                patterns_found = metadata.get('patterns_found', 0)

                self.log_step(
                    f"RAG Enhancement - {scenario['name']}",
                    time.time() - step_start,
                    f"Enhanced: {enhancement_applied}, Patterns: {patterns_found}",
                    enhancement_applied == scenario['expected_enhancement']
                )

                # Quality check
                quality_score = self._calculate_quality_score(enhanced, scenario['input'], scenario['clipboard'])
                self.log_step(
                    f"Quality Score - {scenario['name']}",
                    0,
                    f"Score: {quality_score}/100",
                    quality_score >= 70
                )

            except Exception as e:
                self.log_step(
                    f"RAG Enhancement - {scenario['name']}",
                    time.time() - step_start,
                    f"Error: {e}",
                    False
                )

        # Scenario 5: Performance optimization check
        print(f"\n🧪 SCENARIO 5: Performance Optimization Check")
        print("-" * 50)

        # Test response times
        response_times = []
        for _ in range(5):
            step_start = time.time()
            try:
                self.processor.process_with_context("test request", {})
                response_time = time.time() - step_start
                response_times.append(response_time)
            except:
                response_times.append(999)  # Error

        avg_time = sum(response_times) / len(response_times)
        self.log_step(
            "Average Response Time",
            0,
            f"Average: {avg_time:.3f}s over 5 requests",
            avg_time < 2.0
        )

        # Scenario 6: Memory and storage check
        print(f"\n🧪 SCENARIO 6: Memory and Storage Check")
        print("-" * 50)

        try:
            step_start = time.time()

            # Test pattern storage
            test_pattern = "fix api authentication token issue"
            test_solution = "Use JWT tokens with proper expiration handling"
            pattern_id = self.processor.store_pattern(test_pattern, test_solution)

            self.log_step(
                "Pattern Storage",
                time.time() - step_start,
                f"Stored pattern: {pattern_id}",
                bool(pattern_id)
            )

            # Test retrieval
            step_start = time.time()
            retrieved = self.processor.find_similar_patterns("authentication token error", max_results=1)

            self.log_step(
                "Pattern Retrieval",
                time.time() - step_start,
                f"Retrieved {len(retrieved)} patterns",
                len(retrieved) > 0
            )

        except Exception as e:
            self.log_step(
                "Memory Operations",
                time.time() - step_start,
                f"Error: {e}",
                False
            )

        # Generate final report
        self.generate_debug_report()

    def _calculate_quality_score(self, enhanced_output: str, original_input: str, clipboard_content: str) -> int:
        """Calculate quality score for RAG enhancement - more realistic scoring"""
        score = 50  # Base score for processing successfully

        # Check if enhancement was applied (not just original input)
        if enhanced_output != original_input:
            score += 20

        # Check for structured elements
        if "Current Request:" in enhanced_output:
            score += 10

        # Check if patterns included
        if "Relevant Past Solutions:" in enhanced_output or "💾" in enhanced_output:
            score += 15

        # Check if knowledge included
        if "Knowledge" in enhanced_output or "productivity" in enhanced_output or "programming" in enhanced_output:
            score += 10

        # Check if file context included (when clipboard provided)
        if clipboard_content and "File Context" in enhanced_output:
            score += 15

        # Check for professional formatting
        if len(enhanced_output) > 100 and len(enhanced_output) > len(original_input):
            score += 10

        # Penalty for truncation (shows incomplete processing)
        if "..." in enhanced_output and enhanced_output.count("...") > 1:
            score -= 5

        # Bonus for context-appropriate enhancement
        if "workflow" in original_input.lower() and "workflow" in enhanced_output.lower():
            score += 5

        if "debug" in original_input.lower() and "error" in enhanced_output.lower():
            score += 5

        return max(0, min(score, 100))

    def generate_debug_report(self):
        """Generate comprehensive debug report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE RAG DEBUG REPORT")
        print("=" * 80)

        # Calculate statistics
        total_steps = len(self.optimization_steps)
        successful_steps = sum(1 for step in self.optimization_steps if step['success'])
        success_rate = (successful_steps / total_steps * 100) if total_steps > 0 else 0

        # Timing analysis
        total_time = sum(step['duration'] for step in self.optimization_steps if step['duration'] > 0)
        avg_step_time = total_time / len([s for s in self.optimization_steps if s['duration'] > 0]) if self.optimization_steps else 0

        print(f"📈 OVERALL PERFORMANCE:")
        print(f"   Success Rate: {success_rate:.1f}% ({successful_steps}/{total_steps})")
        print(f"   Total Processing Time: {total_time:.3f}s")
        print(f"   Average Step Time: {avg_step_time:.3f}s")

        print(f"\n🔍 ISSUE ANALYSIS:")

        # Identify issues
        issues = []
        for step in self.optimization_steps:
            if not step['success']:
                issues.append(f"❌ {step['step']}: {step['details']}")

        if issues:
            print("   Issues Found:")
            for issue in issues[:5]:  # Show top 5 issues
                print(f"      {issue}")
        else:
            print("   ✅ No critical issues detected")

        print(f"\n⚡ OPTIMIZATION ANALYSIS:")

        # Performance issues
        slow_steps = [step for step in self.optimization_steps if step['duration'] > 1.0]
        if slow_steps:
            print("   Performance Bottlenecks:")
            for step in slow_steps:
                print(f"      ⏰ {step['step']}: {step['duration']:.3f}s")
        else:
            print("   ✅ All steps performing well")

        print(f"\n💡 RECOMMENDATIONS:")

        if success_rate >= 90:
            print("   🎉 EXCELLENT: RAG system is working optimally!")
        elif success_rate >= 80:
            print("   ✅ GOOD: RAG system is working well with minor improvements possible")
        elif success_rate >= 70:
            print("   ⚠️ FAIR: RAG system needs some improvements")
        else:
            print("   ❌ POOR: RAG system requires significant improvements")

        # Specific recommendations
        if not issues and avg_step_time > 0.5:
            print("   🚀 Consider performance optimization for faster response times")

        if "Pattern Search" in [step['step'] for step in self.optimization_steps if not step['success']]:
            print("   🔧 Check ChromaDB initialization and embedding functions")

        if "File Reading" in [step['step'] for step in self.optimization_steps if not step['success']]:
            print("   📁 Verify file permissions and path accessibility")

        print(f"\n📋 STEP-BY-STEP OPTIMIZATION:")
        for i, step in enumerate(self.optimization_steps, 1):
            status = "✅" if step['success'] else "❌"
            time_str = f"({step['duration']:.3f}s)" if step['duration'] > 0 else ""
            print(f"   {i:2d}. {status} {step['step']} {time_str}")
            if step['details']:
                print(f"       → {step['details']}")

        print(f"\n🎯 FINAL STATUS: {'HEALTHY' if success_rate >= 80 else 'NEEDS ATTENTION'}")
        print("=" * 80)

def main():
    debugger = RAGDebugger()
    debugger.run_comprehensive_debug()

if __name__ == '__main__':
    main()