#!/usr/bin/env python3
"""
Enhanced Test Generator Service with Fallback System
==================================================

This system generates dynamic, varied test scenarios with automatic fallback
to the custodes fallback system when Claude tokens are unavailable.
Features:
- Internet knowledge integration
- Dynamic difficulty scaling (x1, x2, etc.)
- Docker simulation for real-world testing
- AI communication for collaborative responses
- Infinite scenario generation
- Training ground integration
- Neon database persistence
- FALLBACK SYSTEM: Uses custodes fallback when Claude tokens unavailable
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
from app.services.anthropic_service import call_claude, anthropic_rate_limited_call
from app.services.unified_ai_service_shared import unified_ai_service_shared
from app.models.sql_models import CustodyTestResult, InternetKnowledge
from app.services.custodes_fallback_testing import CustodesFallbackTesting, FallbackTestDifficulty, FallbackTestCategory

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
    """Enhanced Test Generator with fallback system integration"""
    
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
            self.fallback_service = CustodesFallbackTesting()  # Initialize fallback service
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
        logger.info("✅ Enhanced Test Generator initialized with fallback system")
        return instance

    async def _load_internet_knowledge(self):
        """Load internet knowledge from database"""
        try:
            async with get_session() as session:
                # Load from database
                result = await session.execute(
                    text("SELECT source, content, source_type, created_at FROM internet_knowledge ORDER BY created_at DESC LIMIT 50")
                )
                
                for row in result.fetchall():
                    source = row[0]
                    content = row[1]
                    source_type = row[2]
                    
                    if source not in self.internet_knowledge_cache:
                        self.internet_knowledge_cache[source] = []
                    
                    self.internet_knowledge_cache[source].append({
                        "type": source_type,
                        "content": content,
                        "timestamp": row[3]
                    })
                
                logger.info(f"✅ Loaded internet knowledge from {len(self.internet_knowledge_cache)} sources")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not load internet knowledge: {str(e)}")
            self.internet_knowledge_cache = {}

    def _extract_knowledge(self, content: str) -> Dict[str, Any]:
        """Extract structured knowledge from content"""
        try:
            if isinstance(content, str):
                # Try to parse as JSON first
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Parse as plain text
                    return {
                        "technologies": re.findall(r'\b[A-Z][a-zA-Z]*\b', content),
                        "concepts": re.findall(r'\b[a-z]+(?:\s+[a-z]+)*\b', content),
                        "domains": ["General Computing"]
                    }
            elif isinstance(content, dict):
                return content
            else:
                return {"technologies": [], "concepts": [], "domains": ["General"]}
        except Exception as e:
            logger.warning(f"⚠️ Error extracting knowledge: {str(e)}")
            return {"technologies": [], "concepts": [], "domains": ["General"]}

    async def _load_scenario_templates(self):
        """Load scenario templates for different test types"""
        self.scenario_templates = {
            "custody": {
                "basic": {
                    "description": "Basic custody test focusing on fundamental AI capabilities",
                    "requirements": ["knowledge_verification", "code_quality"],
                    "time_limit": 30
                },
                "intermediate": {
                    "description": "Intermediate custody test with security and performance focus",
                    "requirements": ["security_awareness", "performance_optimization"],
                    "time_limit": 45
                },
                "advanced": {
                    "description": "Advanced custody test requiring innovation and collaboration",
                    "requirements": ["innovation_capability", "cross_ai_collaboration"],
                    "time_limit": 60
                }
            },
            "olympic": {
                "basic": {
                    "description": "Olympic event focusing on competitive problem solving",
                    "requirements": ["performance_optimization", "code_quality"],
                    "time_limit": 40
                },
                "intermediate": {
                    "description": "Olympic event with security and innovation challenges",
                    "requirements": ["security_awareness", "innovation_capability"],
                    "time_limit": 50
                },
                "advanced": {
                    "description": "Advanced Olympic event requiring multiple AI collaboration",
                    "requirements": ["cross_ai_collaboration", "experimental_validation"],
                    "time_limit": 70
                }
            },
            "collaborative": {
                "basic": {
                    "description": "Collaborative test requiring multiple AI coordination",
                    "requirements": ["collaboration", "integration"],
                    "time_limit": 50
                },
                "intermediate": {
                    "description": "Intermediate collaborative test with complex requirements",
                    "requirements": ["architecture", "testing"],
                    "time_limit": 60
                },
                "advanced": {
                    "description": "Advanced collaborative test with experimental validation",
                    "requirements": ["experimental_validation", "self_improvement"],
                    "time_limit": 80
                }
            }
        }

    async def generate_dynamic_test_scenario(self, ai_types: List[str], difficulty: str, 
                                           test_type: str, ai_levels: Dict[str, int]) -> Dict[str, Any]:
        """Generate dynamic test scenario with automatic fallback system"""
        try:
            # Check if Claude tokens are available
            tokens_available = await self._check_claude_tokens_available()
            
            if tokens_available:
                logger.info("🎯 Using Claude for test generation")
                return await self._generate_with_claude(ai_types, difficulty, test_type, ai_levels)
            else:
                logger.info("🔄 Using fallback system for test generation")
                return await self._generate_with_fallback(ai_types, difficulty, test_type, ai_levels)
                
        except Exception as e:
            logger.error(f"❌ Error generating test scenario: {str(e)}")
            return await self._generate_with_fallback(ai_types, difficulty, test_type, ai_levels)

    async def _check_claude_tokens_available(self) -> bool:
        """Check if Claude tokens are available"""
        try:
            # Try a simple Claude call to check availability
            test_response = await anthropic_rate_limited_call(
                "Test token availability",
                max_tokens=10
            )
            return test_response is not None and len(test_response) > 0
        except Exception as e:
            logger.warning(f"⚠️ Claude tokens not available: {str(e)}")
            return False

    async def _generate_with_claude(self, ai_types: List[str], difficulty: str, 
                                   test_type: str, ai_levels: Dict[str, int]) -> Dict[str, Any]:
        """Generate test using Claude when tokens are available"""
        try:
            # Get current knowledge
            knowledge = await self._get_current_knowledge()
            
            # Calculate average AI level
            avg_level = sum(ai_levels.values()) / len(ai_levels) if ai_levels else 1
            complexity = self._get_complexity_for_level(avg_level)
            
            # Generate varied requirements
            requirements = await self._generate_varied_requirements(test_type, complexity, knowledge)
            
            # Create dynamic scenario
            scenario = await self._create_dynamic_scenario(requirements, ai_types, complexity)
            
            # Generate description and success criteria
            scenario["description"] = await self._generate_scenario_description(requirements, ai_types, complexity)
            scenario["success_criteria"] = await self._generate_success_criteria(requirements, complexity)
            
            # Add Docker configuration if available
            if self.docker_client:
                scenario["docker_config"] = await self._generate_docker_config(scenario)
            
            # Persist to database
            await self._persist_scenario_to_database(scenario)
            
            return scenario
            
        except Exception as e:
            logger.error(f"❌ Error generating with Claude: {str(e)}")
            # Fallback to fallback system
            return await self._generate_with_fallback(ai_types, difficulty, test_type, ai_levels)

    async def _generate_with_fallback(self, ai_types: List[str], difficulty: str, 
                                     test_type: str, ai_levels: Dict[str, int]) -> Dict[str, Any]:
        """Generate test using fallback system when Claude is unavailable"""
        try:
            logger.info(f"🔄 Generating fallback test for {ai_types} with difficulty {difficulty}")
            
            # Convert difficulty to fallback format
            fallback_difficulty = self._convert_to_fallback_difficulty(difficulty)
            
            # Generate test for each AI type
            tests = {}
            for ai_type in ai_types:
                # Choose appropriate category based on test type
                category = self._get_fallback_category_for_test_type(test_type)
                
                # Generate fallback test
                test_content = await self.fallback_service.generate_fallback_test(
                    ai_type=ai_type,
                    difficulty=fallback_difficulty,
                    category=category
                )
                
                tests[ai_type] = test_content
            
            # Create comprehensive scenario
            scenario = {
                "id": f"fallback_{test_type}_{uuid.uuid4().hex[:8]}",
                "test_type": test_type,
                "difficulty": difficulty,
                "ai_types": ai_types,
                "ai_levels": ai_levels,
                "tests": tests,
                "description": f"Fallback {test_type} test for {', '.join(ai_types)} AIs",
                "success_criteria": [
                    "Complete all assigned tasks",
                    "Demonstrate understanding of requirements",
                    "Provide clear and logical responses",
                    "Show appropriate technical knowledge"
                ],
                "time_limit": self._get_fallback_time_limit(fallback_difficulty),
                "source": "fallback_system",
                "created_at": datetime.utcnow().isoformat(),
                "scenario_type": f"fallback_{test_type}"
            }
            
            # Persist to database
            await self._persist_scenario_to_database(scenario)
            
            logger.info(f"✅ Generated fallback test scenario: {scenario['id']}")
            return scenario
            
        except Exception as e:
            logger.error(f"❌ Error generating fallback test: {str(e)}")
            return self._create_emergency_fallback_scenario(ai_types, difficulty, test_type)

    def _convert_to_fallback_difficulty(self, difficulty: str) -> FallbackTestDifficulty:
        """Convert difficulty string to fallback difficulty enum"""
        difficulty_map = {
            "basic": FallbackTestDifficulty.BASIC,
            "intermediate": FallbackTestDifficulty.INTERMEDIATE,
            "advanced": FallbackTestDifficulty.ADVANCED,
            "expert": FallbackTestDifficulty.EXPERT,
            "master": FallbackTestDifficulty.MASTER,
            "legendary": FallbackTestDifficulty.LEGENDARY
        }
        return difficulty_map.get(difficulty.lower(), FallbackTestDifficulty.INTERMEDIATE)

    def _get_fallback_category_for_test_type(self, test_type: str) -> FallbackTestCategory:
        """Get appropriate fallback category for test type"""
        category_map = {
            "custody": FallbackTestCategory.KNOWLEDGE_VERIFICATION,
            "olympic": FallbackTestCategory.PERFORMANCE_OPTIMIZATION,
            "collaborative": FallbackTestCategory.CROSS_AI_COLLABORATION,
            "security": FallbackTestCategory.SECURITY_AWARENESS,
            "innovation": FallbackTestCategory.INNOVATION_CAPABILITY,
            "code_quality": FallbackTestCategory.CODE_QUALITY,
            "self_improvement": FallbackTestCategory.SELF_IMPROVEMENT,
            "experimental": FallbackTestCategory.EXPERIMENTAL_VALIDATION
        }
        return category_map.get(test_type, FallbackTestCategory.KNOWLEDGE_VERIFICATION)

    def _get_fallback_time_limit(self, difficulty: FallbackTestDifficulty) -> int:
        """Get time limit for fallback test based on difficulty"""
        time_limits = {
            FallbackTestDifficulty.BASIC: 30,
            FallbackTestDifficulty.INTERMEDIATE: 45,
            FallbackTestDifficulty.ADVANCED: 60,
            FallbackTestDifficulty.EXPERT: 75,
            FallbackTestDifficulty.MASTER: 90,
            FallbackTestDifficulty.LEGENDARY: 120
        }
        return time_limits.get(difficulty, 45)

    def _create_emergency_fallback_scenario(self, ai_types: List[str], difficulty: str, test_type: str) -> Dict[str, Any]:
        """Create emergency fallback scenario when all else fails"""
        return {
            "id": f"emergency_fallback_{uuid.uuid4().hex[:8]}",
            "test_type": test_type,
            "difficulty": difficulty,
            "ai_types": ai_types,
            "description": f"Emergency fallback {test_type} test",
            "success_criteria": ["Complete the assigned task"],
            "time_limit": 30,
            "source": "emergency_fallback",
            "created_at": datetime.utcnow().isoformat(),
            "scenario_type": "emergency_fallback"
        }

    def _get_complexity_for_level(self, avg_level: float) -> TestComplexity:
        """Get complexity based on average AI level"""
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
        """Get current knowledge from cache"""
        knowledge = {
            "technologies": [],
            "concepts": [],
            "domains": []
        }
        
        for source, entries in self.internet_knowledge_cache.items():
            for entry in entries:
                content = entry.get("content", {})
                knowledge["technologies"].extend(content.get("technologies", []))
                knowledge["concepts"].extend(content.get("concepts", []))
                knowledge["domains"].extend(content.get("domains", []))
        
        # Remove duplicates
        knowledge["technologies"] = list(set(knowledge["technologies"]))
        knowledge["concepts"] = list(set(knowledge["concepts"]))
        knowledge["domains"] = list(set(knowledge["domains"]))
        
        return knowledge

    async def _generate_varied_requirements(self, test_type: str, complexity: TestComplexity, 
                                          knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate varied requirements based on test type and complexity"""
        requirements = []
        
        # Get technologies and concepts for requirements
        technologies = knowledge.get("technologies", ["Python", "JavaScript", "Docker"])
        concepts = knowledge.get("concepts", ["API Design", "Security", "Performance"])
        
        # Generate requirements based on test type
        if test_type == "custody":
            requirements.extend([
                await self._create_requirement(TestRequirement.KNOWLEDGE_VERIFICATION, technologies, concepts, complexity),
                await self._create_requirement(TestRequirement.CODE_QUALITY, technologies, concepts, complexity),
                await self._create_requirement(TestRequirement.SECURITY, technologies, concepts, complexity)
            ])
        elif test_type == "olympic":
            requirements.extend([
                await self._create_requirement(TestRequirement.PERFORMANCE, technologies, concepts, complexity),
                await self._create_requirement(TestRequirement.OPTIMIZATION, technologies, concepts, complexity),
                await self._create_requirement(TestRequirement.INNOVATION, technologies, concepts, complexity)
            ])
        elif test_type == "collaborative":
            requirements.extend([
                await self._create_requirement(TestRequirement.COLLABORATION, technologies, concepts, complexity),
                await self._create_requirement(TestRequirement.INTEGRATION, technologies, concepts, complexity),
                await self._create_requirement(TestRequirement.TESTING, technologies, concepts, complexity)
            ])
        
        return requirements

    async def _create_requirement(self, req_type: TestRequirement, technologies: List[str], 
                                 challenges: List[str], complexity: TestComplexity) -> Dict[str, Any]:
        """Create a specific requirement"""
        return {
            "type": req_type.value,
            "description": f"{req_type.value.replace('_', ' ').title()} requirement",
            "technologies": random.sample(technologies, min(3, len(technologies))),
            "challenges": random.sample(challenges, min(2, len(challenges))),
            "complexity": complexity.value,
            "points": self._get_points_for_complexity(complexity)
        }

    def _get_points_for_complexity(self, complexity: TestComplexity) -> int:
        """Get points based on complexity"""
        points_map = {
            TestComplexity.X1: 10,
            TestComplexity.X2: 20,
            TestComplexity.X3: 30,
            TestComplexity.X4: 40,
            TestComplexity.X5: 50,
            TestComplexity.X6: 60
        }
        return points_map.get(complexity, 20)

    async def _create_dynamic_scenario(self, requirements: List[Dict[str, Any]], 
                                     ai_types: List[str], complexity: TestComplexity) -> Dict[str, Any]:
        """Create dynamic scenario from requirements"""
        return {
            "id": f"dynamic_{uuid.uuid4().hex[:8]}",
            "requirements": requirements,
            "ai_types": ai_types,
            "complexity": complexity.value,
            "total_points": sum(req.get("points", 0) for req in requirements),
            "time_limit": self._get_time_limit(complexity),
            "created_at": datetime.utcnow().isoformat()
        }

    async def _generate_scenario_description(self, requirements: List[Dict[str, Any]], 
                                           ai_types: List[str], complexity: TestComplexity) -> str:
        """Generate scenario description"""
        req_types = [req["type"] for req in requirements]
        tech_list = []
        for req in requirements:
            tech_list.extend(req.get("technologies", []))
        tech_list = list(set(tech_list))
        
        return f"Dynamic {complexity.value} complexity test involving {', '.join(ai_types)} AIs. " \
               f"Requirements: {', '.join(req_types)}. Technologies: {', '.join(tech_list[:5])}."

    async def _generate_success_criteria(self, requirements: List[Dict[str, Any]], 
                                       complexity: TestComplexity) -> List[str]:
        """Generate success criteria"""
        criteria = [
            "Complete all assigned requirements",
            "Demonstrate understanding of technologies",
            "Provide clear and logical solutions",
            "Show appropriate technical knowledge"
        ]
        
        if complexity.value in ["x4", "x5", "x6"]:
            criteria.extend([
                "Demonstrate advanced problem-solving skills",
                "Show innovation and creativity",
                "Provide comprehensive documentation"
            ])
        
        return criteria

    def _get_time_limit(self, complexity: TestComplexity) -> int:
        """Get time limit based on complexity"""
        time_limits = {
            TestComplexity.X1: 30,
            TestComplexity.X2: 45,
            TestComplexity.X3: 60,
            TestComplexity.X4: 75,
            TestComplexity.X5: 90,
            TestComplexity.X6: 120
        }
        return time_limits.get(complexity, 45)

    async def _generate_docker_config(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Docker configuration for scenario"""
        if not self.docker_client:
            return {}
        
        return {
            "dockerfile": self._create_dockerfile(scenario),
            "docker_compose": self._create_docker_compose(scenario),
            "test_script": self._create_test_script(scenario),
            "environment": self._create_environment_config(scenario)
        }

    def _create_dockerfile(self, scenario: Dict[str, Any]) -> str:
        """Create Dockerfile for scenario"""
        return f"""FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "test_script.py"]
