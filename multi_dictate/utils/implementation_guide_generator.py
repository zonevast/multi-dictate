#!/usr/bin/env python3
"""
Implementation Guide Generator
Generates detailed step-by-step implementation guides with code examples
and testing procedures for RAG-enhanced responses
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class ImplementationGuideGenerator:
    """Generates structured implementation guides with testing procedures"""

    def __init__(self):
        self.test_commands = {
            'javascript': {
                'unit_test': 'npm test -- --testPathPattern={test_pattern}',
                'integration_test': 'curl -X GET http://localhost:3000{endpoint}',
                'performance_test': 'lighthouse http://localhost:3000{endpoint} --output=json',
                'debug': 'npm run dev:debug'
            },
            'python': {
                'unit_test': 'python3 -m pytest tests/{test_pattern}.py -v',
                'integration_test': 'python3 test_api.py',
                'performance_test': 'python3 -m pytest tests/performance/ -v',
                'debug': 'python3 -m pdb app.py'
            },
            'java': {
                'unit_test': './mvnw test -Dtest={test_class}',
                'integration_test': 'curl -X GET http://localhost:8080{endpoint}',
                'performance_test': 'jmeter -n -t load_test.jmx',
                'debug': './mvnw spring-boot:run -Dspring-boot.run.jvmArguments="-Xdebug"'
            },
            'general': {
                'verify_response': 'curl -v {url}',
                'check_logs': 'tail -f {log_file}',
                'monitor_performance': 'top -p {pid}'
            }
        }

        self.complexity_time_estimates = {
            'low': {'min_time': 5, 'max_time': 30, 'avg_time': 15},
            'medium': {'min_time': 30, 'max_time': 120, 'avg_time': 60},
            'high': {'min_time': 120, 'max_time': 480, 'avg_time': 240}
        }

    def generate_guide(self,
                       structured_solution: Dict,
                       file_analysis: List[Dict] = None,
                       pattern_info: Dict = None) -> Dict:
        """Generate complete implementation guide"""

        guide = {
            'timestamp': datetime.now().isoformat(),
            'analysis': self._generate_analysis_section(file_analysis, pattern_info),
            'implementation_steps': self._generate_implementation_steps(structured_solution),
            'testing_procedures': self._generate_testing_procedures(structured_solution, file_analysis),
            'expected_results': self._generate_expected_results(structured_solution, pattern_info),
            'debug_commands': self._generate_debug_commands(structured_solution)
        }

        return guide

    def _generate_analysis_section(self,
                                  file_analysis: List[Dict] = None,
                                  pattern_info: Dict = None) -> Dict:
        """Generate the Analysis section with file references and pattern info"""

        analysis = {
            'files_with_issues': [],
            'pattern_references': [],
            'issue_summary': ''
        }

        # Process file analysis
        if file_analysis:
            for file_result in file_analysis:
                if file_result.get('total_issues', 0) > 0:
                    file_info = {
                        'path': file_result['file_path'],
                        'issues': []
                    }

                    for issue in file_result['issues_found'][:5]:  # Limit to top 5 issues
                        file_info['issues'].append({
                            'line': issue.get('line', 'N/A'),
                            'description': issue['description'],
                            'severity': issue.get('severity', 'medium'),
                            'type': issue.get('type', 'code_quality')  # Default type if not provided
                        })

                    analysis['files_with_issues'].append(file_info)

        # Process pattern information
        if pattern_info:
            for pattern in pattern_info:
                pattern_ref = {
                    'id': pattern['id'],
                    'similarity': pattern.get('similarity', 0),
                    'success_rate': pattern.get('success_rate', 0),
                    'category': pattern.get('category', 'general'),
                    'usage_count': pattern.get('total_usage', 0)
                }

                if pattern.get('has_structured_solution'):
                    pattern_ref.update({
                        'estimated_time': pattern.get('estimated_time', 'Unknown'),
                        'complexity': pattern.get('complexity', 'medium')
                    })

                analysis['pattern_references'].append(pattern_ref)

        # Generate summary
        total_issues = sum(len(f['issues']) for f in analysis['files_with_issues'])
        high_severity_issues = sum(
            len([i for i in f['issues'] if i['severity'] == 'high'])
            for f in analysis['files_with_issues']
        )

        if total_issues > 0:
            analysis['issue_summary'] = (
                f"Found {total_issues} issues across {len(analysis['files_with_issues'])} files. "
                f"{high_severity_issues} high-priority issues need immediate attention."
            )
        else:
            # Check if we have a URL to optimize
            if hasattr(self, '_current_url') and self._current_url:
                analysis['issue_summary'] = "Page optimization recommended for better performance and user experience."
            else:
                analysis['issue_summary'] = "No critical issues detected in the provided files."

        return analysis

    def _generate_implementation_steps(self, structured_solution: Dict) -> List[Dict]:
        """Generate detailed implementation steps"""

        if not structured_solution or 'implementation_steps' not in structured_solution:
            # Check if we have a URL to optimize (from self._current_url)
            print(f"🐛 GUIDE DEBUG: hasattr _current_url={hasattr(self, '_current_url')}")
            if hasattr(self, '_current_url'):
                print(f"🐛 GUIDE DEBUG: _current_url value={self._current_url}")

            if hasattr(self, '_current_url') and self._current_url:
                return [
                    {
                        'step_number': 1,
                        'title': 'Analyze current page implementation',
                        'description': 'Review the existing page structure and identify optimization opportunities',
                        'estimated_time': 15,
                        'files_affected': []
                    },
                    {
                        'step_number': 2,
                        'title': 'Optimize page performance',
                        'description': 'Improve loading times and resource efficiency',
                        'estimated_time': 30,
                        'files_affected': []
                    },
                    {
                        'step_number': 3,
                        'title': 'Test optimization changes',
                        'description': 'Verify all functionality works correctly after optimizations',
                        'estimated_time': 15,
                        'files_affected': []
                    }
                ]
            return []

        steps = []
        implementation_steps = structured_solution['implementation_steps']

        for i, step in enumerate(implementation_steps, 1):
            step_guide = {
                'step_number': i,
                'title': step.get('action', f'Step {i}'),
                'description': step.get('description', ''),
                'estimated_time': step.get('time', 15),
                'files_affected': []
            }

            # Handle code changes
            if 'code' in step:
                step_guide['code_changes'] = []
                code_info = step['code']

                if isinstance(code_info, dict):
                    # Single code change
                    if 'file' in code_info:
                        step_guide['files_affected'].append(code_info['file'])
                        step_guide['code_changes'].append({
                            'file': code_info['file'],
                            'line': code_info.get('line', 'N/A'),
                            'before': code_info.get('before', ''),
                            'after': code_info.get('after', '')
                        })

                elif isinstance(code_info, list):
                    # Multiple code changes
                    for change in code_info:
                        if 'file' in change:
                            step_guide['files_affected'].append(change['file'])
                            step_guide['code_changes'].append({
                                'file': change['file'],
                                'line': change.get('line', 'N/A'),
                                'before': change.get('before', ''),
                                'after': change.get('after', '')
                            })

            # Add other step details
            if 'dependencies' in step:
                step_guide['dependencies'] = step['dependencies']
            if 'verification' in step:
                step_guide['verification'] = step['verification']

            steps.append(step_guide)

        return steps

    def _generate_testing_procedures(self,
                                    structured_solution: Dict,
                                    file_analysis: List[Dict] = None) -> List[Dict]:
        """Generate testing procedures"""

        testing_procedures = []

        # Add testing from structured solution
        if structured_solution and 'testing_procedures' in structured_solution:
            for test in structured_solution['testing_procedures']:
                test_procedure = {
                    'type': test.get('type', 'manual'),
                    'title': f"{test.get('type', 'Test').title()} Verification",
                    'description': test.get('description', ''),
                    'command': test.get('command', ''),
                    'expected_result': test.get('expected_result', 'Should work correctly')
                }
                testing_procedures.append(test_procedure)

        # Generate automatic tests based on file types
        if file_analysis:
            file_types = set()
            for file_result in file_analysis:
                if 'file_path' in file_result:
                    file_type = self._detect_file_type(file_result['file_path'])
                    if file_type:
                        file_types.add(file_type)

            for file_type in file_types:
                if file_type in self.test_commands:
                    # Add unit test
                    testing_procedures.append({
                        'type': 'unit_test',
                        'title': f'Unit Test for {file_type.title()}',
                        'description': f'Run unit tests for {file_type} files',
                        'command': self.test_commands[file_type]['unit_test'].format(
                            test_pattern='*'  # Generic pattern
                        ),
                        'expected_result': 'All tests pass'
                    })

                    # Add integration test for web-related files
                    if file_type in ['javascript', 'python', 'java']:
                        testing_procedures.append({
                            'type': 'integration_test',
                            'title': 'API Integration Test',
                            'description': 'Test the API endpoints',
                            'command': self.test_commands[file_type]['integration_test'].format(
                                endpoint='/api/test'
                            ),
                            'expected_result': 'API responds correctly'
                        })

        # Add general verification steps
        testing_procedures.extend([
            {
                'type': 'verification',
                'title': 'Manual Verification',
                'description': 'Verify the changes work in the browser/application',
                'command': self.test_commands['general']['verify_response'].format(url='YOUR_URL_HERE'),
                'expected_result': 'Page loads correctly with dynamic data'
            },
            {
                'type': 'performance_check',
                'title': 'Performance Check',
                'description': 'Check if performance has improved',
                'command': 'Monitor load times and resource usage',
                'expected_result': 'Improved performance metrics'
            }
        ])

        return testing_procedures

    def _generate_expected_results(self,
                                 structured_solution: Dict,
                                 pattern_info: Dict = None) -> Dict:
        """Generate expected results section"""

        expected_results = {
            'performance_improvements': [],
            'reliability_improvements': [],
            'maintainability_improvements': [],
            'success_probability': 0.8,  # Default
            'estimated_impact': 'medium'
        }

        # Extract from structured solution
        if structured_solution and 'expected_results' in structured_solution:
            results = structured_solution['expected_results']
            if 'performance' in results:
                expected_results['performance_improvements'].append(results['performance'])
            if 'reliability' in results:
                expected_results['reliability_improvements'].append(results['reliability'])
            if 'maintainability' in results:
                expected_results['maintainability_improvements'].append(results['maintainability'])

        # Calculate success probability from patterns
        if pattern_info:
            avg_success_rate = sum(p.get('success_rate', 0) for p in pattern_info) / len(pattern_info)
            expected_results['success_probability'] = round(avg_success_rate, 2)

            # Determine impact based on pattern complexity and success
            high_success_patterns = [p for p in pattern_info if p.get('success_rate', 0) > 0.8]
            if high_success_patterns:
                expected_results['estimated_impact'] = 'high'
            elif avg_success_rate > 0.6:
                expected_results['estimated_impact'] = 'medium'
            else:
                expected_results['estimated_impact'] = 'low'

        # Add default improvements
        if not expected_results['performance_improvements']:
            expected_results['performance_improvements'].append(
                "Faster data loading with dynamic database queries"
            )
        if not expected_results['reliability_improvements']:
            expected_results['reliability_improvements'].append(
                "Elimination of hardcoded fake data improves reliability"
            )
        if not expected_results['maintainability_improvements']:
            expected_results['maintainability_improvements'].append(
                "Easier maintenance with centralized data management"
            )

        return expected_results

    def _generate_debug_commands(self, structured_solution: Dict) -> List[Dict]:
        """Generate debug commands for troubleshooting"""

        debug_commands = [
            {
                'title': 'Verify API Response',
                'command': self.test_commands['general']['verify_response'].format(
                    url='http://localhost:3000/api/your-endpoint'
                ),
                'description': 'Check if API returns correct data'
            },
            {
                'title': 'Monitor Application Logs',
                'command': self.test_commands['general']['check_logs'].format(
                    log_file='logs/app.log'
                ),
                'description': 'Watch for errors or warnings'
            }
        ]

        # Add specific debug commands based on structured solution
        if structured_solution and 'debug_commands' in structured_solution:
            for cmd in structured_solution['debug_commands']:
                debug_commands.append({
                    'title': cmd.get('title', 'Debug Command'),
                    'command': cmd.get('command', ''),
                    'description': cmd.get('description', '')
                })

        return debug_commands

    def _detect_file_type(self, file_path: str) -> Optional[str]:
        """Detect file type from path"""
        if file_path.endswith('.js') or file_path.endswith('.jsx'):
            return 'javascript'
        elif file_path.endswith('.py'):
            return 'python'
        elif file_path.endswith('.java'):
            return 'java'
        elif file_path.endswith('.ts') or file_path.endswith('.tsx'):
            return 'typescript'
        return None

    def format_guide_as_text(self, guide: Dict) -> str:
        """Format the guide as a contextual optimization prompt with URL references"""

        analysis = guide['analysis']

        # Extract URL or context information if available
        url_info = ""
        if hasattr(self, '_current_url'):
            url_info = self._current_url

        # Extract file information for context
        files_info = ""
        if analysis['files_with_issues']:
            file_names = []
            for file_info in analysis['files_with_issues']:
                file_names.append(os.path.basename(file_info['path']))
            if file_names:
                files_info = f" (Files: {', '.join(file_names)})"

        # Extract specific issues
        issues_found = []
        if analysis['files_with_issues']:
            for file_info in analysis['files_with_issues']:
                file_name = os.path.basename(file_info['path'])
                for issue in file_info['issues'][:2]:  # Only first 2 issues
                    issues_found.append(f"{file_name}:{issue['line']} - {issue['description']}")

        # Extract implementation steps
        implementation_steps = []
        if guide['implementation_steps']:
            for i, step in enumerate(guide['implementation_steps'][:4], 1):  # Max 4 steps
                implementation_steps.append(f"{i}. {step['title']}")

        # Extract pattern/context information
        context_info = ""
        if analysis['pattern_references']:
            patterns = []
            for pattern in analysis['pattern_references'][:2]:  # Max 2 patterns
                if 'CustomerSuite' in str(pattern.get('id', '')) or 'customer' in str(pattern.get('id', '')).lower():
                    patterns.append("CustomerSuite")
                if 'translation' in str(pattern.get('id', '')).lower():
                    patterns.append("translation issues")

            if patterns:
                context_info = f"Context: {', '.join(patterns)}"

        # Build the structured optimization prompt
        prompt_parts = []

        if url_info:
            prompt_parts.append(f"Need to debug and optimize page: {url_info}")

        if issues_found:
            prompt_parts.append("Issues to fix:")
            for issue in issues_found:
                prompt_parts.append(f"  - {issue}")

        if implementation_steps:
            prompt_parts.append("Implementation steps:")
            prompt_parts.extend(implementation_steps)

        if context_info:
            prompt_parts.append(f"Additional context: {context_info}")

        if url_info:
            prompt_parts.append(f"Target URL: {url_info}")

        # Join with proper spacing
        if prompt_parts:
            return "\n".join(prompt_parts) + files_info
        else:
            # Default enhancement prompt when no specific issues found
            return f"Need to analyze and optimize this page for better performance and dynamic data{files_info}"