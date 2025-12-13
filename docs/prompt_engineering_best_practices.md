# Prompt Engineering Best Practices and Optimization Guide

## Table of Contents
1. [Structured Prompt Templates](#structured-prompt-templates)
2. [Zero-Shot, Few-Shot, and Chain-of-Thought Techniques](#zero-shot-few-shot-and-chain-of-thought-techniques)
3. [Reference-Based Optimization Strategies](#reference-based-optimization-strategies)
4. [Messy Input Handling and Cleaning](#messy-input-handling-and-cleaning)
5. [Prompt Refactoring and Optimization](#prompt-refactoring-and-optimization)
6. [Transformation Patterns](#transformation-patterns)
7. [Implementation Examples](#implementation-examples)

---

## Structured Prompt Templates

### 1. The TASK-COFT Framework

Based on analysis of your codebase and best practices, here's a structured template framework:

```python
TASK_TEMPLATE = """
You are a {role} with expertise in {domain}.

## TASK
{task_description}

## CONTEXT
{context_information}

## OBJECTIVES
{specific_objectives}

## CONSTRAINTS
{limitations_and_constraints}

## OUTPUT FORMAT
{desired_output_format}

## EXPECTED OUTCOME
{expected_result}
"""
```

### 2. Problem-Solution Template

```python
PROBLEM_SOLUTION_TEMPLATE = """
## PROBLEM ANALYSIS
**Issue**: {problem_description}
**Impact**: {problem_impact}
**Context**: {problem_context}

## SOLUTION REQUIREMENTS
1. **Immediate Action**: {quick_fix_requirement}
2. **Implementation Plan**: {detailed_solution_requirement}
3. **Key Components**: {component_requirements}
4. **Verification**: {testing_requirements}

## EXPECTED DELIVERABLES
{deliverable_specification}
"""
```

### 3. Code Enhancement Template

```python
CODE_ENHANCEMENT_TEMPLATE = """
## CURRENT SITUATION
**Code/Feature**: {current_implementation}
**Issue**: {identified_problem}
**Goal**: {improvement_objective}

## ENHANCEMENT REQUIREMENTS
1. **Performance**: {performance_requirements}
2. **Security**: {security_requirements}
3. **Maintainability**: {maintainability_requirements}
4. **Scalability**: {scalability_requirements}

## IMPLEMENTATION GUIDELINES
{specific_guidelines}

## SUCCESS CRITERIA
{measurable_outcomes}
"""
```

---

## Zero-Shot, Few-Shot, and Chain-of-Thought Techniques

### 1. Zero-Shot Prompting

**When to use**: Simple tasks with clear instructions

**Template**:
```python
ZERO_SHOT_TEMPLATE = """
Task: {clear_task_description}
Instructions: {step_by_step_instructions}
Input: {user_input}

Output:"""
```

**Example**:
```python
# Input: "i have issue in my api and it give me missing authentication token"
# Zero-shot prompt:
"""
Task: Convert user speech into a structured technical problem statement
Instructions:
1. Identify the main technical issue
2. Extract any error messages
3. Determine the affected system/component
4. Formulate as a clear problem statement

Input: "i have issue in my api and it give me missing authentication token"

Output: API authentication error - missing authentication token preventing API access"""
```

### 2. Few-Shot Prompting

**When to use**: Complex tasks requiring examples

**Template**:
```python
FEW_SHOT_TEMPLATE = """
Task: {task_description}

Examples:
Example 1:
Input: {example_input_1}
Output: {example_output_1}

Example 2:
Input: {example_input_2}
Output: {example_output_2}

Example 3:
Input: {example_input_3}
Output: {example_output_3}

Now process:
Input: {user_input}
Output:"""
```

**Example from your codebase**:
```python
# Transforming messy technical requests
examples = [
    ("my database slow optimize fast", "Database performance optimization needed"),
    ("login not working fix bug", "Authentication system bug fix required"),
    ("api gateway error missing token", "API Gateway authentication token issue")
]
```

### 3. Chain-of-Thought (CoT) Prompting

**When to use**: Multi-step reasoning, problem-solving

**Template**:
```python
COT_TEMPLATE = """
Problem: {problem_description}

Let's think step by step:

Step 1: {analyze_the_problem}
Step 2: {identify_components}
Step 3: {determine_solution_approach}
Step 4: {create_action_plan}
Step 5: {define_verification_steps}

Final Solution:"""
```

**Example**:
```python
# From your problem_solver_processor.py
"""
Problem: User reports "login route not working" with API Gateway configuration issues

Let's think step by step:

Step 1: Identify the authentication flow components
Step 2: Check API Gateway routing configuration
Step 3: Verify token validation logic
Step 4: Test endpoint connectivity
Step 5: Implement fixes and validate

Final Solution: [Detailed implementation plan]"""
```

---

## Reference-Based Optimization Strategies

### 1. Context-Aware Enhancement

From your `prompt_optimizer.py`, here's the pattern:

```python
def optimize_with_reference(input_text, context_references):
    """
    Enhances prompts using reference materials and context
    """
    optimization_strategy = {
        'files_referenced': context_references.get('clipboard'),
        'domain_keywords': extract_domain_keywords(input_text),
        'intent_classification': classify_user_intent(input_text),
        'complexity_level': assess_task_complexity(input_text)
    }

    return build_enhanced_prompt(input_text, optimization_strategy)
```

### 2. Pattern-Based Optimization

Based on your `optimization_processor.py`:

```python
OPTIMIZATION_PATTERNS = {
    'performance': {
        'keywords': ['slow', 'optimize', 'performance', 'fast'],
        'template': PERFORMANCE_OPTIMIZATION_TEMPLATE,
        'actions': ['profile', 'identify_bottlenecks', 'implement_caching', 'optimize_queries']
    },
    'security': {
        'keywords': ['auth', 'token', 'security', 'vulnerable'],
        'template': SECURITY_ENHANCEMENT_TEMPLATE,
        'actions': ['audit', 'implement_auth', 'add_validation', 'secure_endpoints']
    },
    'deployment': {
        'keywords': ['deploy', 'production', 'server', 'hosting'],
        'template': DEPLOYMENT_TEMPLATE,
        'actions': ['environment_setup', 'ci_cd', 'monitoring', 'documentation']
    }
}
```

---

## Messy Input Handling and Cleaning

### 1. Common Messy Patterns (from your codebase)

```python
MESSY_INPUT_PATTERNS = {
    'grammar_issues': [
        r'i\s+have\s+issue\s+in\s+my\s+(\w+)',     # "i have issue in my api"
        r'it\s+give\s+me\s+(\w+\s+\w+)',           # "it give me missing authentication"
        r'(\w+)\s+not\s+working',                  # "api not working"
    ],
    'punctuation_issues': [
        r'\s+',                                     # Multiple spaces
        r'^i\s+',                                  # Lowercase 'i' at start
        r'\w+\s*\.',                               # Bad punctuation spacing
    ],
    'sentence_fragments': [
        # Missing sentence endings
        # Incomplete thoughts
        # Run-on sentences
    ]
}
```

### 2. Cleaning Pipeline

```python
def clean_messy_input(raw_input):
    """
    Multi-stage cleaning process for messy user input
    """
    # Stage 1: Basic normalization
    cleaned = normalize_whitespace(raw_input)
    cleaned = fix_capitalization(cleaned)
    cleaned = fix_punctuation(cleaned)

    # Stage 2: Grammar correction
    cleaned = apply_grammar_rules(cleaned)

    # Stage 3: Structure enhancement
    cleaned = add_missing_context(cleaned)
    cleaned = clarify_ambiguity(cleaned)

    return cleaned
```

### 3. Context Extraction

```python
def extract_technical_context(messy_input):
    """
    Extracts technical context from messy input
    """
    context_indicators = {
        'error_messages': r'["\']([^"\']+)["\']',
        'component_names': r'(api|gateway|database|auth|login)',
        'action_verbs': r'(fix|optimize|debug|deploy|create)',
        'platform_terms': r'(aws|lambda|docker|kubernetes)'
    }

    extracted_context = {}
    for key, pattern in context_indicators.items():
        matches = re.findall(pattern, messy_input, re.IGNORECASE)
        if matches:
            extracted_context[key] = matches

    return extracted_context
```

---

## Prompt Refactoring and Optimization

### 1. Optimization Pipeline

From your `prompt_optimizer.py`, here's the three-step optimization:

```python
class PromptOptimizer:
    def optimize_prompt(self, raw_input, context=None):
        # Step 1: Basic Improvement
        step1 = self._apply_basic_improvement(raw_input)

        # Step 2: Context Enrichment
        step2 = self._enrich_with_context(step1, context)

        # Step 3: Final Structured Prompt
        final = self._generate_final_prompt(step2, raw_input, context)

        return {
            'raw_input': raw_input,
            'step1_basic': step1,
            'step2_improved': step2,
            'final_optimized': final
        }
```

### 2. Quality Metrics

```python
def evaluate_prompt_quality(original, optimized):
    """
    Evaluates prompt improvement quality
    """
    metrics = {
        'clarity_score': measure_clarity(optimized),
        'specificity_score': measure_specificity(optimized),
        'completeness_score': measure_completeness(optimized),
        'actionability_score': measure_actionability(optimized)
    }

    improvement = {
        'length_increase': len(optimized) - len(original),
        'structure_added': has_structure(optimized),
        'context_added': has_context(optimized)
    }

    return metrics, improvement
```

---

## Transformation Patterns

### 1. Performance Optimization Requests

**Messy Input**: "my database slow make app slow optimize fast"

**Transformation**:
```python
PERFORMANCE_OPTIMIZATION_PROMPT = """
## PERFORMANCE OPTIMIZATION REQUEST

**Problem**: Database performance degradation affecting application responsiveness

**Analysis Required**:
1. Identify slow queries and bottlenecks
2. Analyze database schema and indexing
3. Check connection pooling and caching strategies
4. Evaluate query optimization opportunities

**Optimization Plan**:
1. **Immediate Actions** (Quick wins):
   - Add missing indexes
   - Implement query result caching
   - Optimize N+1 query problems

2. **Medium-term Improvements**:
   - Database schema optimization
   - Connection pool configuration
   - Read replica implementation

3. **Long-term Strategy**:
   - Database sharding if needed
   - Advanced caching strategies
   - Performance monitoring setup

**Expected Outcome**:
- Query response time improvement of 60-80%
- Reduced database load
- Better user experience
"""
```

### 2. Security Improvements

**Messy Input**: "my login not secure need fix auth token"

**Transformation**:
```python
SECURITY_ENHANCEMENT_PROMPT = """
## SECURITY ENHANCEMENT REQUEST

**Current Issue**: Authentication system lacks proper security measures

**Security Assessment**:
1. **Authentication**:
   - Implement JWT with proper expiration
   - Add refresh token mechanism
   - Enable multi-factor authentication

2. **Authorization**:
   - Role-based access control (RBAC)
   - Principle of least privilege
   - API endpoint protection

3. **Data Protection**:
   - HTTPS enforcement
   - Input validation and sanitization
   - SQL injection prevention
   - XSS protection

4. **Session Management**:
   - Secure cookie configuration
   - Session timeout implementation
   - Logout functionality

**Implementation Priority**:
1. Critical: JWT authentication + HTTPS
2. High: Input validation + RBAC
3. Medium: MFA + session management
4. Low: Advanced monitoring

**Compliance**: Ensure GDPR/CCPA compliance where applicable
"""
```

### 3. Database Optimization

**Messy Input**: "database query slow need optimize fix performance"

**Transformation**:
```python
DATABASE_OPTIMIZATION_PROMPT = """
## DATABASE PERFORMANCE OPTIMIZATION

**Issue**: Database queries causing performance bottlenecks

**Optimization Areas**:

### 1. Query Analysis
- Identify slow queries using EXPLAIN ANALYZE
- Check for missing indexes
- Analyze query execution plans
- Review query patterns

### 2. Indexing Strategy
- Add composite indexes for common queries
- Implement partial indexes where appropriate
- Monitor index usage
- Remove unused indexes

### 3. Schema Optimization
- Normalize/denormalize based on access patterns
- Optimize data types
- Implement proper foreign keys
- Consider partitioning for large tables

### 4. Connection Management
- Implement connection pooling
- Configure appropriate pool sizes
- Set connection timeouts
- Monitor connection usage

### 5. Caching Layer
- Redis/Memcached for frequent queries
- Application-level caching
- Query result caching
- Cache invalidation strategy

**Performance Targets**:
- Reduce average query time by 70%
- Improve concurrent user handling
- Lower database CPU usage
- Achieve sub-100ms response for common queries
"""
```

### 4. Deployment Tasks

**Messy Input**: "need deploy my app to production server setup"

**Transformation**:
```python
DEPLOYMENT_SETUP_PROMPT = """
## PRODUCTION DEPLOYMENT SETUP

**Requirement**: Deploy application to production environment

### Infrastructure Setup
1. **Server Configuration**:
   - Choose cloud provider (AWS/GCP/Azure)
   - Configure instance types and scaling
   - Set up load balancers
   - Configure CDN

2. **Environment Preparation**:
   - Production environment variables
   - Database setup and migration
   - SSL certificate installation
   - Domain and DNS configuration

3. **CI/CD Pipeline**:
   - GitHub Actions/GitLab CI setup
   - Automated testing integration
   - Deployment stages (dev/staging/prod)
   - Rollback procedures

4. **Monitoring and Logging**:
   - Application monitoring (Prometheus/Grafana)
   - Log aggregation (ELK stack)
   - Error tracking (Sentry)
   - Performance monitoring

5. **Security Hardening**:
   - Firewall configuration
   - Security headers (HSTS, CSP)
   - Regular security updates
   - Backup and disaster recovery

### Deployment Checklist
- [ ] Environment variables configured
- [ ] Database migrations tested
- [ ] SSL certificates installed
- [ ] Monitoring tools active
- [ ] Backup strategy implemented
- [ ] Rollback plan documented
- [ ] Performance tests passed
- [ ] Security audit completed

**Go-Live Criteria**:
- All tests passing
- Performance benchmarks met
- Security scans clear
- Monitoring alerts configured
- Team training completed
"""
```

### 5. Code Debugging

**Messy Input**: "my code not working bug error fix please help"

**Transformation**:
```python
DEBUGGING_PROMPT = """
## CODE DEBUGGING REQUEST

**Issue**: Code malfunction requiring systematic debugging

### Debugging Process

#### 1. Problem Isolation
- **Symptom Description**: {specific_error_or_issue}
- **Affected Components**: {components_not_working}
- **Recent Changes**: {last_modifications}
- **Error Logs**: {error_messages}

#### 2. Systematic Diagnosis
1. **Reproduce the Issue**:
   - Document exact steps to reproduce
   - Identify trigger conditions
   - Note frequency and consistency

2. **Analyze Error Patterns**:
   - Review error messages and stack traces
   - Check browser console errors
   - Examine server logs
   - Monitor network requests

3. **Code Review**:
   - Recent changes analysis
   - Logic flow verification
   - Edge case consideration
   - Dependency updates check

#### 3. Debugging Tools and Techniques
- **Debugging Tools**: {browser_dev_tools, ide_debugger, logging}
- **Testing Methods**: {unit_tests, integration_tests, manual_testing}
- **Monitoring**: {real_time_logs, performance_profiling}

#### 4. Solution Implementation
1. **Hypothesis Formation**: Based on evidence gathered
2. **Minimal Reproduction**: Create isolated test case
3. **Fix Implementation**: Apply targeted solution
4. **Verification**: Test thoroughly including edge cases
5. **Documentation**: Record solution for future reference

### Expected Deliverables
- Root cause analysis report
- Step-by-step solution documentation
- Code changes with comments
- Test cases to prevent regression
- Monitoring setup for early detection
"""
```

---

## Implementation Examples

### 1. Complete Optimization Pipeline

```python
class PromptEngineeringPipeline:
    def __init__(self):
        self.optimizer = PromptOptimizer()
        self.patterns = self._load_patterns()
        self.templates = self._load_templates()

    def transform_messy_input(self, raw_input, context=None):
        """
        Complete transformation from messy input to optimized prompt
        """
        # Step 1: Initial cleaning
        cleaned = self._clean_input(raw_input)

        # Step 2: Intent classification
        intent = self._classify_intent(cleaned)

        # Step 3: Template selection
        template = self._select_template(intent, context)

        # Step 4: Context enrichment
        enriched = self._enrich_with_context(cleaned, context, intent)

        # Step 5: Final optimization
        final_prompt = self._apply_template(template, enriched, context)

        return {
            'original': raw_input,
            'cleaned': cleaned,
            'intent': intent,
            'template': template,
            'final_prompt': final_prompt,
            'metadata': self._generate_metadata(raw_input, final_prompt)
        }

    def _classify_intent(self, text):
        """
        Classify user intent based on keywords and patterns
        """
        intents = {
            'debug': ['fix', 'bug', 'error', 'not working', 'broken'],
            'optimize': ['slow', 'optimize', 'performance', 'improve'],
            'create': ['create', 'make', 'build', 'implement'],
            'deploy': ['deploy', 'production', 'server', 'hosting'],
            'security': ['secure', 'auth', 'token', 'vulnerability']
        }

        text_lower = text.lower()
        scores = {}

        for intent, keywords in intents.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[intent] = score

        return max(scores, key=scores.get) if any(scores.values()) else 'general'
```

### 2. Quality Assurance

```python
def validate_prompt_quality(prompt):
    """
    Validates and scores prompt quality
    """
    quality_checks = {
        'has_clear_structure': bool(re.search(r'##\s+\w+', prompt)),
        'has_specific_requirements': 'REQUIREMENTS' in prompt,
        'has_expected_outcome': 'EXPECTED' in prompt or 'OUTCOME' in prompt,
        'has_actionable_steps': bool(re.search(r'\d+\.\s+\w+', prompt)),
        'has_context': 'CONTEXT' in prompt or 'BACKGROUND' in prompt,
        'appropriate_length': 200 <= len(prompt) <= 2000,
        'no_ambiguity': not any(word in prompt.lower()
                              for word in ['maybe', 'perhaps', 'probably'])
    }

    score = sum(quality_checks.values()) / len(quality_checks) * 100

    return {
        'score': score,
        'checks': quality_checks,
        'recommendations': generate_improvements(quality_checks)
    }
```

---

## Key Takeaways

1. **Structure is Critical**: Always use structured templates with clear sections
2. **Context Matters**: Leverage file context, user history, and domain knowledge
3. **Iterative Improvement**: Use multi-step optimization processes
4. **Pattern Recognition**: Identify and standardize common transformation patterns
5. **Quality Metrics**: Measure and validate prompt effectiveness
6. **Automation Potential**: Most transformations can be automated with the right patterns

This guide provides a comprehensive foundation for implementing effective prompt engineering and optimization in your multi-dictate system. The patterns and templates can be directly applied to transform messy speech input into clear, actionable prompts.