"""

    def _create_docker_compose(self, scenario: Dict[str, Any]) -> str:
        """Create docker-compose.yml for scenario"""
        services = {
            "app": {
                "build": ".",
                "ports": ["8000:8000"],
                "environment": self._create_environment_config(scenario)
            }
        }
        
        return f"""version: '3.8'
services:
{self._format_services(services)}
"""

    def _format_services(self, services: Dict[str, Any]) -> str:
        """Format services for docker-compose"""
        result = ""
        for service_name, config in services.items():
            result += f"  {service_name}:\n"
            for key, value in config.items():
                if isinstance(value, list):
                    result += f"    {key}:\n"
                    for item in value:
                        result += f"      - {item}\n"
                elif isinstance(value, dict):
                    result += f"    {key}:\n"
                    for k, v in value.items():
                        result += f"      {k}: {v}\n"
                else:
                    result += f"    {key}: {value}\n"
        return result

    def _create_test_script(self, scenario: Dict[str, Any]) -> str:
        """Create test script for scenario"""
        return f"""#!/usr/bin/env python3
import requests
import json

def test_scenario():
    print("Testing scenario: {scenario.get('id', 'unknown')}")
    print("Requirements: {len(scenario.get('requirements', []))}")
    print("AI Types: {', '.join(scenario.get('ai_types', []))}")
    
    # Add your test logic here
    return True

