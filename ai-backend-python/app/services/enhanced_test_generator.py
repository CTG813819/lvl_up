#!/usr/bin/env python3
"""
Enhanced Test Generator Service
Generates dynamic, varied, and internet-based test scenarios
Features:
- Internet knowledge integration
- Dynamic difficulty scaling (x1, x2, etc.)
- Docker simulation for real-world testing
- AI communication for collaborative responses
- Infinite scenario generation
- Training ground integration
- Neon database persistence
"""

import asyncio
import json
import uuid
import os
import requests
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import structlog
import random
import re
from bs4 import BeautifulSoup
import docker
import subprocess
import tempfile
import shutil
from sqlalchemy import text

from ..core.database import get_session
from ..core.config import settings
# Removed external API imports - using internal AI agents instead
from app.services.unified_ai_service_shared import unified_ai_service_shared
from app.models.sql_models import CustodyTestResult, InternetKnowledge, AIResponse

logger = structlog.get_logger()


class TestComplexity(Enum):
    """Test complexity levels that scale with AI progression"""
    X1 = "x1"  # Basic - Level 1-3
    X2 = "x2"  # Intermediate - Level 4-6
    X3 = "x3"  # Advanced - Level 7-9
    X4 = "x4"  # Expert - Level 10-12
    X5 = "x5"  # Master - Level 13-15
    X6 = "x6"  # Legendary - Level 16+


class TestRequirement(Enum):
    """Varied test requirements"""
    CODING = "coding"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    INNOVATION = "innovation"
    COLLABORATION = "collaboration"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"
    INTEGRATION = "integration"
    TESTING = "testing"


