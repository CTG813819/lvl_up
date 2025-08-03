"""
Enhanced Test Generation Service
Integrates internet search, AI knowledge, and progressive learning
"""

import asyncio
import aiohttp
import random
import uuid
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
import structlog
from bs4 import BeautifulSoup

from .logging_service import ai_logging_service, LogLevel, AISystemType

logger = structlog.get_logger()


class TestType(Enum):
    """Test types with internet integration"""
    COLLABORATIVE = "collaborative"
    OLYMPIC = "olympic"
    CUSTODES = "custodes"


class ContentCategory(Enum):
    """Content categories for varied test generation"""
    CODING = "coding"
    SCENARIOS = "scenarios"
    ARCHITECTURE = "architecture"
    DOCKER = "docker"
    REAL_LIFE_SIMULATIONS = "real_life_simulations"


class EnhancedTestGenerator:
    """Enhanced test generator with internet search and AI knowledge integration"""
    
    def __init__(self):
        self.ai_knowledge_base = {}
        self.learning_progress = {}
        self.difficulty_progression = {}
        self.internet_cache = {}
        self.test_history = {}
        
    async def generate_enhanced_test(self, test_type: TestType, ai_types: List[str], 
                                   current_difficulty: str = "intermediate") -> Dict[str, Any]:
        """Generate enhanced test with internet search and AI knowledge"""
        try:
            # Get internet knowledge
            internet_knowledge = await self._search_internet_knowledge(test_type, current_difficulty)
            
            # Get AI knowledge and learning progress
            ai_knowledge = await self._get_ai_knowledge(ai_types)
            
            # Determine next difficulty level
            next_difficulty = await self._calculate_next_difficulty(ai_types, current_difficulty)
            
            # Generate test content based on type
            if test_type == TestType.COLLABORATIVE:
                test_content = await self._generate_collaborative_test(internet_knowledge, ai_knowledge, next_difficulty)
            elif test_type == TestType.OLYMPIC:
                test_content = await self._generate_olympic_test(internet_knowledge, ai_knowledge, next_difficulty)
            elif test_type == TestType.CUSTODES:
                test_content = await self._generate_custodes_test(internet_knowledge, ai_knowledge, next_difficulty)
            else:
                raise ValueError(f"Unknown test type: {test_type}")
            
            # Add metadata
            test_content.update({
                "test_id": str(uuid.uuid4()),
                "test_type": test_type.value,
                "ai_types": ai_types,
                "difficulty": next_difficulty,
                "timestamp": datetime.utcnow().isoformat(),
                "internet_sources": internet_knowledge.get("sources", []),
                "ai_knowledge_used": list(ai_knowledge.keys())
            })
            
            # Log test generation
            ai_logging_service.log_test_execution(
                ai_type=",".join(ai_types),
                test_type=test_type.value,
                score=0.0,
                passed=False,
                duration=0.0,
                context={
                    "difficulty": next_difficulty,
                    "internet_sources_count": len(internet_knowledge.get("sources", [])),
                    "ai_knowledge_count": len(ai_knowledge)
                }
            )
            
            return test_content
            
        except Exception as e:
            logger.error(f"Error generating enhanced test: {str(e)}")
            raise
    
    async def _search_internet_knowledge(self, test_type: TestType, difficulty: str) -> Dict[str, Any]:
        """Search internet for current knowledge and trends"""
        try:
            # Define search queries based on test type and difficulty
            search_queries = self._get_search_queries(test_type, difficulty)
            
            knowledge_results = {
                "content": [],
                "sources": [],
                "trends": [],
                "technologies": []
            }
            
            async with aiohttp.ClientSession() as session:
                for query in search_queries:
                    try:
                        # Search multiple sources
                        sources = [
                            f"https://stackoverflow.com/search?q={query}",
                            f"https://github.com/search?q={query}",
                            f"https://medium.com/search?q={query}",
                            f"https://dev.to/search?q={query}"
                        ]
                        
                        for source in sources:
                            async with session.get(source, timeout=10) as response:
                                if response.status == 200:
                                    content = await response.text()
                                    soup = BeautifulSoup(content, 'html.parser')
                                    
                                    # Extract relevant information
                                    extracted_data = await self._extract_web_content(soup, source, query)
                                    knowledge_results["content"].extend(extracted_data)
                                    knowledge_results["sources"].append(source)
                                    
                    except Exception as e:
                        logger.warning(f"Error searching {query}: {str(e)}")
            
            return knowledge_results
            
        except Exception as e:
            logger.error(f"Error searching internet knowledge: {str(e)}")
            return {"content": [], "sources": [], "trends": [], "technologies": []}
    
    def _get_search_queries(self, test_type: TestType, difficulty: str) -> List[str]:
        """Get search queries based on test type and difficulty"""
        base_queries = {
            TestType.COLLABORATIVE: [
                "AI collaboration best practices",
                "multi-agent systems",
                "distributed AI architecture",
                "AI team coordination",
                "collaborative machine learning"
            ],
            TestType.OLYMPIC: [
                "advanced AI challenges",
                "AI competition scenarios",
                "complex problem solving AI",
                "AI performance optimization",
                "AI innovation challenges"
            ],
            TestType.CUSTODES: [
                "AI security testing",
                "AI validation methods",
                "AI quality assurance",
                "AI compliance testing",
                "AI performance benchmarks"
            ]
        }
        
        difficulty_modifiers = {
            "basic": ["beginner", "fundamentals", "basics"],
            "intermediate": ["advanced", "intermediate", "practical"],
            "advanced": ["expert", "complex", "sophisticated"],
            "expert": ["master", "cutting-edge", "innovative"],
            "master": ["legendary", "breakthrough", "revolutionary"],
            "legendary": ["unprecedented", "groundbreaking", "revolutionary"]
        }
        
        queries = base_queries.get(test_type, [])
        modifiers = difficulty_modifiers.get(difficulty, [])
        
        # Combine base queries with difficulty modifiers
        enhanced_queries = []
        for query in queries:
            for modifier in modifiers:
                enhanced_queries.append(f"{query} {modifier}")
        
        return enhanced_queries[:10]  # Limit to 10 queries
    
    async def _extract_web_content(self, soup: BeautifulSoup, source: str, query: str) -> List[Dict]:
        """Extract relevant content from web pages"""
        try:
            extracted_data = []
            
            if "stackoverflow" in source:
                # Extract questions and answers
                questions = soup.find_all('div', class_='question-summary')
                for q in questions[:5]:
                    title = q.find('h3').text.strip() if q.find('h3') else ""
                    excerpt = q.find('div', class_='excerpt').text.strip() if q.find('div', class_='excerpt') else ""
                    extracted_data.append({
                        "type": "stackoverflow_question",
                        "title": title,
                        "content": excerpt,
                        "source": source,
                        "query": query
                    })
            
            elif "github" in source:
                # Extract repository information
                repos = soup.find_all('div', class_='repo-list-item')
                for repo in repos[:5]:
                    name = repo.find('a', class_='v-align-middle').text.strip() if repo.find('a', class_='v-align-middle') else ""
                    description = repo.find('p', class_='mb-1').text.strip() if repo.find('p', class_='mb-1') else ""
                    extracted_data.append({
                        "type": "github_repository",
                        "name": name,
                        "description": description,
                        "source": source,
                        "query": query
                    })
            
            elif "medium" in source or "dev.to" in source:
                # Extract article information
                articles = soup.find_all('article') or soup.find_all('div', class_='post-card')
                for article in articles[:5]:
                    title = article.find('h2').text.strip() if article.find('h2') else ""
                    excerpt = article.find('p').text.strip() if article.find('p') else ""
                    extracted_data.append({
                        "type": "article",
                        "title": title,
                        "content": excerpt,
                        "source": source,
                        "query": query
                    })
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting web content: {str(e)}")
            return []
    
    async def _get_ai_knowledge(self, ai_types: List[str]) -> Dict[str, Any]:
        """Get AI knowledge and learning progress"""
        try:
            ai_knowledge = {}
            
            for ai_type in ai_types:
                # Get AI's current knowledge base
                if ai_type in self.ai_knowledge_base:
                    ai_knowledge[ai_type] = self.ai_knowledge_base[ai_type]
                else:
                    # Initialize AI knowledge
                    ai_knowledge[ai_type] = {
                        "strengths": [],
                        "weaknesses": [],
                        "learning_history": [],
                        "capabilities": [],
                        "recent_improvements": []
                    }
                
                # Get learning progress
                if ai_type in self.learning_progress:
                    ai_knowledge[ai_type]["progress"] = self.learning_progress[ai_type]
                else:
                    ai_knowledge[ai_type]["progress"] = {
                        "level": 1,
                        "experience_points": 0,
                        "skills_acquired": [],
                        "areas_for_improvement": []
                    }
            
            return ai_knowledge
            
        except Exception as e:
            logger.error(f"Error getting AI knowledge: {str(e)}")
            return {}
    
    async def _calculate_next_difficulty(self, ai_types: List[str], current_difficulty: str) -> str:
        """Calculate next difficulty level based on AI progress"""
        try:
            difficulties = ["basic", "intermediate", "advanced", "expert", "master", "legendary"]
            current_index = difficulties.index(current_difficulty)
            
            # Check if AIs are ready for next level
            ready_for_next = True
            for ai_type in ai_types:
                if ai_type in self.learning_progress:
                    progress = self.learning_progress[ai_type]
                    # Check if AI has enough experience and recent improvements
                    if progress.get("experience_points", 0) < (current_index + 1) * 100:
                        ready_for_next = False
                        break
            
            if ready_for_next and current_index < len(difficulties) - 1:
                return difficulties[current_index + 1]
            else:
                return current_difficulty
                
        except Exception as e:
            logger.error(f"Error calculating next difficulty: {str(e)}")
            return current_difficulty
    
    async def _generate_collaborative_test(self, internet_knowledge: Dict, ai_knowledge: Dict, difficulty: str) -> Dict[str, Any]:
        """Generate collaborative test with varied content"""
        try:
            # Select content category
            category = random.choice(list(ContentCategory))
            
            # Generate test based on category
            if category == ContentCategory.CODING:
                test_content = await self._generate_coding_collaborative_test(internet_knowledge, ai_knowledge, difficulty)
            elif category == ContentCategory.SCENARIOS:
                test_content = await self._generate_scenario_collaborative_test(internet_knowledge, ai_knowledge, difficulty)
            elif category == ContentCategory.ARCHITECTURE:
                test_content = await self._generate_architecture_collaborative_test(internet_knowledge, ai_knowledge, difficulty)
            elif category == ContentCategory.DOCKER:
                test_content = await self._generate_docker_collaborative_test(internet_knowledge, ai_knowledge, difficulty)
            elif category == ContentCategory.REAL_LIFE_SIMULATIONS:
                test_content = await self._generate_real_life_collaborative_test(internet_knowledge, ai_knowledge, difficulty)
            else:
                test_content = await self._generate_generic_collaborative_test(internet_knowledge, ai_knowledge, difficulty)
            
            return test_content
            
        except Exception as e:
            logger.error(f"Error generating collaborative test: {str(e)}")
            raise
    
    async def _generate_coding_collaborative_test(self, internet_knowledge: Dict, ai_knowledge: Dict, difficulty: str) -> Dict[str, Any]:
        """Generate coding collaborative test"""
        # Extract coding-related content from internet knowledge
        coding_content = [item for item in internet_knowledge.get("content", []) 
                         if "code" in item.get("content", "").lower() or "programming" in item.get("content", "").lower()]
        
        # Generate collaborative coding challenge
        challenge = {
            "type": "collaborative_coding",
            "scenario": f"Multiple AIs must collaborate to build a {difficulty} system",
            "requirements": [
                "Implement distributed architecture",
                "Handle concurrent operations",
                "Ensure data consistency",
                "Optimize performance",
                "Maintain code quality"
            ],
            "technologies": ["Python", "Docker", "Kubernetes", "Redis", "PostgreSQL"],
            "collaboration_points": [
                "API design and implementation",
                "Database schema design",
                "Testing strategy",
                "Deployment pipeline",
                "Monitoring and logging"
            ],
            "internet_knowledge": coding_content[:3],  # Use top 3 relevant pieces
            "ai_knowledge_requirements": list(ai_knowledge.keys())
        }
        
        return challenge
    
    async def _generate_scenario_collaborative_test(self, internet_knowledge: Dict, ai_knowledge: Dict, difficulty: str) -> Dict[str, Any]:
        """Generate scenario collaborative test"""
        # Extract scenario-related content
        scenario_content = [item for item in internet_knowledge.get("content", []) 
                          if "scenario" in item.get("content", "").lower() or "simulation" in item.get("content", "").lower()]
        
        challenge = {
            "type": "collaborative_scenario",
            "scenario": f"Real-world {difficulty} scenario requiring AI collaboration",
            "context": "Emergency response system with multiple AI agents",
            "roles": [
                "Data Analysis AI",
                "Decision Making AI", 
                "Communication AI",
                "Coordination AI"
            ],
            "challenges": [
                "Real-time data processing",
                "Critical decision making",
                "Inter-agent communication",
                "Resource coordination",
                "Failure handling"
            ],
            "success_criteria": [
                "Response time < 5 seconds",
                "Decision accuracy > 95%",
                "System availability > 99.9%",
                "Zero data loss"
            ],
            "internet_knowledge": scenario_content[:3],
            "ai_knowledge_requirements": list(ai_knowledge.keys())
        }
        
        return challenge
    
    async def _generate_architecture_collaborative_test(self, internet_knowledge: Dict, ai_knowledge: Dict, difficulty: str) -> Dict[str, Any]:
        """Generate architecture collaborative test"""
        # Extract architecture-related content
        arch_content = [item for item in internet_knowledge.get("content", []) 
                       if "architecture" in item.get("content", "").lower() or "design" in item.get("content", "").lower()]
        
        challenge = {
            "type": "collaborative_architecture",
            "scenario": f"Design a {difficulty} distributed system architecture",
            "requirements": [
                "Microservices architecture",
                "Event-driven design",
                "Scalability considerations",
                "Security implementation",
                "Monitoring and observability"
            ],
            "components": [
                "API Gateway",
                "Service Mesh",
                "Message Queue",
                "Database Cluster",
                "Load Balancer"
            ],
            "collaboration_areas": [
                "Service boundaries definition",
                "Data flow design",
                "Security architecture",
                "Deployment strategy",
                "Performance optimization"
            ],
            "internet_knowledge": arch_content[:3],
            "ai_knowledge_requirements": list(ai_knowledge.keys())
        }
        
        return challenge
    
    async def _generate_docker_collaborative_test(self, internet_knowledge: Dict, ai_knowledge: Dict, difficulty: str) -> Dict[str, Any]:
        """Generate Docker collaborative test"""
        # Extract Docker-related content
        docker_content = [item for item in internet_knowledge.get("content", []) 
                         if "docker" in item.get("content", "").lower() or "container" in item.get("content", "").lower()]
        
        challenge = {
            "type": "collaborative_docker",
            "scenario": f"Build a {difficulty} containerized application ecosystem",
            "requirements": [
                "Multi-container application",
                "Service orchestration",
                "Environment management",
                "Security hardening",
                "CI/CD pipeline"
            ],
            "services": [
                "Web Application",
                "API Service",
                "Database",
                "Cache",
                "Monitoring"
            ],
            "docker_components": [
                "Dockerfile optimization",
                "Docker Compose setup",
                "Volume management",
                "Network configuration",
                "Security scanning"
            ],
            "internet_knowledge": docker_content[:3],
            "ai_knowledge_requirements": list(ai_knowledge.keys())
        }
        
        return challenge
    
    async def _generate_real_life_collaborative_test(self, internet_knowledge: Dict, ai_knowledge: Dict, difficulty: str) -> Dict[str, Any]:
        """Generate real-life simulation collaborative test"""
        # Extract real-life related content
        real_life_content = [item for item in internet_knowledge.get("content", []) 
                            if "real" in item.get("content", "").lower() or "production" in item.get("content", "").lower()]
        
        challenge = {
            "type": "collaborative_real_life",
            "scenario": f"Simulate a {difficulty} real-world business scenario",
            "context": "E-commerce platform during Black Friday sale",
            "ai_roles": [
                "Inventory Management AI",
                "Customer Service AI",
                "Fraud Detection AI",
                "Recommendation AI",
                "Logistics AI"
            ],
            "challenges": [
                "Peak traffic handling",
                "Inventory synchronization",
                "Fraud prevention",
                "Customer satisfaction",
                "Order fulfillment"
            ],
            "metrics": [
                "Response time < 2 seconds",
                "99.9% uptime",
                "Zero fraud incidents",
                "95% customer satisfaction",
                "100% order accuracy"
            ],
            "internet_knowledge": real_life_content[:3],
            "ai_knowledge_requirements": list(ai_knowledge.keys())
        }
        
        return challenge
    
    async def _generate_generic_collaborative_test(self, internet_knowledge: Dict, ai_knowledge: Dict, difficulty: str) -> Dict[str, Any]:
        """Generate generic collaborative test"""
        challenge = {
            "type": "collaborative_generic",
            "scenario": f"General {difficulty} AI collaboration challenge",
            "requirements": [
                "Effective communication",
                "Task distribution",
                "Quality assurance",
                "Problem solving",
                "Innovation"
            ],
            "internet_knowledge": internet_knowledge.get("content", [])[:3],
            "ai_knowledge_requirements": list(ai_knowledge.keys())
        }
        
        return challenge
    
    async def _generate_olympic_test(self, internet_knowledge: Dict, ai_knowledge: Dict, difficulty: str) -> Dict[str, Any]:
        """Generate Olympic test with varied content"""
        # Similar structure to collaborative but focused on competition
        challenge = {
            "type": "olympic_competition",
            "scenario": f"AI Olympic competition at {difficulty} level",
            "categories": [
                "Speed Challenge",
                "Accuracy Challenge", 
                "Innovation Challenge",
                "Efficiency Challenge",
                "Creativity Challenge"
            ],
            "internet_knowledge": internet_knowledge.get("content", [])[:3],
            "ai_knowledge_requirements": list(ai_knowledge.keys())
        }
        
        return challenge
    
    async def _generate_custodes_test(self, internet_knowledge: Dict, ai_knowledge: Dict, difficulty: str) -> Dict[str, Any]:
        """Generate Custodes test with varied content"""
        # Similar structure but focused on validation and security
        challenge = {
            "type": "custodes_validation",
            "scenario": f"AI validation and security testing at {difficulty} level",
            "validation_areas": [
                "Security Testing",
                "Performance Testing",
                "Quality Assurance",
                "Compliance Testing",
                "Innovation Validation"
            ],
            "internet_knowledge": internet_knowledge.get("content", [])[:3],
            "ai_knowledge_requirements": list(ai_knowledge.keys())
        }
        
        return challenge
    
    async def update_ai_knowledge(self, ai_type: str, test_result: Dict[str, Any]):
        """Update AI knowledge based on test results"""
        try:
            if ai_type not in self.ai_knowledge_base:
                self.ai_knowledge_base[ai_type] = {
                    "strengths": [],
                    "weaknesses": [],
                    "learning_history": [],
                    "capabilities": [],
                    "recent_improvements": []
                }
            
            # Update based on test performance
            score = test_result.get("score", 0)
            passed = test_result.get("passed", False)
            
            if passed and score > 80:
                # AI performed well - add to strengths
                strength = f"Excelled in {test_result.get('test_type', 'unknown')} test"
                if strength not in self.ai_knowledge_base[ai_type]["strengths"]:
                    self.ai_knowledge_base[ai_type]["strengths"].append(strength)
            elif not passed:
                # AI needs improvement - add to weaknesses
                weakness = f"Needs improvement in {test_result.get('test_type', 'unknown')} test"
                if weakness not in self.ai_knowledge_base[ai_type]["weaknesses"]:
                    self.ai_knowledge_base[ai_type]["weaknesses"].append(weakness)
            
            # Update learning history
            self.ai_knowledge_base[ai_type]["learning_history"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "test_type": test_result.get("test_type", "unknown"),
                "score": score,
                "passed": passed,
                "difficulty": test_result.get("difficulty", "unknown")
            })
            
            # Update progress
            if ai_type not in self.learning_progress:
                self.learning_progress[ai_type] = {
                    "level": 1,
                    "experience_points": 0,
                    "skills_acquired": [],
                    "areas_for_improvement": []
                }
            
            # Award experience points
            points_earned = score if passed else score // 2
            self.learning_progress[ai_type]["experience_points"] += points_earned
            
            # Check for level up
            current_level = self.learning_progress[ai_type]["level"]
            required_xp = current_level * 100
            if self.learning_progress[ai_type]["experience_points"] >= required_xp:
                self.learning_progress[ai_type]["level"] += 1
                logger.info(f"AI {ai_type} leveled up to level {self.learning_progress[ai_type]['level']}")
            
        except Exception as e:
            logger.error(f"Error updating AI knowledge: {str(e)}")


# Global instance
enhanced_test_generator = EnhancedTestGenerator() 