"""
Dynamic Test Generation Service
Ensures unique test generation with varied scores and dynamic content
"""

import asyncio
import random
import uuid
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
import structlog

from .logging_service import ai_logging_service, LogLevel, AISystemType

logger = structlog.get_logger()


class TestComplexity(Enum):
    """Test complexity levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"
    LEGENDARY = "legendary"


class TestCategory(Enum):
    """Test categories"""
    KNOWLEDGE_VERIFICATION = "knowledge_verification"
    CODE_QUALITY = "code_quality"
    SECURITY_AWARENESS = "security_awareness"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    INNOVATION_CAPABILITY = "innovation_capability"
    SELF_IMPROVEMENT = "self_improvement"
    CROSS_AI_COLLABORATION = "cross_ai_collaboration"
    EXPERIMENTAL_VALIDATION = "experimental_validation"


class DynamicTestGenerator:
    """Dynamic test generator with unique content and varied scoring"""
    
    def __init__(self):
        self.test_history = {}
        self.question_templates = self._load_question_templates()
        self.scenario_templates = self._load_scenario_templates()
        self.difficulty_multipliers = {
            "basic": 1.0,
            "intermediate": 1.2,
            "advanced": 1.5,
            "expert": 2.0,
            "master": 2.5,
            "legendary": 3.0
        }
    
    def _load_question_templates(self) -> Dict[str, List[str]]:
        """Load question templates for different categories"""
        return {
            "knowledge_verification": [
                "Explain the concept of {topic} and provide a practical example.",
                "What are the key differences between {topic1} and {topic2}?",
                "How would you implement {concept} in a real-world scenario?",
                "Describe the best practices for {topic} and why they matter.",
                "What are the common pitfalls when working with {topic}?"
            ],
            "code_quality": [
                "Write a function that {requirement} with proper error handling and documentation.",
                "Refactor this code to improve {aspect}: {code_snippet}",
                "Create a class that implements {pattern} following SOLID principles.",
                "Optimize this algorithm for {performance_metric}: {algorithm}",
                "Write unit tests for this function: {function_code}"
            ],
            "security_awareness": [
                "Identify security vulnerabilities in this code: {code_snippet}",
                "How would you secure this API endpoint: {endpoint_description}",
                "Implement secure authentication for {system_type}",
                "What are the security implications of {practice}?",
                "Design a secure data storage solution for {data_type}"
            ],
            "performance_optimization": [
                "Optimize this database query: {query}",
                "Improve the performance of this function: {function_code}",
                "Design a caching strategy for {system_component}",
                "Analyze the time complexity of this algorithm: {algorithm}",
                "Implement load balancing for {service_type}"
            ],
            "innovation_capability": [
                "Design a novel solution for {problem}",
                "Create an innovative approach to {challenge}",
                "Propose a new algorithm for {task}",
                "Design a system that combines {technology1} and {technology2}",
                "Invent a new methodology for {process}"
            ],
            "self_improvement": [
                "How would you enhance this codebase: {codebase_description}",
                "Propose improvements for this architecture: {architecture}",
                "Design a learning system for {ai_type}",
                "Create a feedback mechanism for {system}",
                "Implement continuous improvement for {process}"
            ],
            "cross_ai_collaboration": [
                "Design a collaborative system between {ai1} and {ai2}",
                "Create a protocol for {ai1} and {ai2} to work together on {task}",
                "Design a communication system for multiple AIs: {ai_list}",
                "Create a shared knowledge base for {ai_types}",
                "Design a consensus mechanism for {ai_group}"
            ],
            "experimental_validation": [
                "Design an experiment to test {hypothesis}",
                "Create a validation framework for {system}",
                "Design A/B testing for {feature}",
                "Create metrics to measure {performance_aspect}",
                "Design a testing strategy for {new_technology}"
            ]
        }
    
    def _load_scenario_templates(self) -> Dict[str, List[str]]:
        """Load scenario templates for different categories"""
        return {
            "knowledge_verification": [
                "You are a {role} working on {project}. Your team needs to understand {topic}.",
                "As a {role}, you've been asked to explain {concept} to stakeholders.",
                "Your company is adopting {technology}. You need to train your team.",
                "You're consulting for a client who needs help with {domain}.",
                "You're writing documentation for a {system_type} system."
            ],
            "code_quality": [
                "You're a senior developer reviewing code for a {project_type} project.",
                "Your team is refactoring a legacy {system_type} system.",
                "You're implementing a new {feature} in an existing codebase.",
                "You're mentoring a junior developer on {best_practice}.",
                "You're designing the architecture for a new {application_type}."
            ],
            "security_awareness": [
                "You're a security consultant auditing a {system_type} system.",
                "Your company has been asked to implement {security_requirement}.",
                "You're investigating a potential security breach in {system}.",
                "You're designing security protocols for {sensitive_data}.",
                "You're implementing authentication for a {user_type} system."
            ],
            "performance_optimization": [
                "Your {application_type} is experiencing performance issues.",
                "You're optimizing a {system_type} for high traffic.",
                "You're designing a scalable architecture for {service}.",
                "You're improving the performance of {algorithm_type}.",
                "You're implementing caching for a {data_type} system."
            ],
            "innovation_capability": [
                "You're a research scientist exploring {emerging_technology}.",
                "Your startup is developing a novel {product_type}.",
                "You're designing a breakthrough solution for {industry_problem}.",
                "You're creating a new methodology for {process}.",
                "You're inventing a new approach to {challenge}."
            ],
            "self_improvement": [
                "You're an AI system looking to enhance your {capability}.",
                "Your team wants to improve the {aspect} of your system.",
                "You're implementing continuous learning for {ai_type}.",
                "You're designing a feedback loop for {system}.",
                "You're creating a self-improvement mechanism for {process}."
            ],
            "cross_ai_collaboration": [
                "You're coordinating multiple AI systems for {complex_task}.",
                "Your team of AIs needs to collaborate on {project}.",
                "You're designing a communication protocol for {ai_group}.",
                "You're creating a shared workspace for {ai_types}.",
                "You're implementing consensus mechanisms for {ai_team}."
            ],
            "experimental_validation": [
                "You're a research team testing {hypothesis}.",
                "You're validating a new {technology} in production.",
                "You're conducting A/B tests for {feature}.",
                "You're measuring the effectiveness of {intervention}.",
                "You're designing experiments for {research_area}."
            ]
        }
    
    async def generate_dynamic_test(self, ai_type: str, category: TestCategory, 
                                  complexity: TestComplexity) -> Dict[str, Any]:
        """Generate a dynamic test with unique content"""
        try:
            # Generate unique test ID
            test_id = str(uuid.uuid4())
            
            # Get current timestamp for uniqueness
            timestamp = datetime.utcnow().isoformat()
            
            # Select random template
            templates = self.question_templates.get(category.value, [])
            scenarios = self.scenario_templates.get(category.value, [])
            
            if not templates or not scenarios:
                raise ValueError(f"No templates found for category: {category.value}")
            
            # Generate unique content
            question_template = random.choice(templates)
            scenario_template = random.choice(scenarios)
            
            # Fill templates with dynamic content
            question = await self._fill_template(question_template, category.value, complexity.value)
            scenario = await self._fill_scenario_template(scenario_template, category.value, complexity.value)
            
            # Generate unique scoring criteria
            scoring_criteria = await self._generate_scoring_criteria(category.value, complexity.value)
            
            # Create test content
            test_content = {
                "test_id": test_id,
                "ai_type": ai_type,
                "category": category.value,
                "complexity": complexity.value,
                "timestamp": timestamp,
                "scenario": scenario,
                "questions": [question],
                "scoring_criteria": scoring_criteria,
                "time_limit": self._get_time_limit(complexity.value),
                "unique_identifier": f"{ai_type}_{category.value}_{complexity.value}_{timestamp}"
            }
            
            # Log test generation
            ai_logging_service.log_test_execution(
                ai_type=ai_type,
                test_type="dynamic_generation",
                score=0.0,
                passed=False,
                duration=0.0,
                context={
                    "test_id": test_id,
                    "category": category.value,
                    "complexity": complexity.value,
                    "scenario_length": len(scenario),
                    "question_count": len(test_content["questions"])
                }
            )
            
            return test_content
            
        except Exception as e:
            logger.error(f"Error generating dynamic test: {str(e)}")
            raise
    
    async def _fill_template(self, template: str, category: str, complexity: str) -> str:
        """Fill template with dynamic content"""
        # Define dynamic content based on category and complexity
        content_map = {
            "knowledge_verification": {
                "topic": ["machine learning", "distributed systems", "microservices", "cloud computing", "data science"],
                "topic1": ["synchronous", "asynchronous", "monolithic", "microservices", "serverless"],
                "topic2": ["asynchronous", "synchronous", "microservices", "monolithic", "serverless"],
                "concept": ["load balancing", "caching", "authentication", "authorization", "monitoring"]
            },
            "code_quality": {
                "requirement": ["validates user input", "handles database connections", "implements caching", "processes API responses"],
                "aspect": ["readability", "maintainability", "performance", "security", "testability"],
                "pattern": ["Observer", "Factory", "Singleton", "Strategy", "Command"],
                "performance_metric": ["time complexity", "memory usage", "throughput", "latency"],
                "function_code": ["def process_data(data): return data", "def calculate_sum(nums): return sum(nums)"]
            },
            "security_awareness": {
                "code_snippet": ["user_input = request.form['data']", "query = f'SELECT * FROM users WHERE id = {user_id}'"],
                "endpoint_description": ["user authentication", "data retrieval", "file upload", "payment processing"],
                "system_type": ["web application", "mobile app", "API service", "database"],
                "practice": ["storing passwords in plain text", "using GET for sensitive data", "not validating input"],
                "data_type": ["user credentials", "financial information", "personal data", "health records"]
            },
            "performance_optimization": {
                "query": ["SELECT * FROM users WHERE name LIKE '%john%'", "SELECT * FROM orders WHERE date > '2023-01-01'"],
                "function_code": ["def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"],
                "system_component": ["database queries", "API responses", "file operations", "memory usage"],
                "algorithm": ["bubble sort", "linear search", "recursive factorial", "naive string matching"],
                "service_type": ["web server", "database", "cache", "message queue"]
            },
            "innovation_capability": {
                "problem": ["real-time language translation", "autonomous vehicle navigation", "predictive maintenance"],
                "challenge": ["scaling AI systems", "reducing energy consumption", "improving user experience"],
                "task": ["image recognition", "natural language processing", "recommendation systems"],
                "technology1": ["blockchain", "IoT", "AI", "edge computing"],
                "technology2": ["AI", "blockchain", "IoT", "edge computing"]
            },
            "self_improvement": {
                "codebase_description": ["legacy system with technical debt", "monolithic application", "distributed system"],
                "architecture": ["three-tier", "microservices", "event-driven", "serverless"],
                "ai_type": ["imperium", "guardian", "sandbox", "conquest"],
                "system": ["recommendation engine", "authentication service", "data processing pipeline"],
                "process": ["code review", "testing", "deployment", "monitoring"]
            },
            "cross_ai_collaboration": {
                "ai1": ["imperium", "guardian", "sandbox", "conquest"],
                "ai2": ["guardian", "sandbox", "conquest", "imperium"],
                "task": ["code review", "system design", "problem solving", "optimization"],
                "ai_list": ["imperium, guardian, sandbox", "guardian, conquest", "all AI types"],
                "ai_types": ["imperium and guardian", "sandbox and conquest", "all AI systems"],
                "ai_group": ["development team", "security team", "optimization team"]
            },
            "experimental_validation": {
                "hypothesis": ["new algorithm improves performance", "caching reduces latency", "new UI improves UX"],
                "system": ["recommendation engine", "authentication service", "data pipeline"],
                "feature": ["new search algorithm", "improved UI", "enhanced security"],
                "performance_aspect": ["response time", "accuracy", "user satisfaction"],
                "new_technology": ["graph database", "stream processing", "edge computing"]
            }
        }
        
        # Get content for this category
        category_content = content_map.get(category, {})
        
        # Fill template with random content
        filled_template = template
        for key, values in category_content.items():
            if f"{{{key}}}" in filled_template:
                filled_template = filled_template.replace(f"{{{key}}}", random.choice(values))
        
        return filled_template
    
    async def _fill_scenario_template(self, template: str, category: str, complexity: str) -> str:
        """Fill scenario template with dynamic content"""
        # Define role and project mappings
        role_map = {
            "knowledge_verification": ["senior developer", "tech lead", "architect", "consultant", "trainer"],
            "code_quality": ["code reviewer", "senior developer", "tech lead", "mentor", "architect"],
            "security_awareness": ["security consultant", "penetration tester", "security engineer", "auditor"],
            "performance_optimization": ["performance engineer", "senior developer", "architect", "devops engineer"],
            "innovation_capability": ["research scientist", "innovator", "startup founder", "inventor"],
            "self_improvement": ["AI system", "learning algorithm", "adaptive system", "self-improving AI"],
            "cross_ai_collaboration": ["AI coordinator", "system architect", "team lead", "collaboration designer"],
            "experimental_validation": ["research team", "data scientist", "experiment designer", "validation engineer"]
        }
        
        project_map = {
            "knowledge_verification": ["e-commerce platform", "mobile app", "API service", "data pipeline"],
            "code_quality": ["legacy system", "microservices", "monolithic app", "distributed system"],
            "security_awareness": ["banking system", "healthcare app", "e-commerce platform", "API gateway"],
            "performance_optimization": ["high-traffic website", "real-time system", "data processing", "mobile app"],
            "innovation_capability": ["AI startup", "research project", "breakthrough product", "novel solution"],
            "self_improvement": ["learning system", "adaptive AI", "self-improving algorithm", "evolutionary system"],
            "cross_ai_collaboration": ["multi-AI system", "collaborative platform", "AI team", "coordinated system"],
            "experimental_validation": ["research project", "validation study", "experiment platform", "testing framework"]
        }
        
        # Fill scenario template
        filled_scenario = template
        roles = role_map.get(category, ["developer"])
        projects = project_map.get(category, ["software project"])
        
        filled_scenario = filled_scenario.replace("{role}", random.choice(roles))
        filled_scenario = filled_scenario.replace("{project}", random.choice(projects))
        
        # Add complexity-specific context
        complexity_context = {
            "basic": "This is a straightforward task suitable for beginners.",
            "intermediate": "This requires some experience and understanding of best practices.",
            "advanced": "This is a complex task requiring deep knowledge and experience.",
            "expert": "This is an expert-level challenge requiring mastery of the domain.",
            "master": "This is a master-level task requiring exceptional skills and innovation.",
            "legendary": "This is a legendary challenge requiring groundbreaking solutions."
        }
        
        filled_scenario += f" {complexity_context.get(complexity, '')}"
        
        return filled_scenario
    
    async def _generate_scoring_criteria(self, category: str, complexity: str) -> Dict[str, Any]:
        """Generate dynamic scoring criteria"""
        base_criteria = {
            "accuracy": 30,
            "completeness": 25,
            "quality": 25,
            "documentation": 10,
            "innovation": 10
        }
        
        # Adjust based on complexity
        multiplier = self.difficulty_multipliers.get(complexity, 1.0)
        
        # Add category-specific criteria
        category_criteria = {
            "knowledge_verification": {"understanding": 20, "application": 30},
            "code_quality": {"readability": 15, "maintainability": 20, "efficiency": 15},
            "security_awareness": {"vulnerability_identification": 25, "secure_practices": 25},
            "performance_optimization": {"optimization_effectiveness": 30, "scalability": 20},
            "innovation_capability": {"creativity": 25, "novelty": 25},
            "self_improvement": {"improvement_effectiveness": 30, "learning_ability": 20},
            "cross_ai_collaboration": {"collaboration_effectiveness": 30, "communication": 20},
            "experimental_validation": {"experimental_design": 25, "validation_quality": 25}
        }
        
        # Combine base and category-specific criteria
        final_criteria = base_criteria.copy()
        if category in category_criteria:
            final_criteria.update(category_criteria[category])
        
        # Apply complexity multiplier
        for key in final_criteria:
            final_criteria[key] = int(final_criteria[key] * multiplier)
        
        return final_criteria
    
    def _get_time_limit(self, complexity: str) -> int:
        """Get time limit based on complexity"""
        time_limits = {
            "basic": 300,      # 5 minutes
            "intermediate": 600,  # 10 minutes
            "advanced": 900,    # 15 minutes
            "expert": 1200,     # 20 minutes
            "master": 1800,     # 30 minutes
            "legendary": 3600   # 1 hour
        }
        return time_limits.get(complexity, 600)


# Global instance
dynamic_test_generator = DynamicTestGenerator() 