#!/usr/bin/env python3
"""
File Content Analyzer - Analyzes files for specific issues and problems
Actually reads and understands the content instead of giving generic advice
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class FileContentAnalyzer:
    """Analyzes file content to detect specific issues and problems"""

    def __init__(self):
        self.issue_patterns = {
            # Code issues
            'fake_data': [
                r'fake.*email', r'fake.*name', r'test.*user', r'dummy.*data',
                r'sample.*data', r'placeholder.*email', r'example\.com'
            ],
            'missing_required_fields': [
                r'required.*field.*missing', r'null.*email', r'empty.*field',
                r'missing.*validation', r'field.*cannot.*be.*null'
            ],
            'api_issues': [
                r'404.*not.*found', r'500.*error', r'api.*timeout',
                r'connection.*refused', r'invalid.*token', r'unauthorized'
            ],
            'security_issues': [
                r'password.*plain.*text', r'sql.*injection', r'csrf.*missing',
                r'xss.*vulnerable', r'hardcoded.*secret', r'sensitive.*data.*exposed'
            ],
            'data_issues': [
                r'duplicate.*entry', r'constraint.*violation', r'foreign.*key',
                r'data.*integrity', r'corrupted.*data', r'malformed.*json'
            ],
            'url_issues': [
                r'broken.*link', r'invalid.*url', r'missing.*endpoint',
                r'wrong.*route', r'404.*page', r'redirect.*loop'
            ],
            'testing_issues': [
                r'test.*failure', r'assertion.*error', r'timeout.*test',
                r'missing.*test', r'coverage.*low', r'test.*flaky'
            ],
            'performance_issues': [
                r'slow.*query', r'high.*memory', r'infinite.*loop',
                r'memory.*leak', r'n\+1.*query', r'blocking.*operation'
            ]
        }

    def analyze_file_content(self, file_path: str, content: str) -> Dict:
        """Analyze specific file content for issues"""
        issues_found = []
        file_type = self._detect_file_type(file_path, content)

        # Detect fake data
        fake_issues = self._detect_fake_data(content)
        if fake_issues:
            issues_found.extend(fake_issues)

        # Detect code issues based on file type
        if file_type in ['python', 'javascript', 'typescript', 'java', 'sql']:
            code_issues = self._detect_code_issues(content, file_type)
            issues_found.extend(code_issues)

        # Detect config/data issues
        if file_type in ['json', 'yaml', 'xml', 'config']:
            data_issues = self._detect_data_issues(content)
            issues_found.extend(data_issues)

        # Detect documentation issues
        if file_type in ['md', 'txt', 'doc']:
            doc_issues = self._detect_documentation_issues(content)
            issues_found.extend(doc_issues)

        # Detect web/URL issues
        url_issues = self._detect_url_issues(content)
        if url_issues:
            issues_found.extend(url_issues)

        return {
            'file_path': file_path,
            'file_type': file_type,
            'issues_found': issues_found,
            'total_issues': len(issues_found),
            'summary': self._generate_issue_summary(issues_found)
        }

    def _detect_file_type(self, file_path: str, content: str) -> str:
        """Detect file type from path and content"""
        path_lower = file_path.lower()

        # Check file extension
        if path_lower.endswith('.py'):
            return 'python'
        elif path_lower.endswith(('.js', '.jsx')):
            return 'javascript'
        elif path_lower.endswith('.ts'):
            return 'typescript'
        elif path_lower.endswith('.java'):
            return 'java'
        elif path_lower.endswith('.sql'):
            return 'sql'
        elif path_lower.endswith(('.json', '.jsonl')):
            return 'json'
        elif path_lower.endswith(('.yaml', '.yml')):
            return 'yaml'
        elif path_lower.endswith('.xml'):
            return 'xml'
        elif path_lower.endswith(('.md', '.markdown')):
            return 'md'
        elif path_lower.endswith(('.txt', '.log')):
            return 'txt'
        elif path_lower.endswith(('.env', '.config', '.conf')):
            return 'config'

        # Check content patterns
        if 'def ' in content and 'import ' in content:
            return 'python'
        elif 'function ' in content and ('var ' in content or 'let ' in content or 'const ' in content):
            return 'javascript'
        elif 'CREATE TABLE' in content or 'SELECT ' in content:
            return 'sql'
        elif '{' in content and '"' in content and ':' in content:
            return 'json'

        return 'unknown'

    def _detect_fake_data(self, content: str) -> List[Dict]:
        """Detect fake/placeholder data"""
        issues = []
        content_lower = content.lower()

        for pattern in self.issue_patterns['fake_data']:
            matches = list(re.finditer(pattern, content_lower, re.IGNORECASE))
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'type': 'fake_data',
                    'severity': 'medium',
                    'line': line_num,
                    'description': f"Fake/placeholder data detected: {match.group()}",
                    'match_text': match.group(),
                    'context': self._get_line_context(content, line_num)
                })

        return issues

    def _detect_code_issues(self, content: str, file_type: str) -> List[Dict]:
        """Detect code-specific issues"""
        issues = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Common code issues across languages
            if file_type == 'python':
                if 'print(' in line_stripped and 'debug' not in line_stripped:
                    issues.append({
                        'type': 'debug_code',
                        'severity': 'low',
                        'line': line_num,
                        'description': "Debug print statement found",
                        'match_text': line_stripped,
                        'context': self._get_line_context(content, line_num)
                    })

                if line_stripped.startswith('import *'):
                    issues.append({
                        'type': 'wildcard_import',
                        'severity': 'medium',
                        'line': line_num,
                        'description': "Wildcard import detected",
                        'match_text': line_stripped,
                        'context': self._get_line_context(content, line_num)
                    })

            elif file_type in ['javascript', 'typescript']:
                if 'console.log(' in line_stripped:
                    issues.append({
                        'type': 'console_log',
                        'severity': 'low',
                        'line': line_num,
                        'description': "Console.log statement found",
                        'match_text': line_stripped,
                        'context': self._get_line_context(content, line_num)
                    })

                if 'var ' in line_stripped and not ('var i' in line_stripped or 'var x' in line_stripped):
                    issues.append({
                        'type': 'var_declaration',
                        'severity': 'low',
                        'line': line_num,
                        'description': "var keyword found (prefer let/const)",
                        'match_text': line_stripped,
                        'context': self._get_line_context(content, line_num)
                    })

        return issues

    def _detect_data_issues(self, content: str) -> List[Dict]:
        """Detect data format issues"""
        issues = []

        try:
            # Try to parse JSON
            json.loads(content)
        except json.JSONDecodeError as e:
            issues.append({
                'type': 'json_syntax_error',
                'severity': 'high',
                'line': 1,
                'description': f"JSON syntax error: {str(e)}",
                'match_text': str(e),
                'context': content[:200]
            })

        return issues

    def _detect_documentation_issues(self, content: str) -> List[Dict]:
        """Detect documentation issues"""
        issues = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Check for TODO comments that should be addressed
            if re.search(r'todo|fixme|hack', line, re.IGNORECASE):
                issues.append({
                    'type': 'todo_comment',
                    'severity': 'medium',
                    'line': line_num,
                    'description': "TODO/FIXME comment found - should be addressed",
                    'match_text': line.strip(),
                    'context': self._get_line_context(content, line_num)
                })

        return issues

    def _detect_url_issues(self, content: str) -> List[Dict]:
        """Detect URL and endpoint issues"""
        issues = []

        # Find URLs in content
        url_pattern = r'https?://[^\s\)]+'
        urls = re.findall(url_pattern, content)

        for i, url in enumerate(urls):
            # Check for common URL issues
            if 'localhost' in url or '127.0.0.1' in url:
                issues.append({
                    'type': 'localhost_url',
                    'severity': 'medium',
                    'description': f"Localhost URL found: {url}",
                    'match_text': url,
                    'context': f"URL #{i+1} in content"
                })

            if any(dead_url in url for dead_url in ['example.com', 'test.com', 'fake.com']):
                issues.append({
                    'type': 'placeholder_url',
                    'severity': 'high',
                    'description': f"Placeholder/fake URL found: {url}",
                    'match_text': url,
                    'context': f"URL #{i+1} in content"
                })

        return issues

    def _get_line_context(self, content: str, line_num: int, context_lines: int = 2) -> str:
        """Get context around a specific line"""
        lines = content.split('\n')
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)

        context_lines_list = []
        for i in range(start, end):
            prefix = ">>> " if i == line_num - 1 else "    "
            context_lines_list.append(f"{prefix}{lines[i]}")

        return '\n'.join(context_lines_list)

    def _generate_issue_summary(self, issues: List[Dict]) -> str:
        """Generate a summary of found issues"""
        if not issues:
            return "No specific issues detected in the file."

        # Group issues by severity and type
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        type_counts = {}

        for issue in issues:
            severity = issue['severity']
            issue_type = issue['type']
            severity_counts[severity] += 1
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1

        # Create summary
        summary_parts = [f"Found {len(issues)} issues:"]

        # Add severity breakdown
        if severity_counts['high'] > 0:
            summary_parts.append(f"• {severity_counts['high']} high-priority")
        if severity_counts['medium'] > 0:
            summary_parts.append(f"• {severity_counts['medium']} medium-priority")
        if severity_counts['low'] > 0:
            summary_parts.append(f"• {severity_counts['low']} low-priority")

        # Add main issue types
        main_issues = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        if main_issues:
            summary_parts.append("Main issues:")
            for issue_type, count in main_issues:
                summary_parts.append(f"  • {issue_type}: {count} occurrences")

        return '\n'.join(summary_parts)

    def analyze_directory(self, directory_path: str) -> Dict:
        """Analyze all files in a directory"""
        path = Path(directory_path)
        if not path.exists():
            return {'success': False, 'error': f"Directory not found: {directory_path}"}

        all_issues = []
        files_analyzed = 0

        # Find relevant files to analyze
        file_patterns = [
            '*.py', '*.js', '*.ts', '*.java', '*.sql',
            '*.json', '*.yaml', '*.yml', '*.md',
            '*.txt', '*.log', '*.env', '*.config'
        ]

        for pattern in file_patterns:
            for file_path in path.glob(f"**/{pattern}"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    analysis = self.analyze_file_content(str(file_path), content)
                    if analysis['total_issues'] > 0:
                        all_issues.append(analysis)

                    files_analyzed += 1

                except Exception as e:
                    logger.warning(f"Could not analyze {file_path}: {e}")

        return {
            'success': True,
            'directory_path': directory_path,
            'files_analyzed': files_analyzed,
            'total_issues': len(all_issues),
            'issues_by_file': all_issues,
            'summary': self._generate_directory_summary(all_issues, files_analyzed)
        }

    def _generate_directory_summary(self, all_issues: List[Dict], files_analyzed: int) -> str:
        """Generate summary for directory analysis"""
        if not all_issues:
            return f"Analyzed {files_analyzed} files - no critical issues found."

        # Count issues by severity across all files
        total_severity = {'high': 0, 'medium': 0, 'low': 0}
        for file_analysis in all_issues:
            for issue in file_analysis['issues_found']:
                total_severity[issue['severity']] += 1

        summary = [f"Directory Analysis Results:"]
        summary.append(f"• {files_analyzed} files analyzed")
        summary.append(f"• {len(all_issues)} files with issues")

        if total_severity['high'] > 0:
            summary.append(f"• {total_severity['high']} high-priority issues need immediate attention")
        if total_severity['medium'] > 0:
            summary.append(f"• {total_severity['medium']} medium-priority issues")
        if total_severity['low'] > 0:
            summary.append(f"• {total_severity['low']} low-priority issues")

        return '\n'.join(summary)