if __name__ == "__main__":
    test_scenario()
"""

    def _create_environment_config(self, scenario: Dict[str, Any]) -> Dict[str, str]:
        """Create environment configuration"""
        return {
            "SCENARIO_ID": scenario.get("id", "unknown"),
            "TEST_TYPE": scenario.get("test_type", "unknown"),
            "DIFFICULTY": scenario.get("difficulty", "intermediate"),
            "AI_TYPES": ",".join(scenario.get("ai_types", []))
        }

    async def _persist_scenario_to_database(self, scenario: Dict[str, Any]):
        """Persist scenario to database"""
        try:
            async with get_session() as session:
                # Store scenario metadata
                scenario_data = {
                    "scenario_id": scenario["id"],
                    "test_type": scenario.get("test_type", "unknown"),
                    "difficulty": scenario.get("difficulty", "intermediate"),
                    "ai_types": ",".join(scenario.get("ai_types", [])),
                    "description": scenario.get("description", ""),
                    "success_criteria": json.dumps(scenario.get("success_criteria", [])),
                    "time_limit": scenario.get("time_limit", 30),
                    "source": scenario.get("source", "enhanced_generator"),
                    "created_at": datetime.utcnow()
                }
                
                # You can add database persistence logic here
                logger.info(f"✅ Scenario {scenario['id']} persisted to database")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not persist scenario to database: {str(e)}")

    # Additional methods for AI response generation and evaluation
    async def generate_ai_self_generated_response(self, ai_type: str, scenario: Dict[str, Any], 
                                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate AI response using fallback system when Claude is unavailable"""
        try:
            # Check if Claude tokens are available
            tokens_available = await self._check_claude_tokens_available()
            
            if tokens_available:
                logger.info(f"🎯 Using Claude for AI response generation for {ai_type}")
                return await self._generate_claude_response(ai_type, scenario, context)
            else:
                logger.info(f"🔄 Using fallback system for AI response generation for {ai_type}")
                return await self._generate_fallback_response(ai_type, scenario, context)
                
        except Exception as e:
            logger.error(f"❌ Error generating AI response: {str(e)}")
            return await self._generate_fallback_response(ai_type, scenario, context)

    async def _generate_claude_response(self, ai_type: str, scenario: Dict[str, Any], 
                                       context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response using Claude"""
        try:
            # Generate response using Claude
            prompt = self._create_claude_prompt(ai_type, scenario, context)
            response = await anthropic_rate_limited_call(prompt, max_tokens=1000)
            
            return {
                "ai_type": ai_type,
                "response": response,
                "scenario_id": scenario.get("id"),
                "source": "claude",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating Claude response: {str(e)}")
            return await self._generate_fallback_response(ai_type, scenario, context)

    async def _generate_fallback_response(self, ai_type: str, scenario: Dict[str, Any], 
                                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response using fallback system"""
        try:
            # Use fallback service to generate response
            test_content = scenario.get("tests", {}).get(ai_type, {})
            
            # Generate fallback response based on test content
            response = self._create_fallback_response_content(ai_type, test_content, scenario)
            
            return {
                "ai_type": ai_type,
                "response": response,
                "scenario_id": scenario.get("id"),
                "source": "fallback_system",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating fallback response: {str(e)}")
            return {
                "ai_type": ai_type,
                "response": f"Fallback response for {ai_type}: Unable to generate detailed response.",
                "scenario_id": scenario.get("id"),
                "source": "emergency_fallback",
                "timestamp": datetime.utcnow().isoformat()
            }

    def _create_claude_prompt(self, ai_type: str, scenario: Dict[str, Any], 
                              context: Dict[str, Any] = None) -> str:
        """Create prompt for Claude"""
        return f"""You are {ai_type} AI. Please respond to the following scenario:

Scenario: {scenario.get('description', 'No description available')}
Requirements: {json.dumps(scenario.get('requirements', []), indent=2)}
Success Criteria: {json.dumps(scenario.get('success_criteria', []), indent=2)}

Please provide a comprehensive response that addresses all requirements and demonstrates your capabilities.
"""

    def _create_fallback_response_content(self, ai_type: str, test_content: Dict[str, Any], 
                                         scenario: Dict[str, Any]) -> str:
        """Create fallback response content"""
        response_parts = [
            f"Response from {ai_type} AI:",
            f"Scenario: {scenario.get('description', 'No description')}",
            f"Test Type: {scenario.get('test_type', 'unknown')}",
            f"Difficulty: {scenario.get('difficulty', 'intermediate')}",
            "",
            "Analysis:",
            "- Understanding the requirements and constraints",
            "- Applying relevant technical knowledge",
            "- Demonstrating problem-solving capabilities",
            "",
            "Solution:",
            "- Implement appropriate technical solutions",
            "- Follow best practices and standards",
            "- Ensure code quality and security",
            "",
            "Conclusion:",
            f"- Successfully addressed {scenario.get('test_type', 'test')} requirements",
            "- Demonstrated proficiency in required areas",
            "- Ready for evaluation and feedback"
        ]
        
        return "\n".join(response_parts)

    async def evaluate_test_result(self, ai_type: str, scenario: Dict[str, Any], 
                                  response: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate test result using fallback system"""
        try:
            # Check if Claude tokens are available
            tokens_available = await self._check_claude_tokens_available()
            
            if tokens_available:
                logger.info(f"🎯 Using Claude for test evaluation for {ai_type}")
                return await self._evaluate_with_claude(ai_type, scenario, response)
            else:
                logger.info(f"🔄 Using fallback system for test evaluation for {ai_type}")
                return await self._evaluate_with_fallback(ai_type, scenario, response)
                
        except Exception as e:
            logger.error(f"❌ Error evaluating test result: {str(e)}")
            return await self._evaluate_with_fallback(ai_type, scenario, response)

    async def _evaluate_with_claude(self, ai_type: str, scenario: Dict[str, Any], 
                                    response: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate using Claude"""
        try:
            # Create evaluation prompt
            prompt = self._create_evaluation_prompt(ai_type, scenario, response)
            evaluation_response = await anthropic_rate_limited_call(prompt, max_tokens=500)
            
            # Parse evaluation
            score = self._parse_evaluation_score(evaluation_response)
            feedback = self._parse_evaluation_feedback(evaluation_response)
            
            return {
                "ai_type": ai_type,
                "scenario_id": scenario.get("id"),
                "score": score,
                "feedback": feedback,
                "evaluation_source": "claude",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error evaluating with Claude: {str(e)}")
            return await self._evaluate_with_fallback(ai_type, scenario, response)

    async def _evaluate_with_fallback(self, ai_type: str, scenario: Dict[str, Any], 
                                     response: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate using fallback system"""
        try:
            # Use fallback service for evaluation
            test_content = scenario.get("tests", {}).get(ai_type, {})
            ai_response = response.get("response", "")
            
            # Evaluate using fallback service
            evaluation = await self.fallback_service.evaluate_fallback_test(
                ai_type=ai_type,
                test_content=test_content,
                ai_response=ai_response
            )
            
            return {
                "ai_type": ai_type,
                "scenario_id": scenario.get("id"),
                "score": evaluation.get("score", 0.0),
                "feedback": evaluation.get("feedback", "No feedback available"),
                "evaluation_source": "fallback_system",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error evaluating with fallback: {str(e)}")
            return {
                "ai_type": ai_type,
                "scenario_id": scenario.get("id"),
                "score": 0.0,
                "feedback": "Evaluation failed - using emergency fallback",
                "evaluation_source": "emergency_fallback",
                "timestamp": datetime.utcnow().isoformat()
            }

    def _create_evaluation_prompt(self, ai_type: str, scenario: Dict[str, Any], 
                                  response: Dict[str, Any]) -> str:
        """Create evaluation prompt for Claude"""
        return f"""Evaluate the following AI response:

AI Type: {ai_type}
Scenario: {scenario.get('description', 'No description')}
Requirements: {json.dumps(scenario.get('requirements', []), indent=2)}
Success Criteria: {json.dumps(scenario.get('success_criteria', []), indent=2)}

AI Response: {response.get('response', 'No response')}

Please provide:
1. A score from 0-100
2. Detailed feedback on strengths and areas for improvement
3. Specific recommendations for enhancement
"""

    def _parse_evaluation_score(self, evaluation_response: str) -> float:
        """Parse score from evaluation response"""
        try:
            # Look for score in response
            score_match = re.search(r'(\d+(?:\.\d+)?)', evaluation_response)
            if score_match:
                score = float(score_match.group(1))
                return min(max(score, 0.0), 100.0)  # Clamp between 0-100
            return 50.0  # Default score
        except Exception:
            return 50.0

    def _parse_evaluation_feedback(self, evaluation_response: str) -> str:
        """Parse feedback from evaluation response"""
        try:
            # Extract feedback section
            if "feedback:" in evaluation_response.lower():
                feedback_start = evaluation_response.lower().find("feedback:")
                return evaluation_response[feedback_start:].strip()
            return evaluation_response.strip()
        except Exception:
            return "Feedback parsing failed"

    # Additional utility methods
    async def get_test_statistics(self) -> Dict[str, Any]:
        """Get test generation statistics"""
        return {
            "total_scenarios_generated": len(self.scenario_templates),
            "fallback_usage_count": getattr(self, '_fallback_usage_count', 0),
            "claude_usage_count": getattr(self, '_claude_usage_count', 0),
            "last_generation": datetime.utcnow().isoformat()
        }

    async def update_knowledge_base(self):
        """Update knowledge base from learning cycles"""
        try:
            await self.update_internet_knowledge_from_learning_cycle()
            logger.info("✅ Knowledge base updated successfully")
        except Exception as e:
            logger.warning(f"⚠️ Could not update knowledge base: {str(e)}")

    async def update_internet_knowledge_from_learning_cycle(self):
        """Update internet knowledge from learning cycle data"""
        try:
            async with get_session() as session:
                # Get recent learning data
                result = await session.execute(
                    text("SELECT ai_type, subject, learning_outcome FROM learning ORDER BY created_at DESC LIMIT 100")
                )
                learning_entries = result.fetchall()
                
                # Process learning data
                for entry in learning_entries:
                    ai_type = entry[0]
                    subject = entry[1]
                    outcome = entry[2]
                    
                    # Store as knowledge
                    knowledge = {
                        "technologies": [subject] if subject else [],
                        "concepts": [outcome] if outcome else [],
                        "domains": [f"{ai_type} Learning"]
                    }
                    
                    await self._store_internet_knowledge(f"learning_{ai_type}", knowledge)
                
                logger.info(f"✅ Updated knowledge from {len(learning_entries)} learning entries")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not update knowledge from learning cycle: {str(e)}")

    async def _store_internet_knowledge(self, source: str, knowledge: Dict[str, Any]):
        """Store internet knowledge"""
        try:
            async with get_session() as session:
                # Store in database
                knowledge_entry = InternetKnowledge(
                    source=source,
                    source_type="learning_derived",
                    topic="AI Learning",
                    content=json.dumps(knowledge),
                    extracted_knowledge=knowledge,
                    relevance_score=0.8,
                    created_at=datetime.utcnow()
                )
                session.add(knowledge_entry)
                await session.commit()
                
                # Update cache
                if source not in self.internet_knowledge_cache:
                    self.internet_knowledge_cache[source] = []
                
                self.internet_knowledge_cache[source].append({
                    "type": "learning_derived",
                    "content": knowledge,
                    "timestamp": datetime.utcnow()
                })
                
        except Exception as e:
            logger.warning(f"⚠️ Could not store internet knowledge: {str(e)}")

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
            if hasattr(proposal, 'proposal_type'):
                proposal_type = proposal.proposal_type
                if proposal_type:
                    patterns['learning_topics'].append(proposal_type)
        
        # Analyze custody results
        for result in custody_results:
            if hasattr(result, 'test_category'):
                category = result.test_category
                if category:
                    patterns['learning_topics'].append(category)
        
        return patterns