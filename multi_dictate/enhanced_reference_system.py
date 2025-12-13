#!/usr/bin/env python3
"""
Enhanced Reference System with Page-Specific Examples and Directory Integration
Provides comprehensive reference library for different scenarios including plumbing, engineering, and complex deployments
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class EnhancedReferenceSystem:
    """
    Enhanced reference system that provides:
    - Page-specific optimization templates
    - Directory-based example integration
    - Complex deployment scenarios
    - Domain-specific reference libraries (plumbing, engineering, etc.)
    """

    def __init__(self, reference_dir: str = None):
        """Initialize the enhanced reference system."""
        self.reference_dir = reference_dir or os.path.join(os.path.dirname(__file__), '..', 'references')
        self.ensure_reference_directory()
        self.page_templates = self._load_page_templates()
        self.domain_references = self._load_domain_references()
        self.complex_scenarios = self._load_complex_scenarios()
        self.directory_examples = self._load_directory_examples()

    def ensure_reference_directory(self):
        """Ensure reference directory structure exists."""
        directories = [
            'pages',
            'domains',
            'scenarios',
            'examples',
            'deployments'
        ]

        for dir_name in directories:
            dir_path = os.path.join(self.reference_dir, dir_name)
            os.makedirs(dir_path, exist_ok=True)

        # Create default reference files if they don't exist
        self._create_default_references()

    def _create_default_references(self):
        """Create default reference files with comprehensive examples."""

        # Page-specific templates
        page_templates = {
            "dashboard": {
                "url_patterns": ["/dashboard", "/analytics", "/reports"],
                "common_issues": ["slow loading", "data visualization", "real-time updates"],
                "optimization_focus": ["data caching", "lazy loading", "chart optimization"],
                "reference_example": """
Task: Optimize dashboard page performance and user experience

Context:
- Current page: /dashboard with analytics widgets
- Performance issues: Slow initial load (>3s), laggy interactions
- User complaints: Dashboard takes too long to load on mobile

Technical Analysis:
- Multiple API calls for widgets loading sequentially
- Large datasets being processed client-side
- No caching strategy implemented
- Heavy JavaScript bundle size

Optimization Strategy:
1. Implement widget-level lazy loading
2. Add Redis caching for frequently accessed data
3. Use Web Workers for data processing
4. Implement incremental loading for large datasets
5. Optimize bundle size with code splitting

Implementation Steps:
1. Dashboard Audit (2 hours)
   - Measure current performance metrics
   - Identify bottlenecks using Chrome DevTools
   - Map user interaction patterns

2. Caching Implementation (4 hours)
   - Set up Redis for API response caching
   - Implement client-side caching strategies
   - Add cache invalidation logic

3. Lazy Loading (3 hours)
   - Implement intersection observer for widgets
   - Add loading states and skeletons
   - Optimize initial critical rendering path

4. Performance Monitoring (1 hour)
   - Add performance metrics tracking
   - Set up alerts for performance degradation

Expected Outcome:
- Initial load time: 3s → 1.2s (60% improvement)
- Interaction responsiveness: 500ms → 100ms
- Mobile performance score: 45 → 85

Testing Strategy:
- Lighthouse performance testing
- Real user monitoring (RUM)
- Load testing with simulated concurrent users"""
            },

            "api": {
                "url_patterns": ["/api/", "/graphql", "/rest"],
                "common_issues": ["slow responses", "authentication", "rate limiting"],
                "optimization_focus": ["query optimization", "caching", "async processing"],
                "reference_example": """
Task: Optimize API performance and implement scaling strategy

Context:
- REST API experiencing slow response times (>2s average)
- Database queries identified as primary bottleneck
- Growing traffic causing performance degradation

Technical Analysis:
- N+1 query problems in several endpoints
- No query result caching
- Synchronous processing for long-running operations
- Missing database indexes

Optimization Plan:
1. Database Query Optimization
2. API Response Caching
3. Asynchronous Processing
4. Load Balancing Setup

Implementation:
Phase 1: Database Optimization (8 hours)
- Add composite indexes for frequent query patterns
- Implement query result pagination
- Fix N+1 query issues with eager loading
- Set up connection pooling

Phase 2: Caching Layer (6 hours)
- Redis implementation for frequently accessed data
- HTTP caching headers for static responses
- Database query result caching
- Cache invalidation strategy

Phase 3: Async Processing (4 hours)
- Background job processing for long operations
- WebSocket updates for real-time features
- Queue management with Redis/RabbitMQ