class EnhancedTestGenerator:
    """Enhanced Test Generator with internet knowledge, dynamic scaling, and Docker integration"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EnhancedTestGenerator, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.docker_client = None
            self.internet_knowledge_cache = {}
            self.scenario_templates = {}
            self.ai_communication_history = {}
            self._initialized = True
            self._initialize_docker()
    
    def _initialize_docker(self):
        """Initialize Docker client for real-world testing"""
        try:
            self.docker_client = docker.from_env()
            logger.info("✅ Docker client initialized")
        except Exception as e:
            logger.warning(f"⚠️ Docker not available: {str(e)}")
            self.docker_client = None
    
    @classmethod
    async def initialize(cls):
        """Initialize the enhanced test generator"""
        instance = cls()
        await instance._load_internet_knowledge()
        await instance._load_scenario_templates()
        logger.info("✅ Enhanced Test Generator initialized")
        return instance
    
    async def _load_internet_knowledge(self):
        """Load and cache internet knowledge for test generation"""
        try:
            # Fetch current tech trends and knowledge
            knowledge_sources = [
                "https://github.com/trending",
                "https://stackoverflow.com/questions/tagged/python",
                "https://news.ycombinator.com/",
                "https://dev.to/t/python",
                "https://medium.com/tag/programming"
            ]
            
            for source in knowledge_sources:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(source) as response:
                            if response.status == 200:
                                content = await response.text()
                                self.internet_knowledge_cache[source] = self._extract_knowledge(content)
                except Exception as e:
                    logger.warning(f"Failed to fetch from {source}: {str(e)}")
            
            logger.info(f"✅ Loaded internet knowledge from {len(self.internet_knowledge_cache)} sources")
            
        except Exception as e:
            logger.error(f"Error loading internet knowledge: {str(e)}")
    
    def _extract_knowledge(self, content: str) -> Dict[str, Any]:
        """Extract relevant knowledge from web content"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract trending topics, technologies, and challenges
        knowledge = {
            'trending_topics': [],
            'technologies': [],
            'challenges': [],
            'best_practices': [],
            'frameworks': []
        }
        
        # Extract text content and identify patterns
        text_content = soup.get_text()
        
        # Look for technology mentions
        tech_patterns = [
            r'\b(React|Vue|Angular|Node\.js|Python|Java|Go|Rust|TypeScript|Docker|Kubernetes)\b',
            r'\b(microservices|API|REST|GraphQL|WebSocket|JWT|OAuth)\b',
            r'\b(machine learning|AI|ML|deep learning|neural networks)\b',
            r'\b(cloud|AWS|Azure|GCP|serverless|containers)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            knowledge['technologies'].extend(matches)
        
        return knowledge
    
    async def _load_scenario_templates(self):
        """Load dynamic scenario templates"""
        self.scenario_templates = {
            'coding': [
                "Implement a {technology} application that {requirement}",
                "Create a {framework} service that handles {challenge}",
                "Build a {architecture} system with {feature}",
                "Develop a {language} solution for {problem}",
                "Design a {pattern} implementation for {use_case}"
            ],
            'architecture': [
                "Design a {scale} system architecture for {domain}",
                "Create a {pattern} architecture that supports {requirement}",
                "Build a {technology} infrastructure for {challenge}",
                "Design a {framework} solution for {problem}",
                "Architect a {system_type} that integrates {components}"
            ],
            'security': [
                "Implement {security_feature} for {vulnerability}",
                "Design a {security_pattern} system for {threat}",
                "Create {authentication} for {application}",
                "Build {encryption} for {data_type}",
                "Develop {security_measure} against {attack_type}"
            ],
            'performance': [
                "Optimize {system} for {metric}",
                "Scale {application} to handle {load}",
                "Improve {performance_aspect} of {component}",
                "Design {caching} for {data_type}",
                "Implement {optimization} for {bottleneck}"
            ],
            'collaboration': [
                "Collaborate on {project} with {team_size}",
                "Design {solution} together for {challenge}",
                "Build {system} as a team with {roles}",
                "Create {feature} collaboratively for {user}",
                "Develop {integration} between {systems}"
            ]
        }
    
    async def generate_dynamic_test_scenario(self, ai_types: List[str], difficulty: str, 
                                           test_type: str, ai_levels: Dict[str, int]) -> Dict[str, Any]:
        """Generate a dynamic test scenario based on internet knowledge, AI levels, and database knowledge"""
        
        # Update internet knowledge during learning cycle
        await self.update_internet_knowledge_from_learning_cycle()
        
        # Check if Claude tokens are available
        tokens_available = await self._check_claude_tokens_available()
        
        if tokens_available:
            logger.info("✅ Using Claude for scenario generation")
            return await self._generate_with_claude(ai_types, difficulty, test_type, ai_levels)
        else:
            logger.info("✅ Using self-generating system (no LLM calls)")
            return await self._generate_with_fallback(ai_types, difficulty, test_type, ai_levels)
    
    def _get_complexity_for_level(self, avg_level: float) -> TestComplexity:
        """Determine test complexity based on AI level"""
        if avg_level <= 3:
            return TestComplexity.X1
        elif avg_level <= 6:
            return TestComplexity.X2
        elif avg_level <= 9:
            return TestComplexity.X3
        elif avg_level <= 12:
            return TestComplexity.X4
        elif avg_level <= 15:
            return TestComplexity.X5
        else:
            return TestComplexity.X6
    
    async def _get_current_knowledge(self) -> Dict[str, Any]:
        """Get current internet knowledge and trends"""
        # Combine cached knowledge with real-time updates
        knowledge = {
            'technologies': [],
            'trends': [],
            'challenges': [],
            'frameworks': []
        }
        
        for source, source_knowledge in self.internet_knowledge_cache.items():
            knowledge['technologies'].extend(source_knowledge.get('technologies', []))
            knowledge['trends'].extend(source_knowledge.get('trending_topics', []))
            knowledge['challenges'].extend(source_knowledge.get('challenges', []))
        
        # Remove duplicates and get top items
        knowledge = {k: list(set(v))[:10] for k, v in knowledge.items()}
        
        return knowledge
    
    async def _generate_varied_requirements(self, test_type: str, complexity: TestComplexity, 
                                          knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate varied requirements based on test type and complexity"""
        
        requirements = []
        
        # Get random technologies and challenges
        technologies = random.sample(knowledge.get('technologies', ['Python', 'JavaScript', 'Docker']), 3)
        challenges = random.sample(knowledge.get('challenges', ['scalability', 'security', 'performance']), 2)
        
        # Generate different requirement types
        requirement_types = [
            TestRequirement.CODING,
            TestRequirement.ARCHITECTURE,
            TestRequirement.SECURITY,
            TestRequirement.PERFORMANCE,
            TestRequirement.INTEGRATION
        ]
        
        for req_type in random.sample(requirement_types, 3):  # Pick 3 random types
            requirement = await self._create_requirement(req_type, technologies, challenges, complexity)
            requirements.append(requirement)
        
        return requirements
    
    async def _create_requirement(self, req_type: TestRequirement, technologies: List[str], 
                                 challenges: List[str], complexity: TestComplexity) -> Dict[str, Any]:
        """Create a specific requirement"""
        
        templates = {
            TestRequirement.CODING: [
                "Implement {technology} with {feature}",
                "Create {component} using {pattern}",
                "Build {service} with {requirement}",
                "Develop {functionality} in {language}",
                "Code {feature} with {constraint}"
            ],
            TestRequirement.ARCHITECTURE: [
                "Design {system} architecture for {scale}",
                "Create {pattern} for {domain}",
                "Build {infrastructure} supporting {load}",
                "Architect {solution} with {components}",
                "Design {framework} for {requirement}"
            ],
            TestRequirement.SECURITY: [
                "Implement {security} for {vulnerability}",
                "Add {protection} against {threat}",
                "Secure {component} with {method}",
                "Create {authentication} for {access}",
                "Build {encryption} for {data}"
            ],
            TestRequirement.PERFORMANCE: [
                "Optimize {component} for {metric}",
                "Scale {system} to handle {load}",
                "Improve {aspect} of {service}",
                "Enhance {performance} of {feature}",
                "Optimize {bottleneck} in {application}"
            ],
            TestRequirement.INTEGRATION: [
                "Integrate {service} with {api}",
                "Connect {system} to {platform}",
                "Bridge {component} and {service}",
                "Link {application} with {database}",
                "Merge {feature} with {functionality}"
            ]
        }
        
        template = random.choice(templates[req_type])
        
        # Fill template with dynamic content
        requirement = {
            'type': req_type.value,
            'description': template.format(
                technology=random.choice(technologies),
                feature=random.choice(['async/await', 'error handling', 'logging', 'caching', 'validation']),
                component=random.choice(['API', 'service', 'module', 'library', 'framework']),
                pattern=random.choice(['MVC', 'MVVM', 'Repository', 'Factory', 'Observer']),
                service=random.choice(['authentication', 'authorization', 'caching', 'messaging', 'monitoring']),
                requirement=random.choice(['scalability', 'reliability', 'maintainability', 'testability']),
                functionality=random.choice(['user management', 'data processing', 'file handling', 'communication']),
                language=random.choice(['Python', 'JavaScript', 'TypeScript', 'Go', 'Rust']),
                constraint=random.choice(['memory efficient', 'thread safe', 'type safe', 'async']),
                system=random.choice(['microservices', 'monolith', 'distributed', 'event-driven']),
                scale=random.choice(['thousands', 'millions', 'billions']),
                domain=random.choice(['e-commerce', 'healthcare', 'finance', 'education', 'gaming']),
                infrastructure=random.choice(['cloud-native', 'containerized', 'serverless', 'hybrid']),
                load=random.choice(['high traffic', 'real-time', 'batch processing', 'streaming']),
                components=random.choice(['databases', 'caches', 'queues', 'APIs', 'services']),
                security=random.choice(['authentication', 'authorization', 'encryption', 'validation']),
                vulnerability=random.choice(['SQL injection', 'XSS', 'CSRF', 'injection', 'overflow']),
                protection=random.choice(['input validation', 'output encoding', 'rate limiting', 'WAF']),
                threat=random.choice(['malware', 'phishing', 'DDoS', 'data breach', 'insider threat']),
                method=random.choice(['JWT', 'OAuth', 'SAML', '2FA', 'biometric']),
                access=random.choice(['user data', 'admin panel', 'API endpoints', 'database']),
                encryption=random.choice(['AES', 'RSA', 'ChaCha20', 'AES-GCM']),
                data=random.choice(['user credentials', 'payment info', 'personal data', 'sensitive files']),
                metric=random.choice(['response time', 'throughput', 'latency', 'memory usage']),
                aspect=random.choice(['performance', 'efficiency', 'speed', 'resource usage']),
                bottleneck=random.choice(['database queries', 'API calls', 'file I/O', 'network requests']),
                application=random.choice(['web app', 'mobile app', 'desktop app', 'API service']),
                api=random.choice(['REST API', 'GraphQL', 'gRPC', 'WebSocket', 'GraphQL']),
                platform=random.choice(['AWS', 'Azure', 'GCP', 'Heroku', 'DigitalOcean']),
                database=random.choice(['PostgreSQL', 'MongoDB', 'Redis', 'MySQL', 'Cassandra'])
            ),
            'complexity': complexity.value,
            'technologies': random.sample(technologies, min(2, len(technologies))),
            'challenges': random.sample(challenges, min(1, len(challenges)))
        }
        
        return requirement
    
    async def _create_dynamic_scenario(self, requirements: List[Dict[str, Any]], 
                                     ai_types: List[str], complexity: TestComplexity) -> Dict[str, Any]:
        """Create a dynamic scenario from requirements"""
        
        scenario = {
            'id': str(uuid.uuid4()),
            'type': 'dynamic_test',
            'complexity': complexity.value,
            'participants': ai_types,
            'requirements': requirements,
            'description': await self._generate_scenario_description(requirements, ai_types, complexity),
            'success_criteria': await self._generate_success_criteria(requirements, complexity),
            'time_limit': self._get_time_limit(complexity),
            'created_at': datetime.utcnow().isoformat(),
            'docker_enabled': self.docker_client is not None
        }
        
        return scenario
    
    async def _generate_scenario_description(self, requirements: List[Dict[str, Any]], 
                                           ai_types: List[str], complexity: TestComplexity) -> str:
        """Generate a comprehensive scenario description"""
        
        description_parts = [
            f"You are working with {len(ai_types)} AI systems: {', '.join(ai_types)}.",
            f"This is a {complexity.value} complexity test that requires collaboration.",
            "Your task is to:"
        ]
        
        for i, req in enumerate(requirements, 1):
            description_parts.append(f"{i}. {req['description']}")
        
        description_parts.extend([
            "You must work together to create a comprehensive solution.",
            "Each AI should contribute their expertise to different aspects of the solution.",
            "The final solution should be production-ready and well-documented."
        ])
        
        return "\n".join(description_parts)
    
    async def _generate_success_criteria(self, requirements: List[Dict[str, Any]], 
                                       complexity: TestComplexity) -> List[str]:
        """Generate success criteria based on requirements and complexity"""
        
        criteria = []
        
        for req in requirements:
            if req['type'] == 'coding':
                criteria.extend([
                    f"Code is {req['description']}",
                    "Code follows best practices",
                    "Code is well-documented",
                    "Code includes error handling"
                ])
            elif req['type'] == 'architecture':
                criteria.extend([
                    f"Architecture supports {req['description']}",
                    "System is scalable and maintainable",
                    "Components are properly decoupled",
                    "Architecture follows design patterns"
                ])
            elif req['type'] == 'security':
                criteria.extend([
                    f"Security measures implement {req['description']}",
                    "No security vulnerabilities",
                    "Proper authentication and authorization",
                    "Data is encrypted where necessary"
                ])
            elif req['type'] == 'performance':
                criteria.extend([
                    f"Performance meets {req['description']}",
                    "System handles expected load",
                    "Response times are acceptable",
                    "Resource usage is optimized"
                ])
            elif req['type'] == 'integration':
                criteria.extend([
                    f"Integration successfully {req['description']}",
                    "APIs are properly connected",
                    "Data flows correctly between systems",
                    "Error handling for integration points"
                ])
        
        # Add complexity-based criteria
        if complexity.value in ['x4', 'x5', 'x6']:
            criteria.extend([
                "Solution includes comprehensive testing",
                "Documentation is complete and professional",
                "Code is production-ready",
                "Performance benchmarks are met"
            ])
        
        return criteria
    
    def _get_time_limit(self, complexity: TestComplexity) -> int:
        """Get time limit based on complexity"""
        limits = {
            TestComplexity.X1: 30,   # 30 minutes
            TestComplexity.X2: 45,   # 45 minutes
            TestComplexity.X3: 60,   # 1 hour
            TestComplexity.X4: 90,   # 1.5 hours
            TestComplexity.X5: 120,  # 2 hours
            TestComplexity.X6: 180   # 3 hours
        }
        return limits[complexity]
    
    async def _generate_docker_config(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Docker configuration for real-world testing"""
        
        if not self.docker_client:
            return {}
        
        # Create Dockerfile based on scenario requirements
        dockerfile_content = self._create_dockerfile(scenario)
        
        # Create docker-compose.yml for multi-service testing
        compose_content = self._create_docker_compose(scenario)
        
        return {
            'dockerfile': dockerfile_content,
            'docker_compose': compose_content,
            'test_script': self._create_test_script(scenario),
            'environment': self._create_environment_config(scenario)
        }
    
    def _create_dockerfile(self, scenario: Dict[str, Any]) -> str:
        """Create a Dockerfile for the scenario"""
        
        # Determine base image based on requirements
        technologies = []
        for req in scenario['requirements']:
            technologies.extend(req.get('technologies', []))
        
        if 'Python' in technologies:
            base_image = "python:3.11-slim"
            setup_commands = [
                "RUN pip install --no-cache-dir -r requirements.txt"
            ]
        elif 'Node.js' in technologies or 'JavaScript' in technologies:
            base_image = "node:18-alpine"
            setup_commands = [
                "RUN npm install"
            ]
        else:
            base_image = "ubuntu:22.04"
            setup_commands = [
                "RUN apt-get update && apt-get install -y build-essential"
            ]
        
        dockerfile = f"""
FROM {base_image}

WORKDIR /app

COPY requirements.txt .
{' '.join(setup_commands)}

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
"""
        
        return dockerfile
    
    def _create_docker_compose(self, scenario: Dict[str, Any]) -> str:
        """Create docker-compose.yml for multi-service testing"""
        
        services = {
            'app': {
                'build': '.',
                'ports': ['8000:8000'],
                'environment': ['DEBUG=1'],
                'volumes': ['./data:/app/data']
            }
        }
        
        # Add database if needed
        if any('database' in req['description'].lower() for req in scenario['requirements']):
            services['database'] = {
                'image': 'postgres:15',
                'environment': [
                    'POSTGRES_DB=testdb',
                    'POSTGRES_USER=testuser',
                    'POSTGRES_PASSWORD=testpass'
                ],
                'ports': ['5432:5432']
            }
        
        # Add cache if needed
        if any('cache' in req['description'].lower() for req in scenario['requirements']):
            services['cache'] = {
                'image': 'redis:7-alpine',
                'ports': ['6379:6379']
            }
        
        compose_content = f"""
version: '3.8'

services:
{self._format_services(services)}
"""
        
        return compose_content
    
    def _format_services(self, services: Dict[str, Any]) -> str:
        """Format services for docker-compose.yml"""
        formatted = []
        for service_name, config in services.items():
            formatted.append(f"  {service_name}:")
            for key, value in config.items():
                if isinstance(value, list):
                    formatted.append(f"    {key}:")
                    for item in value:
                        formatted.append(f"      - {item}")
                else:
                    formatted.append(f"    {key}: {value}")
        return "\n".join(formatted)
    
    def _create_test_script(self, scenario: Dict[str, Any]) -> str:
        """Create a test script for Docker validation"""
        
        script = """#!/bin/bash
set -e

echo "Running scenario tests..."

# Test basic functionality
python -c "
import requests
import time

# Test API endpoints
response = requests.get('http://localhost:8000/health')
assert response.status_code == 200

# Test main functionality
response = requests.post('http://localhost:8000/api/test', json={'test': 'data'})
assert response.status_code == 200

print('All tests passed!')
"

echo "Scenario validation completed successfully!"
"""
        
        return script
    
    def _create_environment_config(self, scenario: Dict[str, Any]) -> Dict[str, str]:
        """Create environment configuration"""
        
        env_vars = {
            'DEBUG': '1',
            'TEST_MODE': 'true',
            'SCENARIO_ID': scenario['id']
        }
        
        # Add technology-specific environment variables
        for req in scenario['requirements']:
            if 'database' in req['description'].lower():
                env_vars['DATABASE_URL'] = 'postgresql://testuser:testpass@database:5432/testdb'
            if 'cache' in req['description'].lower():
                env_vars['REDIS_URL'] = 'redis://cache:6379'
            if 'api' in req['description'].lower():
                env_vars['API_KEY'] = 'test-api-key'
        
        return env_vars
    
    async def _persist_scenario_to_database(self, scenario: Dict[str, Any]):
        """Persist scenario to Neon database"""
        
        try:
            async with get_session() as session:
                # Create TestScenario record
                test_scenario = TestScenario(
                    id=scenario['id'],
                    type=scenario['type'],
                    complexity=scenario['complexity'],
                    participants=json.dumps(scenario['participants']),
                    requirements=json.dumps(scenario['requirements']),
                    description=scenario['description'],
                    success_criteria=json.dumps(scenario['success_criteria']),
                    time_limit=scenario['time_limit'],
                    docker_config=json.dumps(scenario.get('docker_config', {})),
                    created_at=datetime.fromisoformat(scenario['created_at'])
                )
                
                session.add(test_scenario)
                await session.commit()
                
                logger.info(f"✅ Scenario {scenario['id']} persisted to database")
                
        except Exception as e:
            logger.error(f"❌ Failed to persist scenario: {str(e)}")
    
    async def generate_ai_communication_scenario(self, ai_types: List[str], 
                                               scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a scenario where AIs communicate to create self-generated responses"""
        
        communication_scenario = {
            'id': str(uuid.uuid4()),
            'type': 'ai_communication',
            'participants': ai_types,
            'scenario': scenario,
            'communication_rounds': await self._generate_communication_rounds(ai_types, scenario),
            'collaboration_rules': self._get_collaboration_rules(ai_types),
            'expected_outcome': await self._generate_expected_outcome(scenario)
        }
        
        # Store communication scenario in database
        await self._persist_communication_scenario(communication_scenario)
        
        return communication_scenario
    
    async def _generate_communication_rounds(self, ai_types: List[str], 
                                           scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate communication rounds for AI collaboration"""
        
        rounds = []
        
        # Planning round
        rounds.append({
            'round': 1,
            'type': 'planning',
            'instructions': f"Each AI should analyze the scenario and propose their approach to: {scenario['description'][:200]}...",
            'expected_output': 'Individual analysis and proposed approach',
            'time_limit': 300  # 5 minutes
        })
        
        # Discussion round
        rounds.append({
            'round': 2,
            'type': 'discussion',
            'instructions': "AIs should discuss their approaches, identify synergies, and plan integration points.",
            'expected_output': 'Collaborative plan and integration strategy',
            'time_limit': 600  # 10 minutes
        })
        
        # Implementation round
        rounds.append({
            'round': 3,
            'type': 'implementation',
            'instructions': "AIs should work together to implement the agreed solution, each contributing their expertise.",
            'expected_output': 'Integrated solution with clear contributions',
            'time_limit': 1800  # 30 minutes
        })
        
        # Review round
        rounds.append({
            'round': 4,
            'type': 'review',
            'instructions': "AIs should review the solution, identify improvements, and validate against success criteria.",
            'expected_output': 'Final solution with validation and improvements',
            'time_limit': 300  # 5 minutes
        })
        
        return rounds
    
    def _get_collaboration_rules(self, ai_types: List[str]) -> List[str]:
        """Get collaboration rules for AI communication"""
        
        rules = [
            "Each AI must contribute their unique expertise",
            "AIs should communicate clearly and respectfully",
            "Decisions should be made collaboratively",
            "Each AI should validate the contributions of others",
            "The final solution should integrate all perspectives",
            "AIs should document their contributions clearly",
            "Time limits must be respected for each round",
            "AIs should ask clarifying questions when needed"
        ]
        
        return rules
    
    async def _generate_expected_outcome(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generate expected outcome for the communication scenario"""
        
        return {
            'solution_quality': 'High - integrating multiple AI perspectives',
            'collaboration_effectiveness': 'Strong - clear communication and coordination',
            'innovation_level': 'Enhanced - diverse AI approaches combined',
            'documentation_quality': 'Comprehensive - multiple AI contributions documented',
            'testing_coverage': 'Thorough - multiple AI validation perspectives'
        }
    
    async def _persist_communication_scenario(self, communication_scenario: Dict[str, Any]):
        """Persist AI communication scenario to database"""
        
        try:
            async with get_session() as session:
                # Create AICommunication record
                ai_communication = AICommunication(
                    id=communication_scenario['id'],
                    participants=json.dumps(communication_scenario['participants']),
                    scenario_id=communication_scenario['scenario']['id'],
                    communication_rounds=json.dumps(communication_scenario['communication_rounds']),
                    collaboration_rules=json.dumps(communication_scenario['collaboration_rules']),
                    expected_outcome=json.dumps(communication_scenario['expected_outcome']),
                    created_at=datetime.utcnow()
                )
                
                session.add(ai_communication)
                await session.commit()
                
                logger.info(f"✅ Communication scenario {communication_scenario['id']} persisted to database")
                
        except Exception as e:
            logger.error(f"❌ Failed to persist communication scenario: {str(e)}")
    
    async def get_training_ground_integration(self, ai_type: str) -> Dict[str, Any]:
        """Get training ground results to inform test difficulty"""
        
        try:
            async with get_session() as session:
                # Query training ground results
                query = text("""
                    SELECT * FROM training_ground_results 
                    WHERE ai_type = :ai_type 
                    ORDER BY created_at DESC 
                    LIMIT 10
                """)
                
                result = await session.execute(query, {'ai_type': ai_type})
                training_results = result.fetchall()
                
                if training_results:
                    # Analyze training performance
                    recent_performance = self._analyze_training_performance(training_results)
                    
                    return {
                        'recent_performance': recent_performance,
                        'strengths': self._identify_strengths(training_results),
                        'weaknesses': self._identify_weaknesses(training_results),
                        'difficulty_adjustment': self._calculate_difficulty_adjustment(recent_performance)
                    }
                
                return {
                    'recent_performance': 0.5,  # Default
                    'strengths': [],
                    'weaknesses': [],
                    'difficulty_adjustment': 0
                }
                
        except Exception as e:
            logger.error(f"Error getting training ground integration: {str(e)}")
            return {
                'recent_performance': 0.5,
                'strengths': [],
                'weaknesses': [],
                'difficulty_adjustment': 0
            }
    
    def _analyze_training_performance(self, training_results: List) -> float:
        """Analyze training ground performance"""
        
        if not training_results:
            return 0.5
        
        # Calculate average performance
        performances = [result.performance_score for result in training_results if hasattr(result, 'performance_score')]
        
        if performances:
            return sum(performances) / len(performances)
        
        return 0.5
    
    def _identify_strengths(self, training_results: List) -> List[str]:
        """Identify AI strengths from training results"""
        
        strengths = []
        
        for result in training_results:
            if hasattr(result, 'strengths') and result.strengths:
                strengths.extend(json.loads(result.strengths))
        
        # Get most common strengths
        strength_counts = {}
        for strength in strengths:
            strength_counts[strength] = strength_counts.get(strength, 0) + 1
        
        return [strength for strength, count in sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    def _identify_weaknesses(self, training_results: List) -> List[str]:
        """Identify AI weaknesses from training results"""
        
        weaknesses = []
        
        for result in training_results:
            if hasattr(result, 'weaknesses') and result.weaknesses:
                weaknesses.extend(json.loads(result.weaknesses))
        
        # Get most common weaknesses
        weakness_counts = {}
        for weakness in weaknesses:
            weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
        
        return [weakness for weakness, count in sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    def _calculate_difficulty_adjustment(self, performance: float) -> int:
        """Calculate difficulty adjustment based on performance"""
        
        if performance > 0.8:
            return 1  # Increase difficulty
        elif performance < 0.3:
            return -1  # Decrease difficulty
        else:
            return 0  # Keep current difficulty 
    
    async def get_ai_knowledge_from_database(self, ai_type: str) -> Dict[str, Any]:
        """Get AI learning history and knowledge from Neon database"""
        
        try:
            async with get_session() as session:
                # Get learning history
                learning_query = text("""
                    SELECT * FROM ai_learning_history 
                    WHERE ai_type = :ai_type 
                    ORDER BY created_at DESC 
                    LIMIT 50
                """)
                
                learning_result = await session.execute(learning_query, {'ai_type': ai_type})
                learning_history = learning_result.fetchall()
                
                # Get recent proposals
                proposal_query = text("""
                    SELECT * FROM proposals 
                    WHERE ai_type = :ai_type 
                    ORDER BY created_at DESC 
                    LIMIT 20
                """)
                
                proposal_result = await session.execute(proposal_query, {'ai_type': ai_type})
                recent_proposals = proposal_result.fetchall()
                
                # Get custody test results
                custody_query = text("""
                    SELECT * FROM custody_test_results 
                    WHERE ai_type = :ai_type 
                    ORDER BY created_at DESC 
                    LIMIT 30
                """)
                
                custody_result = await session.execute(custody_query, {'ai_type': ai_type})
                custody_results = custody_result.fetchall()
                
                # Get agent metrics
                metrics_query = text("""
                    SELECT * FROM agent_metrics 
                    WHERE agent_type = :ai_type
                """)
                
                metrics_result = await session.execute(metrics_query, {'ai_type': ai_type})
                agent_metrics = metrics_result.fetchone()
                
                # Analyze knowledge patterns
                knowledge_patterns = self._analyze_knowledge_patterns(learning_history, recent_proposals, custody_results)
                
                return {
                    'learning_history': learning_history,
                    'recent_proposals': recent_proposals,
                    'custody_results': custody_results,
                    'agent_metrics': agent_metrics,
                    'knowledge_patterns': knowledge_patterns,
                    'strengths': knowledge_patterns.get('strengths', []),
                    'weaknesses': knowledge_patterns.get('weaknesses', []),
                    'learning_topics': knowledge_patterns.get('learning_topics', []),
                    'skill_levels': knowledge_patterns.get('skill_levels', {})
                }
                
        except Exception as e:
            logger.error(f"Error getting AI knowledge from database: {str(e)}")
            return {
                'learning_history': [],
                'recent_proposals': [],
                'custody_results': [],
                'agent_metrics': None,
                'knowledge_patterns': {},
                'strengths': [],
                'weaknesses': [],
                'learning_topics': [],
                'skill_levels': {}
            }
    
    def _analyze_knowledge_patterns(self, learning_history: List, recent_proposals: List, custody_results: List) -> Dict[str, Any]:
        """Analyze AI knowledge patterns from database data"""
        
        patterns = {
            'strengths': [],
            'weaknesses': [],
            'learning_topics': [],
            'skill_levels': {},
            'improvement_areas': [],
            'success_patterns': []
        }
        
        # Analyze learning history
        for record in learning_history:
            if hasattr(record, 'learning_event'):
                event = record.learning_event
                if 'success' in event.lower() or 'passed' in event.lower():
                    patterns['success_patterns'].append(event)
                elif 'failed' in event.lower() or 'error' in event.lower():
                    patterns['weaknesses'].append(event)
        
        # Analyze proposals
        for proposal in recent_proposals:
            if hasattr(proposal, 'status'):
                if proposal.status == 'accepted':
                    patterns['strengths'].append('proposal_accepted')
                elif proposal.status == 'rejected':
                    patterns['weaknesses'].append('proposal_rejected')
        
        # Analyze custody results
        for result in custody_results:
            if hasattr(result, 'test_category'):
                category = result.test_category
                if hasattr(result, 'passed') and result.passed:
                    patterns['strengths'].append(f"{category}_mastery")
                else:
                    patterns['weaknesses'].append(f"{category}_needs_improvement")
        
        # Get most common patterns
        patterns['strengths'] = list(set(patterns['strengths']))[:5]
        patterns['weaknesses'] = list(set(patterns['weaknesses']))[:5]
        
        return patterns
    
    async def update_internet_knowledge_from_learning_cycle(self):
        """Update internet knowledge during learning cycles"""
        
        try:
            # Fetch new knowledge sources
            new_sources = [
                "https://github.com/trending?since=daily",
                "https://stackoverflow.com/questions/tagged/python?sort=newest",
                "https://news.ycombinator.com/newest",
                "https://dev.to/t/python/latest",
                "https://medium.com/tag/programming/latest",
                "https://reddit.com/r/programming/new/",
                "https://techcrunch.com/tag/artificial-intelligence/",
                "https://arxiv.org/list/cs.AI/recent"
            ]
            
            for source in new_sources:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(source) as response:
                            if response.status == 200:
                                content = await response.text()
                                new_knowledge = self._extract_knowledge(content)
                                
                                # Store in database
                                await self._store_internet_knowledge(source, new_knowledge)
                                
                                # Update cache
                                self.internet_knowledge_cache[source] = new_knowledge
                                
                except Exception as e:
                    logger.warning(f"Failed to fetch from {source}: {str(e)}")
            
            logger.info("✅ Internet knowledge updated from learning cycle")
            
        except Exception as e:
            logger.error(f"Error updating internet knowledge: {str(e)}")
    
    async def _store_internet_knowledge(self, source: str, knowledge: Dict[str, Any]):
        """Store internet knowledge in Neon database"""
        
        try:
            async with get_session() as session:
                # Store each piece of knowledge
                for topic, content in knowledge.items():
                    if isinstance(content, list) and content:
                        for item in content[:10]:  # Store top 10 items
                            internet_knowledge = InternetKnowledge(
                                source=source,
                                source_type=self._get_source_type(source),
                                topic=topic,
                                content=str(item),
                                extracted_knowledge=json.dumps({topic: item}),
                                relevance_score=0.8,  # Default relevance
                                last_fetched=datetime.utcnow()
                            )
                            session.add(internet_knowledge)
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"Error storing internet knowledge: {str(e)}")
    
    def _get_source_type(self, source: str) -> str:
        """Determine source type from URL"""
        if 'github.com' in source:
            return 'github'
        elif 'stackoverflow.com' in source:
            return 'stackoverflow'
        elif 'news.ycombinator.com' in source:
            return 'hackernews'
        elif 'dev.to' in source:
            return 'devto'
        elif 'medium.com' in source:
            return 'medium'
        elif 'reddit.com' in source:
            return 'reddit'
        elif 'techcrunch.com' in source:
            return 'techcrunch'
        elif 'arxiv.org' in source:
            return 'arxiv'
        else:
            return 'other'
    
    async def generate_scenario_from_ai_knowledge(self, ai_types: List[str], difficulty: str, 
                                                test_type: str) -> Dict[str, Any]:
        """Generate scenario using AI knowledge from database"""
        
        # Get AI knowledge for each participant
        ai_knowledge = {}
        for ai_type in ai_types:
            ai_knowledge[ai_type] = await self.get_ai_knowledge_from_database(ai_type)
        
        # Combine knowledge patterns
        combined_strengths = []
        combined_weaknesses = []
        combined_topics = []
        
        for ai_type, knowledge in ai_knowledge.items():
            combined_strengths.extend(knowledge.get('strengths', []))
            combined_weaknesses.extend(knowledge.get('weaknesses', []))
            combined_topics.extend(knowledge.get('learning_topics', []))
        
        # Remove duplicates
        combined_strengths = list(set(combined_strengths))
        combined_weaknesses = list(set(combined_weaknesses))
        combined_topics = list(set(combined_topics))
        
        # Generate scenario based on knowledge patterns
        scenario = await self._create_knowledge_based_scenario(
            combined_strengths, combined_weaknesses, combined_topics, 
            ai_types, difficulty, test_type
        )
        
        return scenario
    
    async def _create_knowledge_based_scenario(self, strengths: List[str], weaknesses: List[str], 
                                             topics: List[str], ai_types: List[str], 
                                             difficulty: str, test_type: str) -> Dict[str, Any]:
        """Create scenario based on AI knowledge patterns"""
        
        # Determine complexity based on difficulty
        complexity = self._get_complexity_for_difficulty(difficulty)
        
        # Create requirements based on knowledge patterns
        requirements = []
        
        # Add strength-based requirements (challenge their strengths)
        for strength in strengths[:2]:  # Use top 2 strengths
            requirement = await self._create_strength_challenge(strength, complexity)
            requirements.append(requirement)
        
        # Add weakness-based requirements (help improve weaknesses)
        for weakness in weaknesses[:2]:  # Use top 2 weaknesses
            requirement = await self._create_weakness_improvement(weakness, complexity)
            requirements.append(requirement)
        
        # Add topic-based requirements
        for topic in topics[:2]:  # Use top 2 topics
            requirement = await self._create_topic_requirement(topic, complexity)
            requirements.append(requirement)
        
        # Create scenario description
        description = await self._generate_knowledge_based_description(
            requirements, ai_types, complexity, test_type
        )
        
        return {
            'id': str(uuid.uuid4()),
            'type': test_type,
            'complexity': complexity.value,
            'participants': ai_types,
            'requirements': requirements,
            'description': description,
            'success_criteria': await self._generate_success_criteria(requirements, complexity),
            'time_limit': self._get_time_limit(complexity),
            'created_at': datetime.utcnow().isoformat(),
            'knowledge_based': True,
            'strengths_used': strengths[:2],
            'weaknesses_addressed': weaknesses[:2],
            'topics_integrated': topics[:2]
        }
    
    def _get_complexity_for_difficulty(self, difficulty: str) -> TestComplexity:
        """Get complexity based on difficulty string"""
        difficulty_map = {
            'basic': TestComplexity.X1,
            'intermediate': TestComplexity.X2,
            'advanced': TestComplexity.X3,
            'expert': TestComplexity.X4,
            'master': TestComplexity.X5,
            'legendary': TestComplexity.X6
        }
        return difficulty_map.get(difficulty.lower(), TestComplexity.X2)
    
    async def _create_strength_challenge(self, strength: str, complexity: TestComplexity) -> Dict[str, Any]:
        """Create a requirement that challenges an AI's strength"""
        
        strength_challenges = {
            'proposal_accepted': "Create an even more innovative proposal that builds on your successful track record",
            'code_quality_mastery': "Implement a complex system with exceptional code quality and maintainability",
            'security_awareness_mastery': "Design a security system that goes beyond standard practices",
            'performance_optimization_mastery': "Optimize a system for extreme performance under heavy load",
            'architecture_mastery': "Design a scalable architecture for a complex distributed system"
        }
        
        challenge = strength_challenges.get(strength, f"Demonstrate advanced mastery in {strength}")
        
        return {
            'type': 'strength_challenge',
            'description': challenge,
            'complexity': complexity.value,
            'target_strength': strength
        }
    
    async def _create_weakness_improvement(self, weakness: str, complexity: TestComplexity) -> Dict[str, Any]:
        """Create a requirement that helps improve a weakness"""
        
        improvement_requirements = {
            'proposal_rejected': "Create a proposal with enhanced validation and user feedback integration",
            'code_quality_needs_improvement': "Implement comprehensive error handling and documentation",
            'security_awareness_needs_improvement': "Implement multi-layer security with threat modeling",
            'performance_optimization_needs_improvement': "Optimize for both speed and resource efficiency",
            'architecture_needs_improvement': "Design a robust architecture with clear separation of concerns"
        }
        
        improvement = improvement_requirements.get(weakness, f"Improve your approach to {weakness}")
        
        return {
            'type': 'weakness_improvement',
            'description': improvement,
            'complexity': complexity.value,
            'target_weakness': weakness
        }
    
    async def _create_topic_requirement(self, topic: str, complexity: TestComplexity) -> Dict[str, Any]:
        """Create a requirement based on a learning topic"""
        
        return {
            'type': 'topic_integration',
            'description': f"Integrate your knowledge of {topic} into a practical solution",
            'complexity': complexity.value,
            'learning_topic': topic
        }
    
    async def _generate_knowledge_based_description(self, requirements: List[Dict[str, Any]], 
                                                  ai_types: List[str], complexity: TestComplexity, 
                                                  test_type: str) -> str:
        """Generate scenario description based on knowledge requirements"""
        
        description_parts = [
            f"You are working with {len(ai_types)} AI systems: {', '.join(ai_types)}.",
            f"This is a {complexity.value} complexity {test_type} test based on your learning history.",
            "Your task is to:"
        ]
        
        for i, req in enumerate(requirements, 1):
            description_parts.append(f"{i}. {req['description']}")
        
        description_parts.extend([
            "You must work together to create a comprehensive solution.",
            "Each AI should contribute their expertise to different aspects of the solution.",
            "The final solution should be production-ready and well-documented."
        ])
        
        return "\n".join(description_parts)
    
    async def calculate_xp_with_difficulty_integration(self, base_score: float, complexity: TestComplexity, 
                                                      difficulty: str, test_type: str, 
                                                      ai_levels: Dict[str, int]) -> Dict[str, int]:
        """Calculate XP with difficulty and complexity integration"""
        
        # Base XP calculation
        base_xp = 50
        
        # Difficulty multipliers
        difficulty_multipliers = {
            'basic': 1.0,
            'intermediate': 1.5,
            'advanced': 2.0,
            'expert': 2.5,
            'master': 3.0,
            'legendary': 4.0
        }
        
        # Complexity multipliers (x1, x2, x3, etc.)
        complexity_multipliers = {
            TestComplexity.X1: 1.0,
            TestComplexity.X2: 1.2,
            TestComplexity.X3: 1.5,
            TestComplexity.X4: 2.0,
            TestComplexity.X5: 2.5,
            TestComplexity.X6: 3.0
        }
        
        # Test type multipliers
        test_type_multipliers = {
            'custody': 1.0,
            'olympic': 1.5,
            'collaborative': 1.3,
            'adversarial': 1.8
        }
        
        # Level-based multipliers (higher levels get more XP)
        avg_level = sum(ai_levels.values()) / len(ai_levels)
        level_multiplier = 1.0 + (avg_level - 1) * 0.1  # 10% increase per level
        
        # Calculate final XP
        difficulty_mult = difficulty_multipliers.get(difficulty.lower(), 1.0)
        complexity_mult = complexity_multipliers.get(complexity, 1.0)
        test_type_mult = test_type_multipliers.get(test_type, 1.0)
        
        # Score-based adjustment (0-100 scale)
        score_multiplier = base_score / 100.0
        
        # Final XP calculation
        final_xp = int(base_xp * difficulty_mult * complexity_mult * test_type_mult * level_multiplier * score_multiplier)
        
        # Ensure minimum XP
        final_xp = max(final_xp, 10)
        
        return {
            'base_xp': base_xp,
            'difficulty_multiplier': difficulty_mult,
            'complexity_multiplier': complexity_mult,
            'test_type_multiplier': test_type_mult,
            'level_multiplier': level_multiplier,
            'score_multiplier': score_multiplier,
            'final_xp': final_xp
        }
    
    async def generate_dynamic_test_scenario(self, ai_types: List[str], difficulty: str, 
                                           test_type: str, ai_levels: Dict[str, int]) -> Dict[str, Any]:
        """Generate a dynamic test scenario based on internet knowledge, AI levels, and database knowledge"""
        
        # Update internet knowledge during learning cycle
        await self.update_internet_knowledge_from_learning_cycle()
        
        # Check if Claude tokens are available
        tokens_available = await self._check_claude_tokens_available()
        
        if tokens_available:
            logger.info("✅ Using Claude for scenario generation")
            return await self._generate_with_claude(ai_types, difficulty, test_type, ai_levels)
        else:
            logger.info("✅ Using self-generating system (no LLM calls)")
            return await self._generate_with_fallback(ai_types, difficulty, test_type, ai_levels)
    
    async def generate_ai_self_generated_response(self, ai_type: str, scenario: Dict[str, Any], 
                                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate self-generated response from AI using real knowledge and internet data"""
        
        try:
            # Get AI knowledge and capabilities from database
            ai_knowledge = await self.get_ai_knowledge_from_database(ai_type)
            ai_level = await self._get_ai_level(ai_type)
            
            # Get current internet knowledge for real-time trends
            current_knowledge = await self._get_current_knowledge()
            
            # Determine response types based on scenario requirements
            response_types = self._determine_response_types(scenario)
            
            # Generate comprehensive response using real data
            response = {
                'ai_type': ai_type,
                'ai_level': ai_level,
                'scenario_id': scenario.get('id'),
                'response_types': response_types,
                'generated_content': {},
                'languages_used': [],
                'architecture_components': [],
                'code_snippets': [],
                'documentation': '',
                'testing_approach': '',
                'performance_considerations': '',
                'security_measures': '',
                'deployment_strategy': '',
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Generate code based on AI knowledge and current technologies
            if 'coding' in response_types:
                response['generated_content']['code'] = await self._generate_live_code_from_knowledge(
                    scenario, ai_knowledge, current_knowledge
                )
                response['languages_used'] = list(response['generated_content']['code'].keys())
            
            # Generate architecture based on AI strengths and current trends
            if 'architecture' in response_types:
                response['generated_content']['architecture'] = await self._generate_live_architecture_from_knowledge(
                    scenario, ai_knowledge, current_knowledge
                )
                response['architecture_components'] = response['generated_content']['architecture'].get('components', [])
            
            # Generate documentation based on AI learning history
            if 'documentation' in response_types:
                response['generated_content']['documentation'] = await self._generate_live_documentation_from_knowledge(
                    scenario, ai_knowledge, current_knowledge
                )
            
            # Generate testing strategy based on AI experience
            if 'testing' in response_types:
                response['generated_content']['testing'] = await self._generate_live_testing_from_knowledge(
                    scenario, ai_knowledge, current_knowledge
                )
            
            # Generate deployment strategy based on current best practices
            if 'deployment' in response_types:
                response['generated_content']['deployment'] = await self._generate_live_deployment_from_knowledge(
                    scenario, ai_knowledge, current_knowledge
                )
            
            # Generate security measures based on AI security knowledge
            if 'security' in response_types:
                response['generated_content']['security'] = await self._generate_live_security_from_knowledge(
                    scenario, ai_knowledge, current_knowledge
                )
            
            # Generate performance optimization based on AI experience
            if 'performance' in response_types:
                response['generated_content']['performance'] = await self._generate_live_performance_from_knowledge(
                    scenario, ai_knowledge, current_knowledge
                )
            
            # Store response in database
            await self._persist_ai_response_to_database(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating self-generated response for {ai_type}: {str(e)}")
            return {
                'ai_type': ai_type,
                'error': str(e),
                'generated_content': {}
            }
    
    def _determine_response_types(self, scenario: Dict[str, Any]) -> List[str]:
        """Determine what types of responses to generate based on scenario requirements"""
        
        response_types = ['coding', 'architecture', 'documentation']
        
        # Analyze scenario requirements
        requirements = scenario.get('requirements', [])
        for req in requirements:
            req_type = req.get('type', '').lower()
            if 'security' in req_type or 'security' in req.get('description', '').lower():
                response_types.append('security')
            if 'performance' in req_type or 'performance' in req.get('description', '').lower():
                response_types.append('performance')
            if 'testing' in req_type or 'testing' in req.get('description', '').lower():
                response_types.append('testing')
            if 'deployment' in req_type or 'deployment' in req.get('description', '').lower():
                response_types.append('deployment')
        
        return list(set(response_types))
    
    async def _generate_live_code_from_knowledge(self, scenario: Dict[str, Any], ai_knowledge: Dict[str, Any], 
                                                 current_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on AI knowledge and current technologies"""
        
        # Determine appropriate languages based on scenario
        languages = self._select_programming_languages(scenario)
        
        code_generation = {}
        
        for language in languages:
            try:
                # Generate language-specific code
                code_content = await self._generate_language_specific_code(language, scenario, ai_knowledge)
                code_generation[language] = code_content
                
            except Exception as e:
                logger.error(f"Error generating {language} code: {str(e)}")
                code_generation[language] = {'error': str(e)}
        
        return code_generation
    
    def _select_programming_languages(self, scenario: Dict[str, Any]) -> List[str]:
        """Select appropriate programming languages based on scenario requirements"""
        
        # Base languages that most AIs should know
        base_languages = ['Python', 'JavaScript']
        
        # Additional languages based on scenario complexity
        additional_languages = []
        
        complexity = scenario.get('complexity', 'x1')
        requirements = scenario.get('requirements', [])
        
        # Add languages based on requirements
        for req in requirements:
            req_desc = req.get('description', '').lower()
            
            if 'web' in req_desc or 'frontend' in req_desc:
                additional_languages.extend(['TypeScript', 'HTML', 'CSS'])
            if 'mobile' in req_desc or 'app' in req_desc:
                additional_languages.extend(['Swift', 'Kotlin'])
            if 'backend' in req_desc or 'api' in req_desc:
                additional_languages.extend(['Go', 'Rust', 'Java'])
            if 'data' in req_desc or 'analytics' in req_desc:
                additional_languages.extend(['SQL', 'R'])
            if 'system' in req_desc or 'low-level' in req_desc:
                additional_languages.extend(['C++', 'C'])
            if 'cloud' in req_desc or 'serverless' in req_desc:
                additional_languages.extend(['YAML', 'JSON'])
        
        # Add languages based on complexity
        if complexity in ['x4', 'x5', 'x6']:
            additional_languages.extend(['Rust', 'Go', 'Scala'])
        
        # Remove duplicates and limit to reasonable number
        all_languages = list(set(base_languages + additional_languages))
        return all_languages[:6]  # Limit to 6 languages max
    
    async def _generate_language_specific_code(self, language: str, scenario: Dict[str, Any], 
                                             ai_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code for a specific programming language"""
        
        # Create language-specific prompt
        prompt = self._create_language_code_prompt(language, scenario, ai_knowledge)
        
        try:
            # Use internal AI agent instead of external API
            from app.services.self_generating_ai_service import self_generating_ai_service
            code_result = await self_generating_ai_service.generate_ai_response(
                ai_type="imperium",  # Use imperium for code generation
                prompt=prompt,
                context={"task": "code_generation", "language": language}
            )
            code_response = code_result.get("response", "")
            
            # Parse and structure the response
            structured_code = self._parse_code_response(code_response, language)
            
            return {
                'language': language,
                'main_code': structured_code.get('main_code', ''),
                'dependencies': structured_code.get('dependencies', []),
                'configuration': structured_code.get('configuration', {}),
                'tests': structured_code.get('tests', ''),
                'documentation': structured_code.get('documentation', ''),
                'error_handling': structured_code.get('error_handling', ''),
                'performance_optimizations': structured_code.get('performance_optimizations', ''),
                'security_measures': structured_code.get('security_measures', '')
            }
            
        except Exception as e:
            logger.error(f"Error generating {language} code: {str(e)}")
            return {
                'language': language,
                'error': str(e)
            }
    
    def _create_language_code_prompt(self, language: str, scenario: Dict[str, Any], 
                                   ai_knowledge: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for code generation in a specific language"""
        
        requirements = scenario.get('requirements', [])
        complexity = scenario.get('complexity', 'x1')
        
        prompt = f"""
You are an expert {language} developer. Generate production-ready code for the following scenario:

SCENARIO:
{scenario.get('description', '')}

REQUIREMENTS:
"""
        
        for i, req in enumerate(requirements, 1):
            prompt += f"{i}. {req.get('description', '')}\n"
        
        prompt += f"""
COMPLEXITY LEVEL: {complexity}

LANGUAGE: {language}

Generate the following components:
1. Main implementation code
2. Dependencies and imports
3. Configuration files
4. Unit tests
5. Documentation
6. Error handling
7. Performance optimizations
8. Security measures

Requirements:
- Use {language} best practices
- Include comprehensive error handling
- Add detailed comments and documentation
- Implement proper testing
- Consider security implications
- Optimize for performance
- Make code production-ready

Format your response as JSON with the following structure:
{{
    "main_code": "// Main implementation code here",
    "dependencies": ["dependency1", "dependency2"],
    "configuration": {{"config_key": "config_value"}},
    "tests": "// Unit tests here",
    "documentation": "// Documentation here",
    "error_handling": "// Error handling code here",
    "performance_optimizations": "// Performance optimizations here",
    "security_measures": "// Security measures here"
}}
"""
        
        return prompt
    
    def _parse_code_response(self, response: str, language: str) -> Dict[str, Any]:
        """Parse the code generation response"""
        
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                parsed_json = json.loads(response)
                # Ensure all values are properly typed
                return {
                    'main_code': str(parsed_json.get('main_code', '')),
                    'dependencies': parsed_json.get('dependencies', []) if isinstance(parsed_json.get('dependencies'), list) else [],
                    'configuration': parsed_json.get('configuration', {}) if isinstance(parsed_json.get('configuration'), dict) else {},
                    'tests': str(parsed_json.get('tests', '')),
                    'documentation': str(parsed_json.get('documentation', '')),
                    'error_handling': str(parsed_json.get('error_handling', '')),
                    'performance_optimizations': str(parsed_json.get('performance_optimizations', '')),
                    'security_measures': str(parsed_json.get('security_measures', ''))
                }
        except Exception as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
        
        # Fallback parsing with proper type handling
        sections = {
            'main_code': '',
            'dependencies': [],
            'configuration': {},
            'tests': '',
            'documentation': '',
            'error_handling': '',
            'performance_optimizations': '',
            'security_measures': ''
        }
        
        # Simple parsing based on common patterns
        lines = response.split('\n')
        current_section = 'main_code'
        
        for line in lines:
            if 'dependencies' in line.lower() or 'import' in line.lower():
                current_section = 'dependencies'
            elif 'test' in line.lower():
                current_section = 'tests'
            elif 'documentation' in line.lower() or 'comment' in line.lower():
                current_section = 'documentation'
            elif 'error' in line.lower():
                current_section = 'error_handling'
            elif 'performance' in line.lower() or 'optimization' in line.lower():
                current_section = 'performance_optimizations'
            elif 'security' in line.lower():
                current_section = 'security_measures'
            elif 'config' in line.lower():
                current_section = 'configuration'
            
            # Ensure proper type handling for each section
            if current_section == 'main_code':
                sections['main_code'] += line + '\n'
            elif current_section == 'dependencies':
                if line.strip() and not line.startswith('#'):
                    sections['dependencies'].append(line.strip())
            elif current_section == 'configuration':
                # Handle configuration as dict
                if ':' in line and line.strip():
                    key, value = line.split(':', 1)
                    sections['configuration'][key.strip()] = value.strip()
            else:
                # Handle string sections properly
                if isinstance(sections[current_section], str):
                    sections[current_section] += line + '\n'
        
        return sections
    
    async def _generate_live_architecture_from_knowledge(self, scenario: Dict[str, Any], ai_knowledge: Dict[str, Any], 
                                                         current_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Generate architecture based on AI strengths and current trends"""
        
        prompt = f"""
You are an expert software architect. Design a comprehensive architecture for the following scenario:

SCENARIO:
{scenario.get('description', '')}

REQUIREMENTS:
"""
        
        for i, req in enumerate(scenario.get('requirements', []), 1):
            prompt += f"{i}. {req.get('description', '')}\n"
        
        prompt += f"""
COMPLEXITY: {scenario.get('complexity', 'x1')}

Design a comprehensive architecture including:
1. System overview and high-level design
2. Component diagram and relationships
3. Data flow and API design
4. Database schema and data models
5. Security architecture
6. Scalability and performance considerations
7. Deployment architecture
8. Technology stack recommendations
9. Monitoring and logging strategy
10. Disaster recovery and backup strategy

Format your response as JSON:
{{
    "system_overview": "High-level system description",
    "components": [
        {{"name": "component_name", "description": "component_description", "responsibilities": ["resp1", "resp2"]}}
    ],
    "data_flow": "Data flow description",
    "api_design": "API design details",
    "database_schema": "Database schema description",
    "security_architecture": "Security design details",
    "scalability": "Scalability considerations",
    "deployment": "Deployment architecture",
    "technology_stack": ["tech1", "tech2"],
    "monitoring": "Monitoring strategy",
    "disaster_recovery": "Disaster recovery plan"
}}
"""
        
        try:
            # Use internal AI agent instead of external API
            from app.services.self_generating_ai_service import self_generating_ai_service
            architecture_result = await self_generating_ai_service.generate_ai_response(
                ai_type="imperium",  # Use imperium for architecture design
                prompt=prompt,
                context={"task": "architecture_design"}
            )
            architecture_response = architecture_result.get("response", "")
            
            # Parse architecture response
            return self._parse_architecture_response(architecture_response)
            
        except Exception as e:
            logger.error(f"Error generating architecture: {str(e)}")
            return {'error': str(e)}
    
    def _parse_architecture_response(self, response: str) -> Dict[str, Any]:
        """Parse architecture generation response"""
        
        try:
            if response.strip().startswith('{'):
                parsed_json = json.loads(response)
                # Ensure all values are properly typed
                return {
                    'system_overview': str(parsed_json.get('system_overview', '')),
                    'components': parsed_json.get('components', []) if isinstance(parsed_json.get('components'), list) else [],
                    'data_flow': str(parsed_json.get('data_flow', '')),
                    'api_design': str(parsed_json.get('api_design', '')),
                    'database_schema': str(parsed_json.get('database_schema', '')),
                    'security_architecture': str(parsed_json.get('security_architecture', '')),
                    'scalability': str(parsed_json.get('scalability', '')),
                    'deployment': str(parsed_json.get('deployment', '')),
                    'technology_stack': parsed_json.get('technology_stack', []) if isinstance(parsed_json.get('technology_stack'), list) else [],
                    'monitoring': str(parsed_json.get('monitoring', '')),
                    'disaster_recovery': str(parsed_json.get('disaster_recovery', ''))
                }
        except Exception as e:
            logger.error(f"Error parsing architecture JSON response: {str(e)}")
        
        # Fallback parsing
        return {
            'system_overview': response[:500],
            'components': [],
            'data_flow': '',
            'api_design': '',
            'database_schema': '',
            'security_architecture': '',
            'scalability': '',
            'deployment': '',
            'technology_stack': [],
            'monitoring': '',
            'disaster_recovery': ''
        }
    
    async def _generate_live_documentation_from_knowledge(self, scenario: Dict[str, Any], ai_knowledge: Dict[str, Any], 
                                                          current_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation based on AI learning history"""
        
        prompt = f"""
Create comprehensive documentation for the following system:

SCENARIO: {scenario.get('description', '')}
COMPLEXITY: {scenario.get('complexity', 'x1')}

Generate documentation including:
1. README with setup instructions
2. API documentation
3. Architecture documentation
4. Deployment guide
5. Troubleshooting guide
6. Contributing guidelines
7. Security considerations
8. Performance guidelines

Format as JSON:
{{
    "readme": "README content",
    "api_docs": "API documentation",
    "architecture_docs": "Architecture documentation",
    "deployment_guide": "Deployment instructions",
    "troubleshooting": "Troubleshooting guide",
    "contributing": "Contributing guidelines",
    "security": "Security considerations",
    "performance": "Performance guidelines"
}}
"""
        
        try:
            # Use internal AI agent instead of external API
            from app.services.self_generating_ai_service import self_generating_ai_service
            doc_result = await self_generating_ai_service.generate_ai_response(
                ai_type="imperium",  # Use imperium for documentation
                prompt=prompt,
                context={"task": "documentation_generation"}
            )
            doc_response = doc_result.get("response", "")
            
            return self._parse_documentation_response(doc_response)
            
        except Exception as e:
            logger.error(f"Error generating documentation: {str(e)}")
            return {'error': str(e)}
    
    def _parse_documentation_response(self, response: str) -> Dict[str, Any]:
        """Parse documentation response"""
        
        try:
            if response.strip().startswith('{'):
                parsed_json = json.loads(response)
                # Ensure all values are properly typed
                return {
                    'readme': str(parsed_json.get('readme', '')),
                    'api_docs': str(parsed_json.get('api_docs', '')),
                    'architecture_docs': str(parsed_json.get('architecture_docs', '')),
                    'deployment_guide': str(parsed_json.get('deployment_guide', '')),
                    'troubleshooting': str(parsed_json.get('troubleshooting', '')),
                    'contributing': str(parsed_json.get('contributing', '')),
                    'security': str(parsed_json.get('security', '')),
                    'performance': str(parsed_json.get('performance', ''))
                }
        except Exception as e:
            logger.error(f"Error parsing documentation JSON response: {str(e)}")
        
        return {
            'readme': response[:300],
            'api_docs': '',
            'architecture_docs': '',
            'deployment_guide': '',
            'troubleshooting': '',
            'contributing': '',
            'security': '',
            'performance': ''
        }
    
    async def _generate_live_testing_from_knowledge(self, scenario: Dict[str, Any], ai_knowledge: Dict[str, Any], 
                                                    current_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Generate testing strategy based on AI experience"""
        
        prompt = f"""
Create a comprehensive testing strategy for the following system:

SCENARIO: {scenario.get('description', '')}
COMPLEXITY: {scenario.get('complexity', 'x1')}

Generate testing strategy including:
1. Unit testing approach
2. Integration testing strategy
3. End-to-end testing
4. Performance testing
5. Security testing
6. Test automation strategy
7. Test data management
8. Continuous testing integration

Format as JSON:
{{
    "unit_testing": "Unit testing strategy",
    "integration_testing": "Integration testing approach",
    "e2e_testing": "End-to-end testing strategy",
    "performance_testing": "Performance testing approach",
    "security_testing": "Security testing strategy",
    "automation": "Test automation strategy",
    "test_data": "Test data management",
    "ci_cd": "Continuous testing integration"
}}
"""
        
        try:
            # Use internal AI agent instead of external API
            from app.services.self_generating_ai_service import self_generating_ai_service
            test_result = await self_generating_ai_service.generate_ai_response(
                ai_type="imperium",  # Use imperium for testing strategy
                prompt=prompt,
                context={"task": "testing_strategy"}
            )
            test_response = test_result.get("response", "")
            
            return self._parse_testing_response(test_response)
            
        except Exception as e:
            logger.error(f"Error generating testing strategy: {str(e)}")
            return {'error': str(e)}
    
    def _parse_testing_response(self, response: str) -> Dict[str, Any]:
        """Parse testing strategy response"""
        
        try:
            if response.strip().startswith('{'):
                return json.loads(response)
        except:
            pass
        
        return {
            'unit_testing': response[:200],
            'integration_testing': '',
            'e2e_testing': '',
            'performance_testing': '',
            'security_testing': '',
            'automation': '',
            'test_data': '',
            'ci_cd': ''
        }
    
    async def _generate_live_deployment_from_knowledge(self, scenario: Dict[str, Any], ai_knowledge: Dict[str, Any], 
                                                        current_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deployment strategy based on current best practices"""
        
        prompt = f"""
Create a deployment strategy for the following system:

SCENARIO: {scenario.get('description', '')}
COMPLEXITY: {scenario.get('complexity', 'x1')}

Generate deployment strategy including:
1. Environment setup
2. Containerization strategy
3. CI/CD pipeline
4. Infrastructure as Code
5. Monitoring and logging
6. Rollback strategy
7. Blue-green deployment
8. Disaster recovery

Format as JSON:
{{
    "environment": "Environment setup",
    "containerization": "Containerization strategy",
    "ci_cd": "CI/CD pipeline",
    "infrastructure": "Infrastructure as Code",
    "monitoring": "Monitoring and logging",
    "rollback": "Rollback strategy",
    "blue_green": "Blue-green deployment",
    "disaster_recovery": "Disaster recovery"
}}
"""
        
        try:
            # Use internal AI agent instead of external API
            from app.services.self_generating_ai_service import self_generating_ai_service
            deploy_result = await self_generating_ai_service.generate_ai_response(
                ai_type="imperium",  # Use imperium for deployment strategy
                prompt=prompt,
                context={"task": "deployment_strategy"}
            )
            deploy_response = deploy_result.get("response", "")
            
            return self._parse_deployment_response(deploy_response)
            
        except Exception as e:
            logger.error(f"Error generating deployment strategy: {str(e)}")
            return {'error': str(e)}
    
    def _parse_deployment_response(self, response: str) -> Dict[str, Any]:
        """Parse deployment strategy response"""
        
        try:
            if response.strip().startswith('{'):
                return json.loads(response)
        except:
            pass
        
        return {
            'environment': response[:200],
            'containerization': '',
            'ci_cd': '',
            'infrastructure': '',
            'monitoring': '',
            'rollback': '',
            'blue_green': '',
            'disaster_recovery': ''
        }
    
    async def _generate_live_security_from_knowledge(self, scenario: Dict[str, Any], ai_knowledge: Dict[str, Any], 
                                                      current_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Generate security measures based on AI security knowledge"""
        
        prompt = f"""
Create comprehensive security measures for the following system:

SCENARIO: {scenario.get('description', '')}
COMPLEXITY: {scenario.get('complexity', 'x1')}

Generate security measures including:
1. Authentication and authorization
2. Data encryption
3. Input validation
4. SQL injection prevention
5. XSS protection
6. CSRF protection
7. Rate limiting
8. Security headers
9. Vulnerability scanning
10. Security monitoring

Format as JSON:
{{
    "authentication": "Authentication strategy",
    "encryption": "Data encryption approach",
    "input_validation": "Input validation strategy",
    "sql_injection": "SQL injection prevention",
    "xss_protection": "XSS protection",
    "csrf_protection": "CSRF protection",
    "rate_limiting": "Rate limiting strategy",
    "security_headers": "Security headers",
    "vulnerability_scanning": "Vulnerability scanning",
    "security_monitoring": "Security monitoring"
}}
"""
        
        try:
            # Use internal AI agent instead of external API
            from app.services.self_generating_ai_service import self_generating_ai_service
            security_result = await self_generating_ai_service.generate_ai_response(
                ai_type="guardian",  # Use guardian for security measures
                prompt=prompt,
                context={"task": "security_measures"}
            )
            security_response = security_result.get("response", "")
            
            return self._parse_security_response(security_response)
            
        except Exception as e:
            logger.error(f"Error generating security measures: {str(e)}")
            return {'error': str(e)}
    
    def _parse_security_response(self, response: str) -> Dict[str, Any]:
        """Parse security measures response"""
        
        try:
            if response.strip().startswith('{'):
                return json.loads(response)
        except:
            pass
        
        return {
            'authentication': response[:200],
            'encryption': '',
            'input_validation': '',
            'sql_injection': '',
            'xss_protection': '',
            'csrf_protection': '',
            'rate_limiting': '',
            'security_headers': '',
            'vulnerability_scanning': '',
            'security_monitoring': ''
        }
    
    async def _generate_live_performance_from_knowledge(self, scenario: Dict[str, Any], ai_knowledge: Dict[str, Any], 
                                                         current_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance optimization based on AI experience"""
        
        prompt = f"""
Create performance optimization strategy for the following system:

SCENARIO: {scenario.get('description', '')}
COMPLEXITY: {scenario.get('complexity', 'x1')}

Generate performance optimization including:
1. Caching strategy
2. Database optimization
3. Code optimization
4. Load balancing
5. CDN implementation
6. Resource optimization
7. Monitoring and metrics
8. Performance testing

Format as JSON:
{{
    "caching": "Caching strategy",
    "database_optimization": "Database optimization",
    "code_optimization": "Code optimization",
    "load_balancing": "Load balancing strategy",
    "cdn": "CDN implementation",
    "resource_optimization": "Resource optimization",
    "monitoring": "Performance monitoring",
    "performance_testing": "Performance testing"
}}
"""
        
        try:
            # Use internal AI agent instead of external API
            from app.services.self_generating_ai_service import self_generating_ai_service
            perf_result = await self_generating_ai_service.generate_ai_response(
                ai_type="imperium",  # Use imperium for performance optimization
                prompt=prompt,
                context={"task": "performance_optimization"}
            )
            perf_response = perf_result.get("response", "")
            
            return self._parse_performance_response(perf_response)
            
        except Exception as e:
            logger.error(f"Error generating performance optimization: {str(e)}")
            return {'error': str(e)}
    
    def _parse_performance_response(self, response: str) -> Dict[str, Any]:
        """Parse performance optimization response"""
        
        try:
            if response.strip().startswith('{'):
                return json.loads(response)
        except:
            pass
        
        return {
            'caching': response[:200],
            'database_optimization': '',
            'code_optimization': '',
            'load_balancing': '',
            'cdn': '',
            'resource_optimization': '',
            'monitoring': '',
            'performance_testing': ''
        }
    
    async def _persist_ai_response_to_database(self, response: Dict[str, Any]):
        """Persist AI self-generated response to database"""
        
        try:
            async with get_session() as session:
                # Create AIResponse record
                ai_response = AIResponse(
                    id=str(uuid.uuid4()),
                    ai_type=response['ai_type'],
                    scenario_id=response.get('scenario_id'),
                    response_types=json.dumps(response.get('response_types', [])),
                    generated_content=json.dumps(response.get('generated_content', {})),
                    languages_used=json.dumps(response.get('languages_used', [])),
                    architecture_components=json.dumps(response.get('architecture_components', [])),
                    code_snippets=json.dumps(response.get('code_snippets', [])),
                    documentation=response.get('documentation', ''),
                    testing_approach=response.get('testing_approach', ''),
                    performance_considerations=response.get('performance_considerations', ''),
                    security_measures=response.get('security_measures', ''),
                    deployment_strategy=response.get('deployment_strategy', ''),
                    created_at=datetime.fromisoformat(response['created_at'])
                )
                
                session.add(ai_response)
                await session.commit()
                
                logger.info(f"✅ AI response for {response['ai_type']} persisted to database")
                
        except Exception as e:
            logger.error(f"❌ Failed to persist AI response: {str(e)}")
    
    async def _get_ai_level(self, ai_type: str) -> int:
        """Get AI level from database"""
        
        try:
            async with get_session() as session:
                query = text("""
                    SELECT level FROM agent_metrics 
                    WHERE agent_type = :ai_type
                """)
                
                result = await session.execute(query, {'ai_type': ai_type})
                row = result.fetchone()
                
                return row.level if row else 1
                
        except Exception as e:
            logger.error(f"Error getting AI level: {str(e)}")
            return 1
    
    async def _calculate_collaborative_score(self, ai_contributions: Dict[str, Any], scenario: str) -> float:
        """Calculate collaborative score based on AI contributions"""
        
        try:
            if not ai_contributions:
                return 0.0
            
            total_score = 0.0
            valid_contributions = 0
            
            for ai_type, contribution in ai_contributions.items():
                if isinstance(contribution, dict) and 'error' not in contribution:
                    # Calculate individual contribution score
                    score = self._evaluate_contribution_quality(contribution, scenario)
                    total_score += score
                    valid_contributions += 1
                elif isinstance(contribution, str):
                    # Simple text contribution
                    score = self._evaluate_text_contribution(contribution, scenario)
                    total_score += score
                    valid_contributions += 1
            
            if valid_contributions == 0:
                return 0.0
            
            # Calculate collaborative bonus
            collaboration_bonus = self._calculate_collaboration_bonus(ai_contributions)
            
            avg_score = total_score / valid_contributions
            final_score = min(100.0, avg_score + collaboration_bonus)
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating collaborative score: {str(e)}")
            return 0.0
    
    def _evaluate_contribution_quality(self, contribution: Dict[str, Any], scenario: str) -> float:
        """Evaluate the quality of an AI contribution"""
        
        try:
            score = 0.0
            
            # Check for generated content
            generated_content = contribution.get('generated_content', {})
            
            # Code quality
            if 'code' in generated_content:
                code_quality = len(generated_content['code']) * 10
                score += min(30, code_quality)
            
            # Architecture quality
            if 'architecture' in generated_content:
                arch_quality = len(generated_content['architecture'].get('components', [])) * 5
                score += min(25, arch_quality)
            
            # Documentation quality
            if 'documentation' in generated_content:
                doc_quality = len(generated_content['documentation']) / 100
                score += min(20, doc_quality)
            
            # Testing strategy
            if 'testing' in generated_content:
                test_quality = len(generated_content['testing'].get('strategies', [])) * 3
                score += min(15, test_quality)
            
            # Security measures
            if 'security' in generated_content:
                sec_quality = len(generated_content['security'].get('measures', [])) * 2
                score += min(10, sec_quality)
            
            return min(100.0, score)
            
        except Exception as e:
            logger.error(f"Error evaluating contribution quality: {str(e)}")
            return 50.0
    
    def _evaluate_text_contribution(self, contribution: str, scenario: str) -> float:
        """Evaluate simple text contribution"""
        
        try:
            # Basic scoring based on content length and relevance
            content_length = len(contribution)
            relevance_score = 50.0  # Base score
            
            # Length bonus
            if content_length > 500:
                relevance_score += 20
            elif content_length > 200:
                relevance_score += 10
            
            # Check for technical keywords
            technical_keywords = ['api', 'database', 'security', 'performance', 'testing', 'deployment']
            keyword_count = sum(1 for keyword in technical_keywords if keyword.lower() in contribution.lower())
            relevance_score += keyword_count * 5
            
            return min(100.0, relevance_score)
            
        except Exception as e:
            logger.error(f"Error evaluating text contribution: {str(e)}")
            return 50.0
    
    def _calculate_collaboration_bonus(self, ai_contributions: Dict[str, Any]) -> float:
        """Calculate bonus for good collaboration"""
        
        try:
            if len(ai_contributions) < 2:
                return 0.0
            
            # Check for complementary contributions
            has_code = any('code' in str(contrib) for contrib in ai_contributions.values())
            has_architecture = any('architecture' in str(contrib) for contrib in ai_contributions.values())
            has_documentation = any('documentation' in str(contrib) for contrib in ai_contributions.values())
            
            bonus = 0.0
            if has_code and has_architecture:
                bonus += 10.0
            if has_code and has_documentation:
                bonus += 5.0
            if has_architecture and has_documentation:
                bonus += 5.0
            
            return bonus
            
        except Exception as e:
            logger.error(f"Error calculating collaboration bonus: {str(e)}")
            return 0.0
    
    async def _check_claude_tokens_available(self) -> bool:
        """Check if Claude tokens are available for LLM calls"""
        try:
            # Use internal AI agent instead of external API
            from app.services.self_generating_ai_service import self_generating_ai_service
            test_result = await self_generating_ai_service.generate_ai_response(
                ai_type="imperium",
                prompt="Test",
                context={"task": "token_check"}
            )
            return True
        except Exception as e:
            logger.warning(f"⚠️ Claude tokens not available: {str(e)}")
            return False
    
    async def _generate_with_claude(self, ai_types: List[str], difficulty: str, 
                                   test_type: str, ai_levels: Dict[str, int]) -> Dict[str, Any]:
        """Generate scenario using Claude when tokens are available"""
        
        # Determine complexity based on AI levels
        avg_level = sum(ai_levels.values()) / len(ai_levels)
        complexity = self._get_complexity_for_level(avg_level)
        
        # Get internet knowledge for current trends
        current_knowledge = await self._get_current_knowledge()
        
        # Generate varied requirements
        requirements = await self._generate_varied_requirements(test_type, complexity, current_knowledge)
        
        # Create dynamic scenario
        scenario = await self._create_dynamic_scenario(requirements, ai_types, complexity)
        
        # Add Docker integration if available
        if self.docker_client:
            scenario['docker_config'] = await self._generate_docker_config(scenario)
        
        # Store in Neon database
        await self._persist_scenario_to_database(scenario)
        
        return scenario
    
    async def _generate_with_fallback(self, ai_types: List[str], difficulty: str, 
                                     test_type: str, ai_levels: Dict[str, int]) -> Dict[str, Any]:
        """Generate scenario using self-generating system without LLM calls"""
        
        # Determine complexity based on AI levels
        avg_level = sum(ai_levels.values()) / len(ai_levels)
        complexity = self._get_complexity_for_level(avg_level)
        
        # Get AI knowledge from database for each participant
        ai_knowledge = {}
        for ai_type in ai_types:
            ai_knowledge[ai_type] = await self.get_ai_knowledge_from_database(ai_type)
        
        # Get internet knowledge for current trends
        current_knowledge = await self._get_current_knowledge()
        
        # Generate requirements based on AI knowledge and internet data
        requirements = await self._generate_self_generated_requirements(
            test_type, complexity, current_knowledge, ai_knowledge
        )
        
        # Create scenario using self-generated content
        scenario = await self._create_self_generated_scenario(requirements, ai_types, complexity, ai_knowledge)
        
        # Add Docker integration if available
        if self.docker_client:
            scenario['docker_config'] = await self._generate_docker_config(scenario)
        
        # Store in Neon database
        await self._persist_scenario_to_database(scenario)
        
        return scenario
    
    async def _generate_self_generated_requirements(self, test_type: str, complexity: TestComplexity,
                                                   knowledge: Dict[str, Any], ai_knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate requirements using self-generating system without LLM"""
        
        requirements = []
        
        # Get technologies and challenges from internet knowledge
        technologies = knowledge.get('technologies', ['Python', 'JavaScript', 'Docker', 'PostgreSQL', 'Redis'])
        challenges = knowledge.get('challenges', ['scalability', 'security', 'performance', 'reliability'])
        
        # Get AI strengths and weaknesses
        all_strengths = []
        all_weaknesses = []
        for ai_type, knowledge_data in ai_knowledge.items():
            all_strengths.extend(knowledge_data.get('strengths', []))
            all_weaknesses.extend(knowledge_data.get('weaknesses', []))
        
        # Remove duplicates
        all_strengths = list(set(all_strengths))
        all_weaknesses = list(set(all_weaknesses))
        
        # Generate requirements based on AI knowledge patterns
        requirement_types = [
            TestRequirement.CODING,
            TestRequirement.ARCHITECTURE,
            TestRequirement.SECURITY,
            TestRequirement.PERFORMANCE,
            TestRequirement.INTEGRATION
        ]
        
        # Create strength-based requirements
        for strength in all_strengths[:2]:  # Use top 2 strengths
            requirement = await self._create_strength_challenge(strength, complexity)
            requirements.append(requirement)
        
        # Create weakness-based requirements
        for weakness in all_weaknesses[:2]:  # Use top 2 weaknesses
            requirement = await self._create_weakness_improvement(weakness, complexity)
            requirements.append(requirement)
        
        # Create technology-based requirements
        for tech in random.sample(technologies, min(2, len(technologies))):
            requirement = await self._create_technology_requirement(tech, complexity)
            requirements.append(requirement)
        
        return requirements[:5]  # Limit to 5 requirements
    
    async def _create_technology_requirement(self, technology: str, complexity: TestComplexity) -> Dict[str, Any]:
        """Create a requirement based on a specific technology"""
        
        tech_requirements = {
            'Python': 'Implement a Python service with async/await patterns and comprehensive error handling',
            'JavaScript': 'Create a JavaScript application with modern ES6+ features and proper module structure',
            'Docker': 'Containerize the application with multi-stage builds and security best practices',
            'PostgreSQL': 'Design a PostgreSQL database schema with proper indexing and data integrity',
            'Redis': 'Implement Redis caching with proper key management and expiration strategies',
            'React': 'Build a React application with hooks, context, and proper state management',
            'Node.js': 'Create a Node.js API with Express, middleware, and proper error handling',
            'TypeScript': 'Develop a TypeScript application with strict typing and interface definitions'
        }
        
        description = tech_requirements.get(technology, f'Implement a solution using {technology} with best practices')
        
        return {
            'type': 'technology_integration',
            'description': description,
            'complexity': complexity.value,
            'technology': technology
        }
    
    async def _create_self_generated_scenario(self, requirements: List[Dict[str, Any]], 
                                             ai_types: List[str], complexity: TestComplexity,
                                             ai_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Create a scenario using self-generated content without LLM calls"""
        
        # Generate description based on requirements and AI knowledge
        description = await self._generate_self_generated_description(requirements, ai_types, complexity, ai_knowledge)
        
        # Generate success criteria based on requirements
        success_criteria = await self._generate_self_generated_success_criteria(requirements, complexity)
        
        scenario = {
            'id': str(uuid.uuid4()),
            'type': 'self_generated_test',
            'complexity': complexity.value,
            'participants': ai_types,
            'requirements': requirements,
            'description': description,
            'success_criteria': success_criteria,
            'time_limit': self._get_time_limit(complexity),
            'created_at': datetime.utcnow().isoformat(),
            'self_generated': True,
            'ai_knowledge_used': list(ai_knowledge.keys())
        }
        
        return scenario
    
    async def _generate_self_generated_description(self, requirements: List[Dict[str, Any]], 
                                                  ai_types: List[str], complexity: TestComplexity,
                                                  ai_knowledge: Dict[str, Any]) -> str:
        """Generate scenario description without LLM calls"""
        
        description_parts = [
            f"You are working with {len(ai_types)} AI systems: {', '.join(ai_types)}.",
            f"This is a {complexity.value} complexity test that requires collaboration.",
            "Your task is to:"
        ]
        
        for i, req in enumerate(requirements, 1):
            description_parts.append(f"{i}. {req['description']}")
        
        description_parts.extend([
            "You must work together to create a comprehensive solution.",
            "Each AI should contribute their expertise to different aspects of the solution.",
            "The final solution should be production-ready and well-documented."
        ])
        
        return "\n".join(description_parts)
    
    async def _generate_self_generated_success_criteria(self, requirements: List[Dict[str, Any]], 
                                                       complexity: TestComplexity) -> List[str]:
        """Generate success criteria without LLM calls"""
        
        criteria = []
        
        for req in requirements:
            req_type = req.get('type', '').lower()
            
            if 'coding' in req_type or 'code' in req.get('description', '').lower():
                criteria.extend([
                    "Code is well-structured and follows best practices",
                    "Code includes comprehensive error handling",
                    "Code is properly documented with comments",
                    "Code passes all unit tests"
                ])
            elif 'architecture' in req_type or 'design' in req.get('description', '').lower():
                criteria.extend([
                    "Architecture is scalable and maintainable",
                    "Components are properly decoupled",
                    "System follows design patterns",
                    "Architecture supports the required functionality"
                ])
            elif 'security' in req_type or 'security' in req.get('description', '').lower():
                criteria.extend([
                    "Security measures are properly implemented",
                    "No security vulnerabilities are present",
                    "Authentication and authorization are secure",
                    "Data is encrypted where necessary"
                ])
            elif 'performance' in req_type or 'performance' in req.get('description', '').lower():
                criteria.extend([
                    "Performance meets the specified requirements",
                    "System handles expected load efficiently",
                    "Response times are within acceptable limits",
                    "Resource usage is optimized"
                ])
            elif 'integration' in req_type or 'integration' in req.get('description', '').lower():
                criteria.extend([
                    "Integration points are properly connected",
                    "APIs are well-designed and documented",
                    "Data flows correctly between systems",
                    "Error handling for integration points is robust"
                ])
        
        # Add complexity-based criteria
        if complexity.value in ['x4', 'x5', 'x6']:
            criteria.extend([
                "Solution includes comprehensive testing",
                "Documentation is complete and professional",
                "Code is production-ready",
                "Performance benchmarks are met"
            ])
        
        return criteria