Expected Results:
- API response time: 2s → 200ms (90% improvement)
- Database load: 80% → 30% CPU usage
- Concurrent user support: 100 → 1000+ users"""
            },

            "user_profile": {
                "url_patterns": ["/profile", "/settings", "/account"],
                "common_issues": ["data loading", "permissions", "security"],
                "optimization_focus": ["data privacy", "efficient loading", "security"],
                "reference_example": """
Task: Enhance user profile page security and performance

Context:
- User profile page loading slowly with large datasets
- Security concerns with data exposure
- Poor mobile experience with profile management

Security Enhancement:
1. Implement proper data access controls
2. Add data encryption for sensitive information
3. Implement audit logging for profile changes
4. Add two-factor authentication options

Performance Optimization:
1. Lazy load non-critical profile sections
2. Implement client-side caching for profile data
3. Optimize image upload and processing
4. Add progressive loading for profile history

Implementation Strategy:
Week 1: Security Audit and Fixes
Week 2: Performance Optimization
Week 3: Testing and Deployment
Week 4: Monitoring and Refinement"""
            }
        }

        # Domain-specific references
        domain_references = {
            "plumbing": {
                "keywords": ["pipes", "water", "drainage", "plumbing", "leak", "fixtures"],
                "scenarios": [
                    {
                        "title": "Residential Plumbing System Design",
                        "description": "Complete plumbing system optimization for residential properties",
                        "steps": [
                            "Water pressure analysis and optimization",
                            "Pipe sizing calculations for optimal flow",
                            "Drainage system design and venting requirements",
                            "Fixture placement and water supply routing",
                            "Hot water system optimization with recirculation",
                            "Leak detection and prevention systems",
                            "Water conservation measures implementation"
                        ],
                        "tools": ["Hydraulic calculation software", "Building code requirements", "Material selection guides"],
                        "references": ["International Plumbing Code", "Local building regulations", "Best practice guidelines"]
                    },
                    {
                        "title": "Commercial Plumbing Retrofit",
                        "description": "Upgrading existing commercial plumbing systems",
                        "steps": [
                            "Current system audit and deficiency identification",
                            "Water efficiency assessment and upgrade planning",
                            "Pipe material evaluation and replacement strategy",
                            "Fixture upgrade to water-efficient models",
                            "Backflow prevention system installation",
                            "Grease trap and drainage optimization",
                            "Maintenance schedule optimization"
                        ]
                    }
                ]
            },

            "engineering": {
                "keywords": ["structural", "mechanical", "electrical", "civil", "industrial"],
                "scenarios": [
                    {
                        "title": "Industrial Automation System Implementation",
                        "description": "Complete automation system for manufacturing facility",
                        "steps": [
                            "Current process analysis and automation opportunities",
                            "PLC system design and programming",
                            "Sensor and actuator network implementation",
                            "HMI/SCADA system integration",
                            "Safety system design and implementation",
                            "Data collection and analytics setup",
                            "Maintenance protocol development",
                            "Operator training program"
                        ],
                        "technical_specifications": {
                            "control_system": "PLC-based with redundant controllers",
                            "communication": "Industrial Ethernet with OPC-UA protocol",
                            "safety": "SIL 2 rated safety systems",
                            "monitoring": "Real-time performance dashboards"
                        }
                    },
                    {
                        "title": "Structural Retrofit for Seismic Compliance",
                        "description": "Building structural reinforcement for earthquake resistance",
                        "steps": [
                            "Structural analysis and vulnerability assessment",
                            "Seismic retrofit strategy development",
                            "Foundation strengthening design",
                            "Shear wall and bracing system installation",
                            "Connection reinforcement implementation",
                            "Non-structural component securing",
                            "Post-retrofit verification testing"
                        ]
                    }
                ]
            },

            "medical": {
                "keywords": ["healthcare", "medical", "hospital", "clinic", "patient"],
                "scenarios": [
                    {
                        "title": "Hospital Information System Integration",
                        "description": "Comprehensive HIS integration for healthcare facility",
                        "steps": [
                            "Current system assessment and gap analysis",
                            "HIPAA compliance review and enhancement",
                            "Electronic Health Records (EHR) integration",
                            "Clinical decision support system implementation",
                            "Patient portal development and integration",
                            "Billing and insurance system integration",
                            "Pharmacy management system connection",
                            "Laboratory information system integration",
                            "Telemedicine platform integration",
                            "Staff training and change management"
                        ],
                        "compliance": ["HIPAA", "HITECH", "FDA regulations", "State medical privacy laws"],
                        "security_measures": [
                            "End-to-end encryption",
                            "Access control and authentication",
                            "Audit logging and monitoring",
                            "Data backup and disaster recovery",
                            "Business associate agreements"
                        ]
                    }
                ]
            }
        }

        # Complex deployment scenarios
        complex_scenarios = {
            "microservices_migration": {
                "title": "Monolith to Microservices Migration",
                "description": "Complete migration strategy from monolithic to microservices architecture",
                "complexity": "high",
                "duration": "3-6 months",
                "phases": [
                    {
                        "phase": "Assessment and Planning",
                        "duration": "4 weeks",
                        "deliverables": [
                            "Current architecture analysis",
                            "Service boundary identification",
                            "Migration strategy document",
                            "Technology stack selection",
                            "Risk assessment and mitigation plan"
                        ]
                    },
                    {
                        "phase": "Infrastructure Setup",
                        "duration": "3 weeks",
                        "deliverables": [
                            "Container orchestration setup (Kubernetes)",
                            "Service mesh implementation",
                            "CI/CD pipeline configuration",
                            "Monitoring and logging infrastructure",
                            "Security and networking configuration"
                        ]
                    },
                    {
                        "phase": "Incremental Migration",
                        "duration": "8-16 weeks",
                        "deliverables": [
                            "Database decomposition",
                            "Service extraction and implementation",
                            "API gateway configuration",
                            "Service discovery setup",
                            "Gradual traffic shifting"
                        ]
                    }
                ],
                "success_metrics": [
                    "Service deployment frequency: Daily",
                    "Lead time for changes: <1 hour",
                    "Service availability: 99.9%",
                    "Rollback time: <5 minutes",
                    "Cross-team dependency reduction: 70%"
                ]
            },

            "multi_region_disaster_recovery": {
                "title": "Multi-Region Disaster Recovery Implementation",
                "description": "Complete disaster recovery setup across multiple geographic regions",
                "complexity": "very_high",
                "duration": "2-4 months",
                "components": [
                    {
                        "component": "Data Replication",
                        "implementation": "Multi-master database replication with conflict resolution",
                        "rpo": "<1 minute",
                        "rto": "<15 minutes"
                    },
                    {
                        "component": "Application Synchronization",
                        "implementation": "Active-active application deployment with global load balancing",
                        "failover_time": "<30 seconds"
                    },
                    {
                        "component": "Network Infrastructure",
                        "implementation": "SD-WAN with intelligent routing and failover",
                        "bandwidth_utilization": "Optimized with compression"
                    }
                ],
                "testing_scenarios": [
                    "Complete region outage simulation",
                    "Network partition testing",
                    "Partial service degradation",
                    "Graceful degradation under load",
                    "Automated failover verification"
                ]
            }
        }

        # Save default references
        self._save_reference_file('pages/page_templates.json', page_templates)
        self._save_reference_file('domains/domain_references.json', domain_references)
        self._save_reference_file('scenarios/complex_scenarios.json', complex_scenarios)

    def _save_reference_file(self, relative_path: str, data: Dict):
        """Save reference data to file."""
        file_path = os.path.join(self.reference_dir, relative_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Created reference file: {file_path}")

    def _load_page_templates(self) -> Dict:
        """Load page-specific optimization templates."""
        file_path = os.path.join(self.reference_dir, 'pages', 'page_templates.json')
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}

    def _load_domain_references(self) -> Dict:
        """Load domain-specific reference library."""
        file_path = os.path.join(self.reference_dir, 'domains', 'domain_references.json')
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}

    def _load_complex_scenarios(self) -> Dict:
        """Load complex deployment scenarios."""
        file_path = os.path.join(self.reference_dir, 'scenarios', 'complex_scenarios.json')
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}

    def _load_directory_examples(self) -> Dict:
        """Load examples from project directories."""
        examples = {}

        # Scan common project directories for examples
        scan_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..'),  # Project root
            '/tmp',  # Temp directory for testing
            os.path.expanduser('~/Documents')  # User documents
        ]

        for scan_path in scan_paths:
            if os.path.exists(scan_path):
                examples.update(self._scan_directory_for_examples(scan_path))

        return examples

    def _scan_directory_for_examples(self, directory: str) -> Dict:
        """Scan directory for example files and patterns."""
        examples = {}

        try:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories and common non-project directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git']]

                # Look for specific file types
                for file in files:
                    if file.endswith(('.js', '.py', '.java', '.md', '.txt', '.json')):
                        file_path = os.path.join(root, file)

                        # Extract relative path as key
                        rel_path = os.path.relpath(file_path, directory)

                        # Analyze file for relevant content
                        file_info = self._analyze_file_for_reference(file_path)
                        if file_info:
                            examples[rel_path] = file_info

        except PermissionError:
            logger.warning(f"Permission denied scanning directory: {directory}")
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")

        return examples

    def _analyze_file_for_reference(self, file_path: str) -> Optional[Dict]:
        """Analyze a file to extract reference information."""
        try:
            # Skip very large files
            if os.path.getsize(file_path) > 1024 * 1024:  # 1MB limit
                return None

            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()

            # Check for relevant patterns
            indicators = {
                'database': ['sql', 'database', 'query', 'connection'],
                'api': ['api', 'endpoint', 'rest', 'graphql'],
                'security': ['auth', 'security', 'encrypt', 'token'],
                'performance': ['optimize', 'performance', 'cache', 'async'],
                'deployment': ['deploy', 'production', 'docker', 'kubernetes']
            }

            detected_types = []
            for indicator_type, keywords in indicators.items():
                if any(keyword.lower() in content.lower() for keyword in keywords):
                    detected_types.append(indicator_type)

            if detected_types:
                return {
                    'path': file_path,
                    'type': detected_types,
                    'size': os.path.getsize(file_path),
                    'last_modified': os.path.getmtime(file_path),
                    'preview': content[:200] + "..." if len(content) > 200 else content
                }

        except Exception as e:
            logger.debug(f"Could not analyze file {file_path}: {e}")

        return None

    def get_page_reference(self, url: str) -> Optional[Dict]:
        """Get page-specific reference based on URL."""
        for page_name, template in self.page_templates.items():
            for pattern in template.get("url_patterns", []):
                if pattern in url.lower():
                    return {
                        'page_type': page_name,
                        'template': template,
                        'reference_example': template.get('reference_example', '')
                    }
        return None

    def get_domain_reference(self, text: str) -> Optional[Dict]:
        """Get domain-specific reference based on text content."""
        text_lower = text.lower()

        for domain, reference in self.domain_references.items():
            keywords = reference.get("keywords", [])
            if any(keyword in text_lower for keyword in keywords):
                return {
                    'domain': domain,
                    'scenarios': reference.get("scenarios", []),
                    'reference': reference
                }

        return None

    def get_complex_scenario(self, scenario_name: str) -> Optional[Dict]:
        """Get complex deployment scenario reference."""
        return self.complex_scenarios.get(scenario_name)

    def get_directory_reference(self, path: str) -> List[Dict]:
        """Get references from specific directory path."""
        references = []

        for rel_path, file_info in self.directory_examples.items():
            if path in rel_path or any(part in path for part in rel_path.split('/')):
                references.append(file_info)

        return references

    def enhance_prompt_with_references(self, prompt: str, url: str = None, context: Dict = None) -> str:
        """Enhance prompt with relevant references."""
        enhanced_parts = [prompt]

        # Add page-specific reference
        if url:
            page_ref = self.get_page_reference(url)
            if page_ref:
                enhanced_parts.append("\n--- PAGE-SPECIFIC REFERENCE ---")
                enhanced_parts.append(f"Page Type: {page_ref['page_type']}")
                if page_ref['reference_example']:
                    enhanced_parts.append(page_ref['reference_example'])

        # Add domain-specific reference
        if context and 'original_input' in context:
            domain_ref = self.get_domain_reference(context['original_input'])
            if domain_ref:
                enhanced_parts.append("\n--- DOMAIN-SPECIFIC REFERENCE ---")
                enhanced_parts.append(f"Domain: {domain_ref['domain']}")

                scenarios = domain_ref.get('scenarios', [])
                if scenarios:
                    enhanced_parts.append("Related Scenarios:")
                    for i, scenario in enumerate(scenarios[:2], 1):  # Top 2 scenarios
                        enhanced_parts.append(f"{i}. {scenario.get('title', '')}")
                        enhanced_parts.append(f"   {scenario.get('description', '')[:100]}...")

        # Add directory reference if provided
        if context and 'clipboard' in context:
            # Extract directory path from clipboard if it's a file path
            clipboard_content = str(context.get('clipboard', ''))
            if os.path.exists(clipboard_content) and os.path.isdir(clipboard_content):
                dir_refs = self.get_directory_reference(clipboard_content)
                if dir_refs:
                    enhanced_parts.append("\n--- DIRECTORY REFERENCES ---")
                    enhanced_parts.append(f"Found {len(dir_refs)} relevant files in directory:")
                    for ref in dir_refs[:5]:  # Top 5 files
                        rel_path = os.path.relpath(ref['path'], clipboard_content)
                        enhanced_parts.append(f"• {rel_path} ({', '.join(ref['type'])})")

        return "\n".join(enhanced_parts)