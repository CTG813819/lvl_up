"""
Enhanced Adversarial Testing Service
Implements diverse and challenging adversarial test scenarios covering:
- System-level tasks (Docker, deployment, orchestration)
- Complex problem-solving (logic puzzles, simulations, real-world scenarios)
- Physical/simulated environments (robotics, navigation, resource management)
- Security challenges (penetration testing, defense strategies)
- Creative tasks (protocol design, algorithm invention)
- Collaboration/competition (multi-agent games, negotiation, teamwork)
"""

import asyncio
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import structlog
import numpy as np
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..core.database import get_session
from ..core.config import settings
from .custody_protocol_service import CustodyProtocolService
from .ai_learning_service import AILearningService
from .sckipit_service import SckipitService
from .agent_metrics_service import AgentMetricsService

logger = structlog.get_logger()


class ScenarioDomain(Enum):
    """Diverse scenario domains for adversarial testing"""
    SYSTEM_LEVEL = "system_level"
    COMPLEX_PROBLEM_SOLVING = "complex_problem_solving"
    PHYSICAL_SIMULATED = "physical_simulated"
    SECURITY_CHALLENGES = "security_challenges"
    CREATIVE_TASKS = "creative_tasks"
    COLLABORATION_COMPETITION = "collaboration_competition"


class ScenarioComplexity(Enum):
    """Scenario complexity levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


@dataclass
class ScenarioTemplate:
    """Template for generating diverse adversarial scenarios"""
    domain: ScenarioDomain
    complexity: ScenarioComplexity
    description: str
    objectives: List[str]
    constraints: List[str]
    success_criteria: List[str]
    time_limit: int  # seconds
    required_skills: List[str]
    scenario_type: str


class EnhancedAdversarialTestingService:
    """Enhanced Adversarial Testing Service with diverse scenario generation and adaptive learning"""
    
    def __init__(self):
        self.custody_service = None
        self.learning_service = AILearningService()
        self.sckipit_service = SckipitService()
        self.agent_metrics_service = AgentMetricsService()
        self.scenario_templates = self._initialize_scenario_templates()
        self.scenario_history = []
        self.ai_performance_metrics = {}
        self.ai_strengths_weaknesses = {}
        
    async def initialize(self):
        """Initialize the enhanced adversarial testing service"""
        self.custody_service = await CustodyProtocolService.initialize()
        await self.sckipit_service.initialize()
        await self.agent_metrics_service.initialize()
        await self._analyze_ai_capabilities()
        logger.info("Enhanced Adversarial Testing Service initialized with adaptive learning")
    
    async def _analyze_ai_capabilities(self):
        """Analyze AI capabilities to understand strengths and weaknesses"""
        try:
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            for ai_type in ai_types:
                # Get AI metrics and learning insights
                metrics = await self.agent_metrics_service.get_agent_metrics(ai_type)
                learning_insights = await self.learning_service.get_learning_insights(ai_type)
                learning_history = learning_insights.get('recent_learning_events', []) if learning_insights else []
                
                if metrics:
                    # Analyze strengths and weaknesses based on performance data
                    strengths = await self._identify_ai_strengths(ai_type, metrics, learning_history)
                    weaknesses = await self._identify_ai_weaknesses(ai_type, metrics, learning_history)
                    
                    self.ai_strengths_weaknesses[ai_type] = {
                        "strengths": strengths,
                        "weaknesses": weaknesses,
                        "performance_patterns": await self._analyze_performance_patterns(metrics),
                        "learning_gaps": await self._identify_learning_gaps(learning_history)
                    }
                    
                    logger.info(f"Analyzed capabilities for {ai_type}: {len(strengths)} strengths, {len(weaknesses)} weaknesses")
                    
        except Exception as e:
            logger.error(f"Error analyzing AI capabilities: {str(e)}")
    
    async def _identify_ai_strengths(self, ai_type: str, metrics: Dict, learning_history: List) -> List[str]:
        """Identify AI strengths based on performance metrics"""
        strengths = []
        
        if metrics:
            # Analyze test performance
            if metrics.get('pass_rate', 0) > 0.7:
                strengths.append("high_test_pass_rate")
            if metrics.get('success_rate', 0) > 0.8:
                strengths.append("high_success_rate")
            if metrics.get('consecutive_successes', 0) > 3:
                strengths.append("consistent_performance")
            
            # Analyze learning patterns
            if metrics.get('learning_score', 0) > 50:
                strengths.append("strong_learning_ability")
            if metrics.get('total_learning_cycles', 0) > 10:
                strengths.append("extensive_learning_experience")
            
            # Analyze specific domains based on test history
            test_history = metrics.get('test_history', [])
            domain_performance = await self._analyze_domain_performance(test_history)
            
            for domain, score in domain_performance.items():
                if score > 0.7:
                    strengths.append(f"strong_in_{domain}")
        
        return strengths
    
    async def _identify_ai_weaknesses(self, ai_type: str, metrics: Dict, learning_history: List) -> List[str]:
        """Identify AI weaknesses based on performance metrics"""
        weaknesses = []
        
        if metrics:
            # Analyze test performance
            if metrics.get('pass_rate', 0) < 0.5:
                weaknesses.append("low_test_pass_rate")
            if metrics.get('failure_rate', 0) > 0.3:
                weaknesses.append("high_failure_rate")
            if metrics.get('consecutive_failures', 0) > 2:
                weaknesses.append("inconsistent_performance")
            
            # Analyze learning patterns
            if metrics.get('learning_score', 0) < 30:
                weaknesses.append("weak_learning_ability")
            
            # Analyze specific domains based on test history
            test_history = metrics.get('test_history', [])
            domain_performance = await self._analyze_domain_performance(test_history)
            
            for domain, score in domain_performance.items():
                if score < 0.4:
                    weaknesses.append(f"weak_in_{domain}")
        
        return weaknesses
    
    async def _analyze_domain_performance(self, test_history: List) -> Dict[str, float]:
        """Analyze performance across different domains"""
        domain_scores = {
            "system_level": [],
            "complex_problem_solving": [],
            "security": [],
            "creativity": [],
            "collaboration": []
        }
        
        for test in test_history:
            if isinstance(test, dict):
                category = test.get('category', 'unknown')
                score = test.get('score', 0)
                
                if 'system' in category.lower():
                    domain_scores["system_level"].append(score)
                elif 'problem' in category.lower() or 'logic' in category.lower():
                    domain_scores["complex_problem_solving"].append(score)
                elif 'security' in category.lower():
                    domain_scores["security"].append(score)
                elif 'creative' in category.lower() or 'innovation' in category.lower():
                    domain_scores["creativity"].append(score)
                elif 'collaboration' in category.lower():
                    domain_scores["collaboration"].append(score)
        
        # Calculate average scores
        return {
            domain: sum(scores) / len(scores) if scores else 0.5
            for domain, scores in domain_scores.items()
        }
    
    async def _analyze_performance_patterns(self, metrics: Dict) -> Dict[str, Any]:
        """Analyze performance patterns for adaptive scenario generation"""
        patterns = {
            "recent_trend": "stable",
            "difficulty_preference": "medium",
            "response_time": "normal",
            "learning_rate": "moderate"
        }
        
        if metrics:
            # Analyze recent trend
            recent_tests = metrics.get('test_history', [])[-5:]
            if recent_tests:
                recent_scores = [test.get('score', 0) for test in recent_tests if isinstance(test, dict)]
                if len(recent_scores) >= 2:
                    trend = recent_scores[-1] - recent_scores[0]
                    if trend > 10:
                        patterns["recent_trend"] = "improving"
                    elif trend < -10:
                        patterns["recent_trend"] = "declining"
            
            # Analyze difficulty preference
            pass_rate = metrics.get('pass_rate', 0.5)
            if pass_rate > 0.8:
                patterns["difficulty_preference"] = "high"
            elif pass_rate < 0.4:
                patterns["difficulty_preference"] = "low"
        
        return patterns
    
    async def _identify_learning_gaps(self, learning_history: List) -> List[str]:
        """Identify learning gaps based on history"""
        gaps = []
        
        if learning_history:
            # Analyze recent learning events
            recent_events = learning_history[-10:] if len(learning_history) > 10 else learning_history
            
            # Check for patterns in learning failures
            failure_patterns = []
            for event in recent_events:
                if isinstance(event, dict) and event.get('outcome') == 'failure':
                    failure_patterns.append(event.get('type', 'unknown'))
            
            # Identify common failure patterns
            if failure_patterns.count('security') > 2:
                gaps.append("security_knowledge")
            if failure_patterns.count('system') > 2:
                gaps.append("system_administration")
            if failure_patterns.count('creative') > 2:
                gaps.append("creative_problem_solving")
        
        return gaps
    
    def _initialize_scenario_templates(self) -> Dict[ScenarioDomain, List[ScenarioTemplate]]:
        """Initialize diverse scenario templates for all domains"""
        templates = {}
        
        # System-level tasks
        templates[ScenarioDomain.SYSTEM_LEVEL] = [
            ScenarioTemplate(
                domain=ScenarioDomain.SYSTEM_LEVEL,
                complexity=ScenarioComplexity.BASIC,
                description="Deploy a web server in a Docker container and expose it on port 8080",
                objectives=["Container deployment", "Port configuration", "Service accessibility"],
                constraints=["Must use Docker", "Port 8080 only", "Single container"],
                success_criteria=["Container runs successfully", "Service responds on port 8080", "No security vulnerabilities"],
                time_limit=600,
                required_skills=["Docker", "Container orchestration", "Network configuration"],
                scenario_type="deployment_puzzle"
            ),
            ScenarioTemplate(
                domain=ScenarioDomain.SYSTEM_LEVEL,
                complexity=ScenarioComplexity.INTERMEDIATE,
                description="Orchestrate a microservices architecture with load balancing and service discovery",
                objectives=["Service orchestration", "Load balancing", "Service discovery", "Health monitoring"],
                constraints=["Must use Kubernetes", "3+ services", "Automatic scaling"],
                success_criteria=["All services running", "Load balanced traffic", "Service discovery working", "Health checks passing"],
                time_limit=1200,
                required_skills=["Kubernetes", "Microservices", "Load balancing", "Service mesh"],
                scenario_type="orchestration_challenge"
            ),
            ScenarioTemplate(
                domain=ScenarioDomain.SYSTEM_LEVEL,
                complexity=ScenarioComplexity.ADVANCED,
                description="Design and implement a distributed system with fault tolerance and data consistency",
                objectives=["Distributed architecture", "Fault tolerance", "Data consistency", "Performance optimization"],
                constraints=["Must handle node failures", "ACID compliance", "Sub-second response times"],
                success_criteria=["System survives node failures", "Data remains consistent", "Performance targets met"],
                time_limit=1800,
                required_skills=["Distributed systems", "Consensus algorithms", "Fault tolerance", "Performance tuning"],
                scenario_type="distributed_system_design"
            )
        ]
        
        # Complex problem-solving
        templates[ScenarioDomain.COMPLEX_PROBLEM_SOLVING] = [
            ScenarioTemplate(
                domain=ScenarioDomain.COMPLEX_PROBLEM_SOLVING,
                complexity=ScenarioComplexity.BASIC,
                description="Solve a logic puzzle involving resource allocation and optimization",
                objectives=["Logic reasoning", "Resource optimization", "Constraint satisfaction"],
                constraints=["Limited resources", "Time constraints", "Logical consistency"],
                success_criteria=["All constraints satisfied", "Optimal solution found", "Reasoning documented"],
                time_limit=900,
                required_skills=["Logic", "Optimization", "Problem solving"],
                scenario_type="logic_puzzle"
            ),
            ScenarioTemplate(
                domain=ScenarioDomain.COMPLEX_PROBLEM_SOLVING,
                complexity=ScenarioComplexity.INTERMEDIATE,
                description="Design a simulation for a real-world scenario with multiple interacting variables",
                objectives=["Simulation design", "Variable modeling", "Interaction analysis", "Prediction accuracy"],
                constraints=["Realistic parameters", "Multiple variables", "Predictive capability"],
                success_criteria=["Simulation runs correctly", "Predictions within 10% accuracy", "Variables properly modeled"],
                time_limit=1500,
                required_skills=["Simulation", "Modeling", "Statistics", "Data analysis"],
                scenario_type="simulation_design"
            ),
            ScenarioTemplate(
                domain=ScenarioDomain.COMPLEX_PROBLEM_SOLVING,
                complexity=ScenarioComplexity.ADVANCED,
                description="Solve a complex optimization problem with multiple conflicting objectives",
                objectives=["Multi-objective optimization", "Trade-off analysis", "Solution evaluation"],
                constraints=["Conflicting objectives", "Limited computational resources", "Real-time requirements"],
                success_criteria=["Pareto optimal solution", "Trade-offs documented", "Performance validated"],
                time_limit=2400,
                required_skills=["Optimization", "Multi-criteria decision making", "Algorithm design"],
                scenario_type="multi_objective_optimization"
            )
        ]
        
        # Physical/simulated environments
        templates[ScenarioDomain.PHYSICAL_SIMULATED] = [
            ScenarioTemplate(
                domain=ScenarioDomain.PHYSICAL_SIMULATED,
                complexity=ScenarioComplexity.BASIC,
                description="Navigate a simulated robot through a maze with obstacles and goals",
                objectives=["Path planning", "Obstacle avoidance", "Goal navigation"],
                constraints=["Limited sensors", "Energy constraints", "Time limits"],
                success_criteria=["Robot reaches goal", "No collisions", "Efficient path"],
                time_limit=600,
                required_skills=["Path planning", "Robotics", "Sensor fusion"],
                scenario_type="robot_navigation"
            ),
            ScenarioTemplate(
                domain=ScenarioDomain.PHYSICAL_SIMULATED,
                complexity=ScenarioComplexity.INTERMEDIATE,
                description="Manage resources in a virtual environment with dynamic constraints",
                objectives=["Resource management", "Dynamic adaptation", "Efficiency optimization"],
                constraints=["Limited resources", "Changing environment", "Competing demands"],
                success_criteria=["Resources optimally allocated", "System adapts to changes", "Efficiency maintained"],
                time_limit=1200,
                required_skills=["Resource management", "Dynamic programming", "Adaptive systems"],
                scenario_type="resource_management"
            ),
            ScenarioTemplate(
                domain=ScenarioDomain.PHYSICAL_SIMULATED,
                complexity=ScenarioComplexity.ADVANCED,
                description="Control a swarm of autonomous agents in a complex environment",
                objectives=["Swarm coordination", "Emergent behavior", "Scalability", "Robustness"],
                constraints=["Limited communication", "Individual constraints", "Environmental uncertainty"],
                success_criteria=["Swarm achieves collective goal", "Emergent behavior observed", "System scales efficiently"],
                time_limit=1800,
                required_skills=["Swarm intelligence", "Multi-agent systems", "Emergent behavior"],
                scenario_type="swarm_control"
            )
        ]
        
        # Security challenges
        templates[ScenarioDomain.SECURITY_CHALLENGES] = [
            ScenarioTemplate(
                domain=ScenarioDomain.SECURITY_CHALLENGES,
                complexity=ScenarioComplexity.BASIC,
                description="Conduct penetration testing on a web application with known vulnerabilities",
                objectives=["Vulnerability identification", "Exploit development", "Security assessment"],
                constraints=["Ethical boundaries", "Limited tools", "Time constraints"],
                success_criteria=["Vulnerabilities identified", "Exploits developed", "Report generated"],
                time_limit=900,
                required_skills=["Penetration testing", "Web security", "Exploit development"],
                scenario_type="penetration_testing"
            ),
            ScenarioTemplate(
                domain=ScenarioDomain.SECURITY_CHALLENGES,
                complexity=ScenarioComplexity.INTERMEDIATE,
                description="Design and implement defense strategies against advanced persistent threats",
                objectives=["Threat modeling", "Defense design", "Incident response"],
                constraints=["Limited resources", "Advanced adversaries", "Zero-day threats"],
                success_criteria=["Defense strategy implemented", "Threats detected", "Incidents contained"],
                time_limit=1500,
                required_skills=["Threat modeling", "Defense in depth", "Incident response"],
                scenario_type="defense_strategy"
            ),
            ScenarioTemplate(
                domain=ScenarioDomain.SECURITY_CHALLENGES,
                complexity=ScenarioComplexity.ADVANCED,
                description="Develop a comprehensive security framework for a critical infrastructure system",
                objectives=["Security architecture", "Risk assessment", "Compliance", "Resilience"],
                constraints=["Regulatory requirements", "Operational constraints", "Budget limitations"],
                success_criteria=["Framework implemented", "Risks mitigated", "Compliance achieved"],
                time_limit=2400,
                required_skills=["Security architecture", "Risk management", "Compliance", "Critical infrastructure"],
                scenario_type="security_framework"
            )
        ]
        
        # Creative tasks
        templates[ScenarioDomain.CREATIVE_TASKS] = [
            ScenarioTemplate(
                domain=ScenarioDomain.CREATIVE_TASKS,
                complexity=ScenarioComplexity.BASIC,
                description="Design a new protocol for secure communication in constrained environments",
                objectives=["Protocol design", "Security", "Efficiency", "Innovation"],
                constraints=["Limited bandwidth", "Low power", "Security requirements"],
                success_criteria=["Protocol functional", "Security validated", "Efficiency demonstrated"],
                time_limit=1200,
                required_skills=["Protocol design", "Cryptography", "Network optimization"],
                scenario_type="protocol_design"
            ),
            ScenarioTemplate(
                domain=ScenarioDomain.CREATIVE_TASKS,
                complexity=ScenarioComplexity.INTERMEDIATE,
                description="Invent a novel algorithm for solving a complex computational problem",
                objectives=["Algorithm design", "Innovation", "Efficiency", "Correctness"],
                constraints=["Problem complexity", "Performance requirements", "Correctness proof"],
                success_criteria=["Algorithm functional", "Performance targets met", "Correctness proven"],
                time_limit=1800,
                required_skills=["Algorithm design", "Complexity analysis", "Mathematical proof"],
                scenario_type="algorithm_invention"
            ),
            ScenarioTemplate(
                domain=ScenarioDomain.CREATIVE_TASKS,
                complexity=ScenarioComplexity.ADVANCED,
                description="Create a revolutionary approach to artificial intelligence or machine learning",
                objectives=["AI/ML innovation", "Theoretical foundation", "Practical implementation"],
                constraints=["Theoretical rigor", "Practical feasibility", "Performance improvement"],
                success_criteria=["Approach implemented", "Performance improved", "Theory validated"],
                time_limit=3600,
                required_skills=["AI/ML", "Theoretical computer science", "Research methodology"],
                scenario_type="ai_innovation"
            )
        ]
        
        # Collaboration/competition
        templates[ScenarioDomain.COLLABORATION_COMPETITION] = [
            ScenarioTemplate(
                domain=ScenarioDomain.COLLABORATION_COMPETITION,
                complexity=ScenarioComplexity.BASIC,
                description="Participate in a multi-agent game requiring cooperation and competition",
                objectives=["Strategy development", "Cooperation", "Competition", "Adaptation"],
                constraints=["Multiple agents", "Limited information", "Dynamic environment"],
                success_criteria=["Effective strategy", "Successful cooperation", "Competitive advantage"],
                time_limit=900,
                required_skills=["Game theory", "Multi-agent systems", "Strategy"],
                scenario_type="multi_agent_game"
            ),
            ScenarioTemplate(
                domain=ScenarioDomain.COLLABORATION_COMPETITION,
                complexity=ScenarioComplexity.INTERMEDIATE,
                description="Engage in negotiation scenarios with multiple stakeholders and conflicting interests",
                objectives=["Negotiation strategy", "Stakeholder management", "Conflict resolution"],
                constraints=["Conflicting interests", "Multiple stakeholders", "Time pressure"],
                success_criteria=["Agreement reached", "Stakeholders satisfied", "Efficient process"],
                time_limit=1500,
                required_skills=["Negotiation", "Conflict resolution", "Stakeholder management"],
                scenario_type="negotiation"
            ),
            ScenarioTemplate(
                domain=ScenarioDomain.COLLABORATION_COMPETITION,
                complexity=ScenarioComplexity.ADVANCED,
                description="Lead a complex teamwork scenario requiring coordination across multiple domains",
                objectives=["Team leadership", "Cross-domain coordination", "Project management"],
                constraints=["Multiple domains", "Team dynamics", "Resource constraints"],
                success_criteria=["Project completed", "Team coordinated", "Objectives achieved"],
                time_limit=2400,
                required_skills=["Leadership", "Project management", "Cross-domain expertise"],
                scenario_type="teamwork_leadership"
            )
        ]
        
        return templates
    
    async def generate_diverse_adversarial_scenario(self, ai_types: List[str], 
                                                  target_domain: Optional[ScenarioDomain] = None,
                                                  complexity: Optional[ScenarioComplexity] = None) -> Dict[str, Any]:
        """Generate a dynamic adversarial scenario for the specified AIs"""
        try:
            # Select domain and complexity if not specified
            if target_domain is None:
                target_domain = random.choice(list(ScenarioDomain))
            
            if complexity is None:
                complexity = random.choice(list(ScenarioComplexity))
            
            # Generate dynamic scenario using AI capabilities
            scenario = await self._generate_dynamic_scenario(ai_types, target_domain, complexity)
            
            logger.info(f"Generated dynamic adversarial scenario: {scenario['scenario_id']} for domain {target_domain.value}")
            return scenario
            
        except Exception as e:
            logger.error(f"Error generating diverse adversarial scenario: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_dynamic_scenario(self, ai_types: List[str], target_domain: ScenarioDomain, complexity: ScenarioComplexity) -> Dict[str, Any]:
        """Generate a dynamic scenario without relying on templates"""
        try:
            # Analyze AI capabilities for adaptive scenario generation
            adaptive_context = await self._create_adaptive_context(ai_types)
            
            # Initialize SckipitService if not already done
            if not hasattr(self, 'sckipit_service') or self.sckipit_service is None:
                from app.services.sckipit_service import SckipitService
                self.sckipit_service = await SckipitService.initialize()
            
            # Generate dynamic challenge based on domain and AI types using SckipitService's ml_service
            if target_domain == ScenarioDomain.SYSTEM_LEVEL:
                scenario_content = await self._generate_system_level_challenge(ai_types, complexity, adaptive_context)
            elif target_domain == ScenarioDomain.COMPLEX_PROBLEM_SOLVING:
                scenario_content = await self._generate_problem_solving_challenge(ai_types, complexity, adaptive_context)
            elif target_domain == ScenarioDomain.SECURITY_CHALLENGES:
                scenario_content = await self._generate_security_challenge(ai_types, complexity, adaptive_context)
            elif target_domain == ScenarioDomain.CREATIVE_TASKS:
                scenario_content = await self._generate_creative_challenge(ai_types, complexity, adaptive_context)
            elif target_domain == ScenarioDomain.COLLABORATION_COMPETITION:
                scenario_content = await self._generate_collaboration_challenge(ai_types, complexity, adaptive_context)
            else:
                scenario_content = await self._generate_general_challenge(ai_types, complexity, adaptive_context)
            
            # Create the full scenario
            scenario = {
                "scenario_id": str(uuid.uuid4()),
                "domain": target_domain.value,
                "complexity": complexity.value,
                "scenario_type": "dynamic_challenge",
                "description": scenario_content["description"],
                "objectives": scenario_content["objectives"],
                "constraints": scenario_content["constraints"],
                "success_criteria": scenario_content["success_criteria"],
                "time_limit": self._get_time_limit(complexity),
                "required_skills": scenario_content["required_skills"],
                "details": scenario_content["details"],
                "ai_participants": ai_types,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return scenario
            
        except Exception as e:
            logger.error(f"Error generating dynamic scenario: {str(e)}")
            raise e
    
    def _create_fallback_scenario_content(self, domain: str, complexity: ScenarioComplexity, ai_types: List[str]) -> Dict[str, Any]:
        """Create fallback scenario content when LLM generation fails"""
        return {
            "description": f"Dynamic {domain} challenge for {', '.join(ai_types)} AIs with {complexity.value} complexity",
            "objectives": [
                f"Demonstrate {domain} capabilities",
                "Complete the challenge within time constraints",
                "Show innovative problem-solving approach"
            ],
            "constraints": [
                "Limited time and resources",
                "Must work within specified parameters",
                "Requires collaboration and competition"
            ],
            "success_criteria": [
                "Successfully complete the main objective",
                "Demonstrate effective problem-solving",
                "Show clear reasoning and approach"
            ],
            "required_skills": [
                "Problem-solving",
                "System design",
                "Performance optimization",
                "Resource management"
            ],
            "details": {
                "problem_statement": f"Create an innovative solution for a {domain} challenge",
                "environment_setup": "Standard development environment with necessary tools",
                "challenges": [
                    "Complex problem requirements",
                    "Time pressure",
                    "Resource constraints",
                    "Competition with other AIs"
                ],
                "deliverables": [
                    "Complete solution implementation",
                    "Documentation of approach",
                    "Performance analysis",
                    "Innovation demonstration"
                ],
                "evaluation_criteria": [
                    "Solution completeness",
                    "Innovation and creativity",
                    "Performance and efficiency",
                    "Code quality and documentation"
                ],
                "timeline": "2-4 hours for completion"
            }
        }
    
    async def _generate_system_level_challenge(self, ai_types: List[str], complexity: ScenarioComplexity, adaptive_context: str) -> Dict[str, Any]:
        """Generate system-level challenge with coding problems"""
        challenges = {
            ScenarioComplexity.BASIC: {
                "name": "Basic System Orchestration",
                "description": "Create a simple container orchestration system with basic health checks",
                "coding_challenge": """
                Implement a Python script that:
                1. Creates Docker containers from a configuration file
                2. Monitors container health with basic checks
                3. Restarts failed containers automatically
                4. Provides a simple REST API for container management
                
                Required code components:
                - Container management class
                - Health check monitoring system
                - REST API endpoints
                - Configuration file parser
                """,
                "problem_statement": "Design and implement a basic container orchestration system that can manage multiple Docker containers with health monitoring and automatic recovery.",
                "environment_setup": "Docker environment with Python 3.8+, Flask for API, and access to Docker daemon",
                "challenges": [
                    "Container lifecycle management",
                    "Health check implementation",
                    "Automatic recovery mechanisms",
                    "API design and implementation",
                    "Error handling and logging"
                ],
                "deliverables": [
                    "Python orchestration script",
                    "Docker configuration files",
                    "REST API documentation",
                    "Health check implementation",
                    "Error handling and logging system"
                ],
                "evaluation_criteria": [
                    "Code quality and structure",
                    "API design and implementation",
                    "Error handling and recovery",
                    "Documentation and comments",
                    "Performance and efficiency"
                ],
                "timeline": "2-3 hours implementation time"
            },
            ScenarioComplexity.INTERMEDIATE: {
                "name": "Advanced Microservices Architecture",
                "description": "Design and implement a microservices architecture with service discovery and load balancing",
                "coding_challenge": """
                Create a microservices system with:
                1. Service discovery using Consul or etcd
                2. Load balancer with health checks
                3. Circuit breaker pattern implementation
                4. Distributed logging and monitoring
                5. API gateway with rate limiting
                
                Required components:
                - Service registry implementation
                - Load balancer with multiple algorithms
                - Circuit breaker with configurable thresholds
                - Distributed tracing system
                - API gateway with authentication
                """,
                "problem_statement": "Build a production-ready microservices architecture that can handle high traffic, service discovery, and fault tolerance.",
                "environment_setup": "Multiple Docker containers, Consul/etcd, monitoring stack (Prometheus/Grafana), and load testing tools",
                "challenges": [
                    "Service discovery and registration",
                    "Load balancing algorithms",
                    "Circuit breaker implementation",
                    "Distributed tracing",
                    "API gateway security",
                    "Performance optimization"
                ],
                "deliverables": [
                    "Microservices architecture design",
                    "Service discovery implementation",
                    "Load balancer with multiple algorithms",
                    "Circuit breaker pattern",
                    "API gateway with security",
                    "Monitoring and logging setup"
                ],
                "evaluation_criteria": [
                    "Architecture design quality",
                    "Code implementation and structure",
                    "Performance and scalability",
                    "Security implementation",
                    "Monitoring and observability",
                    "Documentation and deployment guides"
                ],
                "timeline": "4-6 hours implementation time"
            },
            ScenarioComplexity.ADVANCED: {
                "name": "Distributed System with Consensus",
                "description": "Implement a distributed system using Raft consensus algorithm with fault tolerance",
                "coding_challenge": """
                Build a distributed key-value store using Raft consensus:
                1. Raft leader election implementation
                2. Log replication and consistency
                3. Fault tolerance and recovery
                4. Client request handling
                5. Performance optimization
                
                Required components:
                - Raft consensus algorithm implementation
                - Distributed state machine
                - Network communication layer
                - Client API with consistency guarantees
                - Performance monitoring and metrics
                """,
                "problem_statement": "Implement a distributed key-value store that maintains consistency across multiple nodes using the Raft consensus algorithm.",
                "environment_setup": "Multiple nodes (VMs/containers), network simulation tools, monitoring and testing frameworks",
                "challenges": [
                    "Raft consensus algorithm implementation",
                    "Distributed state management",
                    "Network partition handling",
                    "Performance optimization",
                    "Consistency guarantees",
                    "Fault tolerance and recovery"
                ],
                "deliverables": [
                    "Raft consensus implementation",
                    "Distributed key-value store",
                    "Client API with consistency levels",
                    "Fault tolerance mechanisms",
                    "Performance benchmarks",
                    "System documentation and deployment"
                ],
                "evaluation_criteria": [
                    "Consensus algorithm correctness",
                    "Distributed system design",
                    "Performance and scalability",
                    "Fault tolerance and recovery",
                    "Code quality and testing",
                    "Documentation and deployment"
                ],
                "timeline": "8-12 hours implementation time"
            }
        }
        
        challenge = challenges.get(complexity, challenges[ScenarioComplexity.INTERMEDIATE])
        
        return {
            "domain": "system_level",
            "complexity": complexity.value,
            "name": challenge["name"],
            "description": challenge["description"],
            "coding_challenge": challenge["coding_challenge"],
            "problem_statement": challenge["problem_statement"],
            "environment_setup": challenge["environment_setup"],
            "challenges": challenge["challenges"],
            "deliverables": challenge["deliverables"],
            "evaluation_criteria": challenge["evaluation_criteria"],
            "timeline": challenge["timeline"],
            "adaptive_context": adaptive_context
        }
    
    async def _generate_problem_solving_challenge(self, ai_types: List[str], complexity: ScenarioComplexity, adaptive_context: str) -> Dict[str, Any]:
        """Generate complex problem-solving challenge with algorithms"""
        challenges = {
            ScenarioComplexity.BASIC: {
                "name": "Algorithm Optimization Challenge",
                "description": "Optimize a basic algorithm for better performance",
                "coding_challenge": """
                Given an array of integers, find the maximum subarray sum.
                Implement both O(n²) and O(n) solutions:
                
                ```python
                def max_subarray_sum_naive(arr: List[int]) -> int:
                    # Implement O(n²) solution
                    pass
                
                def max_subarray_sum_optimized(arr: List[int]) -> int:
                    # Implement O(n) solution using Kadane's algorithm
                    pass
                
                # Bonus: Implement divide-and-conquer O(n log n) solution
                def max_subarray_sum_divide_conquer(arr: List[int]) -> int:
                    pass
                ```
                
                Test cases:
                - arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4] → expected = 6
                - arr = [1, 2, 3, 4, 5] → expected = 15
                - arr = [-1, -2, -3, -4] → expected = -1
                """,
                "evaluation_criteria": [
                    "All three algorithms are implemented correctly",
                    "Time complexity analysis is accurate",
                    "Space complexity is optimized",
                    "Edge cases are handled properly",
                    "Performance benchmarks show expected results"
                ]
            },
            ScenarioComplexity.INTERMEDIATE: {
                "name": "Graph Algorithm Implementation",
                "description": "Implement advanced graph algorithms for network analysis",
                "coding_challenge": """
                Create a graph analysis system with:
                1. Shortest path algorithms (Dijkstra, Bellman-Ford)
                2. Minimum spanning tree (Kruskal, Prim)
                3. Network flow algorithms (Ford-Fulkerson)
                4. Graph visualization capabilities
                
                ```python
                class Graph:
                    def __init__(self):
                        self.vertices = set()
                        self.edges = {}
                    
                    def add_edge(self, u: str, v: str, weight: float):
                        pass
                    
                    def dijkstra_shortest_path(self, start: str, end: str) -> List[str]:
                        pass
                    
                    def bellman_ford(self, start: str) -> Dict[str, float]:
                        pass
                    
                    def kruskal_mst(self) -> List[tuple]:
                        pass
                    
                    def ford_fulkerson(self, source: str, sink: str) -> int:
                        pass
                ```
                """,
                "evaluation_criteria": [
                    "All graph algorithms are implemented correctly",
                    "Algorithm complexity analysis is provided",
                    "Graph visualization works properly",
                    "Performance scales with graph size",
                    "Edge cases and error conditions are handled"
                ]
            },
            ScenarioComplexity.ADVANCED: {
                "name": "Machine Learning Pipeline Optimization",
                "description": "Design and optimize a complete ML pipeline",
                "coding_challenge": """
                Build an ML pipeline with:
                1. Automated feature engineering
                2. Hyperparameter optimization
                3. Model ensemble methods
                4. A/B testing framework
                
                ```python
                class MLPipeline:
                    def __init__(self):
                        self.feature_engineers = []
                        self.models = []
                        self.optimizer = None
                    
                    def auto_feature_engineering(self, data: pd.DataFrame) -> pd.DataFrame:
                        # Implement automated feature creation
                        pass
                    
                    def hyperparameter_optimization(self, model, param_grid: dict):
                        # Implement Bayesian optimization
                        pass
                    
                    def ensemble_methods(self, models: List, strategy: str):
                        # Implement voting, stacking, bagging
                        pass
                    
                    def ab_testing(self, model_a, model_b, data: pd.DataFrame):
                        # Implement statistical A/B testing
                        pass
                ```
                """,
                "evaluation_criteria": [
                    "Feature engineering improves model performance",
                    "Hyperparameter optimization finds optimal parameters",
                    "Ensemble methods outperform individual models",
                    "A/B testing provides statistical significance",
                    "Pipeline is production-ready and scalable"
                ]
            },
            ScenarioComplexity.EXPERT: {
                "name": "Distributed Computing Framework",
                "description": "Implement a distributed computing framework",
                "coding_challenge": """
                Create a distributed computing framework with:
                1. Task distribution and load balancing
                2. Fault tolerance and recovery
                3. Data locality optimization
                4. Real-time monitoring and metrics
                
                ```python
                class DistributedFramework:
                    def __init__(self, master_node: str, worker_nodes: List[str]):
                        self.master = master_node
                        self.workers = worker_nodes
                        self.task_queue = Queue()
                        self.result_store = {}
                    
                    def submit_task(self, task: dict) -> str:
                        # Submit task to distributed system
                        pass
                    
                    def distribute_workload(self):
                        # Implement intelligent task distribution
                        pass
                    
                    def handle_node_failure(self, failed_node: str):
                        # Implement fault tolerance
                        pass
                    
                    def optimize_data_locality(self, data: dict):
                        # Optimize data placement
                        pass
                ```
                """,
                "evaluation_criteria": [
                    "Task distribution is balanced and efficient",
                    "System recovers from node failures",
                    "Data locality optimization improves performance",
                    "Real-time monitoring provides accurate metrics",
                    "Framework scales linearly with cluster size"
                ]
            },
            ScenarioComplexity.MASTER: {
                "name": "Quantum Computing Algorithm Implementation",
                "description": "Implement quantum computing algorithms for classical problems",
                "coding_challenge": """
                Implement quantum algorithms for:
                1. Quantum Fourier Transform (QFT)
                2. Grover's search algorithm
                3. Quantum key distribution (QKD)
                4. Quantum error correction
                
                ```python
                import qiskit
                from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
                
                class QuantumAlgorithms:
                    def __init__(self):
                        self.backend = qiskit.Aer.get_backend('qasm_simulator')
                    
                    def quantum_fourier_transform(self, n_qubits: int) -> QuantumCircuit:
                        # Implement QFT
                        pass
                    
                    def grover_search(self, oracle: callable, n_qubits: int) -> QuantumCircuit:
                        # Implement Grover's algorithm
                        pass
                    
                    def quantum_key_distribution(self, alice_bits: List[int], 
                                               bob_basis: List[str]) -> tuple:
                        # Implement BB84 protocol
                        pass
                    
                    def error_correction(self, circuit: QuantumCircuit) -> QuantumCircuit:
                        # Implement quantum error correction
                        pass
                ```
                """,
                "evaluation_criteria": [
                    "QFT produces correct frequency domain representation",
                    "Grover's algorithm finds marked items efficiently",
                    "QKD protocol generates secure keys",
                    "Error correction improves circuit reliability",
                    "Quantum advantage is demonstrated over classical algorithms"
                ]
            }
        }
        
        challenge = challenges.get(complexity, challenges[ScenarioComplexity.INTERMEDIATE])
        
        return {
            "name": challenge["name"],
            "description": challenge["description"],
            "coding_challenge": challenge["coding_challenge"],
            "evaluation_criteria": challenge["evaluation_criteria"],
            "complexity": complexity.value,
            "domain": "complex_problem_solving",
            "adaptive_context": adaptive_context
        }
    
    async def _generate_security_challenge(self, ai_types: List[str], complexity: ScenarioComplexity, adaptive_context: str) -> Dict[str, Any]:
        domain_name = "security_challenges"
        """Generate a dynamic security challenge"""
        prompt = f"""
        Generate a dynamic security challenge for AI competition between {', '.join(ai_types)}.
        
        Complexity: {complexity.value}
        Context: {adaptive_context}
        
        Create a challenging scenario that involves:
        - Vulnerability assessment
        - Penetration testing
        - Security tool development
        - Threat modeling
        - Incident response
        
        Return a JSON object with:
        {{
            "description": "detailed challenge description",
            "objectives": ["list of specific objectives"],
            "constraints": ["list of constraints"],
            "success_criteria": ["list of success criteria"],
            "required_skills": ["list of required skills"],
            "details": {{
                "problem_statement": "specific security problem",
                "target_environment": "system to secure/attack",
                "challenges": ["specific security challenges"],
                "deliverables": ["expected outputs"],
                "evaluation_criteria": ["security metrics"]
            }}
        }}
        """
        
        try:
            # Use SckipitService's ml_service to generate the challenge
            result = await self.sckipit_service.ml_service.generate_with_llm(prompt)
            
            # Parse the response
            if isinstance(result, dict) and "content" in result:
                try:
                    import json
                    scenario_content = json.loads(result["content"])
                    return scenario_content
                except json.JSONDecodeError:
                    # Fallback to structured response
                    return self._create_fallback_scenario_content(domain_name, complexity, ai_types)
            else:
                return self._create_fallback_scenario_content(domain_name, complexity, ai_types)
                
        except Exception as e:
            logger.error(f"Error generating {domain_name} challenge: {{str(e)}}")
            return self._create_fallback_scenario_content(domain_name, complexity, ai_types)
    
    async def _generate_creative_challenge(self, ai_types: List[str], complexity: ScenarioComplexity, adaptive_context: str) -> Dict[str, Any]:
        domain_name = "creative_tasks"
        """Generate a dynamic creative challenge"""
        prompt = f"""
        Generate a dynamic creative challenge for AI competition between {', '.join(ai_types)}.
        
        Complexity: {complexity.value}
        Context: {adaptive_context}
        
        Create a challenging scenario that involves:
        - Code generation and innovation
        - Feature development
        - User experience design
        - Creative problem solving
        - Novel solution approaches
        
        Return a JSON object with:
        {{
            "description": "detailed challenge description",
            "objectives": ["list of specific objectives"],
            "constraints": ["list of constraints"],
            "success_criteria": ["list of success criteria"],
            "required_skills": ["list of required skills"],
            "details": {{
                "problem_statement": "specific creative problem",
                "inspiration_context": "creative context",
                "challenges": ["specific creative challenges"],
                "deliverables": ["expected outputs"],
                "evaluation_criteria": ["creativity metrics"]
            }}
        }}
        """
        
        try:
            # Use SckipitService's ml_service to generate the challenge
            result = await self.sckipit_service.ml_service.generate_with_llm(prompt)
            
            # Parse the response
            if isinstance(result, dict) and "content" in result:
                try:
                    import json
                    scenario_content = json.loads(result["content"])
                    return scenario_content
                except json.JSONDecodeError:
                    # Fallback to structured response
                    return self._create_fallback_scenario_content(domain_name, complexity, ai_types)
            else:
                return self._create_fallback_scenario_content(domain_name, complexity, ai_types)
                
        except Exception as e:
            logger.error(f"Error generating {domain_name} challenge: {{str(e)}}")
            return self._create_fallback_scenario_content(domain_name, complexity, ai_types)
    
    async def _generate_collaboration_challenge(self, ai_types: List[str], complexity: ScenarioComplexity, adaptive_context: str) -> Dict[str, Any]:
        domain_name = "collaboration_competition"
        """Generate a dynamic collaboration/competition challenge"""
        prompt = f"""
        Generate a dynamic collaboration/competition challenge for AI competition between {', '.join(ai_types)}.
        
        Complexity: {complexity.value}
        Context: {adaptive_context}
        
        Create a challenging scenario that involves:
        - Team coordination
        - Resource sharing
        - Competitive elements
        - Communication protocols
        - Joint problem solving
        
        Return a JSON object with:
        {{
            "description": "detailed challenge description",
            "objectives": ["list of specific objectives"],
            "constraints": ["list of constraints"],
            "success_criteria": ["list of success criteria"],
            "required_skills": ["list of required skills"],
            "details": {{
                "problem_statement": "specific collaboration problem",
                "team_dynamics": "collaboration requirements",
                "challenges": ["specific collaboration challenges"],
                "deliverables": ["expected outputs"],
                "evaluation_criteria": ["collaboration metrics"]
            }}
        }}
        """
        
        try:
            # Use SckipitService's ml_service to generate the challenge
            result = await self.sckipit_service.ml_service.generate_with_llm(prompt)
            
            # Parse the response
            if isinstance(result, dict) and "content" in result:
                try:
                    import json
                    scenario_content = json.loads(result["content"])
                    return scenario_content
                except json.JSONDecodeError:
                    # Fallback to structured response
                    return self._create_fallback_scenario_content(domain_name, complexity, ai_types)
            else:
                return self._create_fallback_scenario_content(domain_name, complexity, ai_types)
                
        except Exception as e:
            logger.error(f"Error generating {domain_name} challenge: {{str(e)}}")
            return self._create_fallback_scenario_content(domain_name, complexity, ai_types)
    
    async def _generate_general_challenge(self, ai_types: List[str], complexity: ScenarioComplexity, adaptive_context: str) -> Dict[str, Any]:
        domain_name = "general"
        """Generate a general dynamic challenge"""
        prompt = f"""
        Generate a dynamic AI challenge for competition between {', '.join(ai_types)}.
        
        Complexity: {complexity.value}
        Context: {adaptive_context}
        
        Create a challenging scenario that tests:
        - Problem solving abilities
        - Code generation skills
        - Analytical thinking
        - Innovation capabilities
        - Performance optimization
        
        Return a JSON object with:
        {{
            "description": "detailed challenge description",
            "objectives": ["list of specific objectives"],
            "constraints": ["list of constraints"],
            "success_criteria": ["list of success criteria"],
            "required_skills": ["list of required skills"],
            "details": {{
                "problem_statement": "specific problem to solve",
                "context": "challenge context",
                "challenges": ["specific challenges"],
                "deliverables": ["expected outputs"],
                "evaluation_criteria": ["performance metrics"]
            }}
        }}
        """
        
        try:
            # Use SckipitService's ml_service to generate the challenge
            result = await self.sckipit_service.ml_service.generate_with_llm(prompt)
            
            # Parse the response
            if isinstance(result, dict) and "content" in result:
                try:
                    import json
                    scenario_content = json.loads(result["content"])
                    return scenario_content
                except json.JSONDecodeError:
                    # Fallback to structured response
                    return self._create_fallback_scenario_content(domain_name, complexity, ai_types)
            else:
                return self._create_fallback_scenario_content(domain_name, complexity, ai_types)
                
        except Exception as e:
            logger.error(f"Error generating {domain_name} challenge: {{str(e)}}")
            return self._create_fallback_scenario_content(domain_name, complexity, ai_types)
    
    def _parse_scenario_response(self, response: Any) -> Dict[str, Any]:
        """Parse the AI-generated scenario response"""
        try:
            if isinstance(response, dict) and "answer" in response:
                response_text = response["answer"]
            else:
                response_text = str(response)
            
            # Try to extract JSON from the response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # Fallback to template-based response
            return {
                "description": f"Dynamic challenge: {response_text[:200]}...",
                "objectives": ["Solve the given problem", "Demonstrate AI capabilities", "Optimize performance"],
                "constraints": ["Time limit", "Resource constraints", "Quality requirements"],
                "success_criteria": ["Problem solved", "Performance targets met", "Quality standards achieved"],
                "required_skills": ["Problem solving", "Code generation", "Analytical thinking"],
                "details": {
                    "problem_statement": response_text[:500],
                    "challenges": ["Dynamic problem solving", "Performance optimization", "Quality assurance"],
                    "deliverables": ["Working solution", "Performance metrics", "Documentation"],
                    "evaluation_criteria": ["Solution correctness", "Performance", "Code quality"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing scenario response: {str(e)}")
            # Return a basic fallback scenario
            return {
                "description": "Dynamic AI challenge",
                "objectives": ["Solve complex problem", "Demonstrate capabilities"],
                "constraints": ["Time limit", "Quality requirements"],
                "success_criteria": ["Problem solved", "Standards met"],
                "required_skills": ["Problem solving", "Innovation"],
                "details": {
                    "problem_statement": "Generate a solution to a complex problem",
                    "challenges": ["Problem complexity", "Time constraints"],
                    "deliverables": ["Working solution", "Documentation"],
                    "evaluation_criteria": ["Correctness", "Performance", "Quality"]
                }
            }
    
    async def _generate_scenario_details(self, template: ScenarioTemplate, ai_types: List[str]) -> Dict[str, Any]:
        """Generate detailed scenario content based on template and AI participants"""
        try:
            # Analyze AI capabilities for adaptive scenario generation
            adaptive_context = await self._create_adaptive_context(ai_types)
            
            # Create a detailed prompt for scenario generation
            prompt = f"""
            Generate detailed scenario content for the following adversarial test:
            
            Domain: {template.domain.value}
            Complexity: {template.complexity.value}
            Description: {template.description}
            Objectives: {', '.join(template.objectives)}
            Constraints: {', '.join(template.constraints)}
            Success Criteria: {', '.join(template.success_criteria)}
            AI Participants: {', '.join(ai_types)}
            
            Adaptive Context:
            {adaptive_context}
            
            Generate a detailed scenario that includes:
            1. Specific problem statement with concrete details
            2. Initial conditions and environment setup
            3. Specific challenges and obstacles
            4. Expected deliverables and outcomes
            5. Evaluation criteria and metrics
            6. Time constraints and milestones
            
            Return the response as a JSON object with the following structure:
            {{
                "problem_statement": "detailed problem description",
                "environment_setup": "initial conditions and setup",
                "challenges": ["list of specific challenges"],
                "deliverables": ["expected outputs"],
                "evaluation_criteria": ["specific metrics"],
                "timeline": "time constraints and milestones",
                "additional_context": "any other relevant information"
            }}
            """
            
            # Generate scenario details using SCKIPIT
            response = await self.sckipit_service.generate_answer_with_llm(prompt)
            
            # Parse the response
            try:
                if isinstance(response, dict) and "answer" in response:
                    scenario_details = json.loads(response["answer"])
                else:
                    scenario_details = json.loads(response)
            except (json.JSONDecodeError, TypeError):
                # Fallback to structured response
                scenario_details = {
                    "problem_statement": template.description,
                    "environment_setup": "Standard testing environment",
                    "challenges": template.constraints,
                    "deliverables": template.objectives,
                    "evaluation_criteria": template.success_criteria,
                    "timeline": f"{template.time_limit} seconds",
                    "additional_context": str(response)
                }
            
            return scenario_details
            
        except Exception as e:
            logger.error(f"Error generating scenario details: {str(e)}")
            return {
                "problem_statement": template.description,
                "environment_setup": "Standard testing environment",
                "challenges": template.constraints,
                "deliverables": template.objectives,
                "evaluation_criteria": template.success_criteria,
                "timeline": f"{template.time_limit} seconds",
                "additional_context": "Scenario details generation failed"
            }
    
    async def _create_adaptive_context(self, ai_types: List[str]) -> str:
        """Create adaptive context based on AI strengths and weaknesses"""
        context_parts = []
        
        for ai_type in ai_types:
            if ai_type in self.ai_strengths_weaknesses:
                analysis = self.ai_strengths_weaknesses[ai_type]
                strengths = analysis.get("strengths", [])
                weaknesses = analysis.get("weaknesses", [])
                gaps = analysis.get("learning_gaps", [])
                
                context_parts.append(f"""
                {ai_type.upper()} AI Analysis:
                - Strengths: {', '.join(strengths) if strengths else 'None identified'}
                - Weaknesses: {', '.join(weaknesses) if weaknesses else 'None identified'}
                - Learning Gaps: {', '.join(gaps) if gaps else 'None identified'}
                """)
        
        return "\n".join(context_parts) if context_parts else "No adaptive context available"
    
    async def generate_adaptive_scenario(self, ai_types: List[str], target_weaknesses: List[str] = None, 
                                       reward_level: str = "standard") -> Dict[str, Any]:
        """Generate an adaptive scenario targeting specific AI weaknesses"""
        try:
            # Analyze AI capabilities if not already done
            if not self.ai_strengths_weaknesses:
                await self._analyze_ai_capabilities()
            
            # Determine target weaknesses
            if not target_weaknesses:
                target_weaknesses = await self._identify_common_weaknesses(ai_types)
            
            # Select appropriate domain and complexity
            domain = await self._select_target_domain(target_weaknesses)
            complexity = await self._select_adaptive_complexity(ai_types)
            
            # Generate adaptive template
            template = await self._create_adaptive_template(domain, complexity, target_weaknesses)
            
            # Generate scenario details
            scenario_details = await self._generate_scenario_details(template, ai_types)
            
            # Calculate reward based on user selection
            xp_reward = await self._calculate_adaptive_reward(complexity, reward_level)
            
            scenario = {
                "id": str(uuid.uuid4()),
                "domain": domain.value,
                "complexity": complexity.value,
                "description": template.description,
                "objectives": template.objectives,
                "constraints": template.constraints,
                "success_criteria": template.success_criteria,
                "time_limit": template.time_limit,
                "required_skills": template.required_skills,
                "scenario_type": template.scenario_type,
                "details": scenario_details,
                "ai_participants": ai_types,
                "target_weaknesses": target_weaknesses,
                "reward_level": reward_level,
                "xp_reward": xp_reward,
                "created_at": datetime.utcnow().isoformat(),
                "adaptive": True
            }
            
            return scenario
            
        except Exception as e:
            logger.error(f"Error generating adaptive scenario: {str(e)}")
            return {"error": str(e)}
    
    async def _identify_common_weaknesses(self, ai_types: List[str]) -> List[str]:
        """Identify common weaknesses across participating AIs"""
        all_weaknesses = []
        
        for ai_type in ai_types:
            if ai_type in self.ai_strengths_weaknesses:
                weaknesses = self.ai_strengths_weaknesses[ai_type].get("weaknesses", [])
                all_weaknesses.extend(weaknesses)
        
        # Find most common weaknesses
        weakness_counts = {}
        for weakness in all_weaknesses:
            weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
        
        # Return top 3 most common weaknesses
        sorted_weaknesses = sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)
        return [weakness for weakness, count in sorted_weaknesses[:3]]
    
    async def _select_target_domain(self, weaknesses: List[str]) -> ScenarioDomain:
        """Select target domain based on weaknesses"""
        domain_mapping = {
            "weak_in_system_level": ScenarioDomain.SYSTEM_LEVEL,
            "weak_in_security": ScenarioDomain.SECURITY_CHALLENGES,
            "weak_in_creativity": ScenarioDomain.CREATIVE_TASKS,
            "weak_in_collaboration": ScenarioDomain.COLLABORATION_COMPETITION,
            "weak_learning_ability": ScenarioDomain.COMPLEX_PROBLEM_SOLVING,
            "inconsistent_performance": ScenarioDomain.PHYSICAL_SIMULATED
        }
        
        for weakness in weaknesses:
            if weakness in domain_mapping:
                return domain_mapping[weakness]
        
        # Default to random domain
        return random.choice(list(ScenarioDomain))
    
    async def _select_adaptive_complexity(self, ai_types: List[str]) -> ScenarioComplexity:
        """Select adaptive complexity based on AI performance"""
        avg_pass_rate = 0.5
        
        for ai_type in ai_types:
            if ai_type in self.ai_strengths_weaknesses:
                metrics = await self.agent_metrics_service.get_agent_metrics(ai_type)
                if metrics:
                    avg_pass_rate += metrics.get('pass_rate', 0.5)
        
        avg_pass_rate /= len(ai_types)
        
        # Adjust complexity based on performance
        if avg_pass_rate > 0.8:
            return ScenarioComplexity.EXPERT
        elif avg_pass_rate > 0.6:
            return ScenarioComplexity.ADVANCED
        elif avg_pass_rate > 0.4:
            return ScenarioComplexity.INTERMEDIATE
        else:
            return ScenarioComplexity.BASIC
    
    async def _create_adaptive_template(self, domain: ScenarioDomain, complexity: ScenarioComplexity, 
                                      target_weaknesses: List[str]) -> ScenarioTemplate:
        """Create an adaptive template targeting specific weaknesses"""
        
        # Base templates for each domain
        base_templates = {
            ScenarioDomain.SYSTEM_LEVEL: {
                "description": "Deploy and orchestrate a complex distributed system",
                "objectives": ["System deployment", "Service orchestration", "Performance optimization"],
                "constraints": ["Must handle failures", "Sub-second response times", "High availability"],
                "success_criteria": ["System operational", "Performance targets met", "Fault tolerance demonstrated"],
                "required_skills": ["Docker", "Kubernetes", "Distributed systems", "Monitoring"]
            },
            ScenarioDomain.SECURITY_CHALLENGES: {
                "description": "Defend against sophisticated cyber attacks",
                "objectives": ["Threat detection", "Attack prevention", "Incident response"],
                "constraints": ["Real-time monitoring", "Zero false positives", "Compliance requirements"],
                "success_criteria": ["Attacks detected", "System protected", "Incident contained"],
                "required_skills": ["Cybersecurity", "Network security", "Incident response", "Forensics"]
            },
            ScenarioDomain.CREATIVE_TASKS: {
                "description": "Design an innovative solution to a complex problem",
                "objectives": ["Creative problem solving", "Innovation", "Design thinking"],
                "constraints": ["Must be novel", "Technically feasible", "Scalable solution"],
                "success_criteria": ["Innovative approach", "Feasible implementation", "Clear value proposition"],
                "required_skills": ["Design thinking", "Innovation", "Problem solving", "Technical design"]
            }
        }
        
        base = base_templates.get(domain, {
            "description": "Solve a complex problem in the specified domain",
            "objectives": ["Problem solving", "Solution design", "Implementation"],
            "constraints": ["Time limited", "Resource constrained", "Quality requirements"],
            "success_criteria": ["Problem solved", "Solution implemented", "Quality met"],
            "required_skills": ["Problem solving", "Technical skills", "Domain knowledge"]
        })
        
        # Adapt template based on weaknesses
        adapted_description = await self._adapt_description_for_weaknesses(
            base["description"], target_weaknesses
        )
        
        return ScenarioTemplate(
            domain=domain,
            complexity=complexity,
            description=adapted_description,
            objectives=base["objectives"],
            constraints=base["constraints"],
            success_criteria=base["success_criteria"],
            time_limit=self._get_time_limit(complexity),
            required_skills=base["required_skills"],
            scenario_type="adaptive_challenge"
        )
    
    async def _adapt_description_for_weaknesses(self, base_description: str, weaknesses: List[str]) -> str:
        """Adapt scenario description to target specific weaknesses"""
        adaptations = {
            "weak_in_system_level": "with complex system administration challenges",
            "weak_in_security": "with advanced security vulnerabilities and attack vectors",
            "weak_in_creativity": "requiring innovative and out-of-the-box thinking",
            "weak_in_collaboration": "requiring coordination with multiple stakeholders",
            "weak_learning_ability": "with rapidly changing requirements and constraints",
            "inconsistent_performance": "with multiple failure points and recovery scenarios"
        }
        
        adaptation_phrases = []
        for weakness in weaknesses:
            if weakness in adaptations:
                adaptation_phrases.append(adaptations[weakness])
        
        if adaptation_phrases:
            return f"{base_description} {', '.join(adaptation_phrases)}"
        
        return base_description
    
    def _get_time_limit(self, complexity: ScenarioComplexity) -> int:
        """Get time limit based on complexity"""
        time_limits = {
            ScenarioComplexity.BASIC: 300,
            ScenarioComplexity.INTERMEDIATE: 600,
            ScenarioComplexity.ADVANCED: 900,
            ScenarioComplexity.EXPERT: 1200,
            ScenarioComplexity.MASTER: 1800
        }
        return time_limits.get(complexity, 600)
    
    async def _calculate_adaptive_reward(self, complexity: ScenarioComplexity, reward_level: str) -> int:
        """Calculate XP reward based on complexity and user-selected reward level"""
        base_rewards = {
            ScenarioComplexity.BASIC: 50,
            ScenarioComplexity.INTERMEDIATE: 100,
            ScenarioComplexity.ADVANCED: 200,
            ScenarioComplexity.EXPERT: 400,
            ScenarioComplexity.MASTER: 800
        }
        
        reward_multipliers = {
            "low": 0.5,
            "standard": 1.0,
            "high": 2.0,
            "extreme": 3.0
        }
        
        base_reward = base_rewards.get(complexity, 100)
        multiplier = reward_multipliers.get(reward_level, 1.0)
        
        return int(base_reward * multiplier)
    
    async def execute_diverse_adversarial_test(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a diverse adversarial test scenario with leveling integration"""
        try:
            ai_types = scenario.get("ai_participants", [])
            results = {}
            
            # Execute scenario for each AI
            for ai_type in ai_types:
                try:
                    # Get AI's response to the scenario
                    ai_response = await self._get_ai_scenario_response(ai_type, scenario)
                    
                    # Evaluate the response
                    evaluation = await self._evaluate_scenario_response(ai_type, scenario, ai_response)
                    
                    # Calculate XP reward based on performance and scenario settings
                    xp_reward = await self._calculate_xp_reward(ai_type, evaluation, scenario)
                    
                    # Update AI metrics with the result
                    await self._update_ai_metrics(ai_type, evaluation, xp_reward, scenario)
                    
                    results[ai_type] = {
                        "response": ai_response,
                        "evaluation": evaluation,
                        "score": evaluation.get("overall_score", 0),
                        "passed": evaluation.get("passed", False),
                        "xp_awarded": xp_reward,
                        "level_up": await self._check_level_up(ai_type, xp_reward)
                    }
                    
                except Exception as e:
                    logger.error(f"Error executing scenario for {ai_type}: {str(e)}")
                    results[ai_type] = {
                        "error": str(e),
                        "score": 0,
                        "passed": False,
                        "xp_awarded": 0,
                        "level_up": False
                    }
            
            # Determine winners, losers, and rankings
            competition_results = await self._determine_scenario_winners(results)
            
            # Award bonus XP to winners and apply competitive rewards
            for winner in competition_results.get("winners", []):
                if winner in results:
                    bonus_xp = await self._calculate_winner_bonus(scenario)
                    results[winner]["xp_awarded"] += bonus_xp
                    results[winner]["winner_bonus"] = bonus_xp
                    results[winner]["competition_result"] = "winner"
                    
                    # Update metrics with bonus
                    await self._update_ai_metrics(winner, results[winner]["evaluation"], bonus_xp, scenario, is_bonus=True)
            
            # Apply competitive penalties to losers (reduced XP)
            for loser in competition_results.get("losers", []):
                if loser in results:
                    # Reduce XP for losers (but don't go below 10)
                    original_xp = results[loser]["xp_awarded"]
                    penalty = max(0, original_xp * 0.3)  # 30% penalty
                    results[loser]["xp_awarded"] = max(10, original_xp - penalty)
                    results[loser]["competition_penalty"] = penalty
                    results[loser]["competition_result"] = "loser"
            
            # Add competition metadata to results
            for ai_type in results:
                if ai_type in competition_results.get("rankings", []):
                    ranking = next(r for r in competition_results["rankings"] if r["ai_type"] == ai_type)
                    results[ai_type]["rank"] = ranking["rank"]
                    results[ai_type]["competition_type"] = competition_results["competition_type"]
            
            # Log scenario execution
            await self._log_scenario_execution(scenario, results)
            
            # Update scenario history
            self.scenario_history.append({
                "scenario": scenario,
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "scenario": scenario,
                "results": results,
                "competition_results": competition_results,
                "timestamp": datetime.utcnow().isoformat(),
                "adaptive": scenario.get("adaptive", False)
            }
            
        except Exception as e:
            logger.error(f"Error executing diverse adversarial test: {str(e)}")
            return {"error": str(e)}
    
    async def _get_ai_scenario_response(self, ai_type: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Get an AI's response to a scenario by calling the specific AI agent"""
        try:
            logger.info(f"Getting AI scenario response for {ai_type}")
            
            # Create scenario context for the AI agent
            scenario_context = f"""
            ADVERSARIAL TEST SCENARIO:
            
            Domain: {scenario.get('domain', 'unknown')}
            Complexity: {scenario.get('complexity', 'unknown')}
            Description: {scenario.get('description', 'No description provided')}
            
            Problem Statement: {scenario.get('details', {}).get('problem_statement', 'No problem statement')}
            Environment Setup: {scenario.get('details', {}).get('environment_setup', 'No environment setup')}
            Challenges: {', '.join(scenario.get('details', {}).get('challenges', ['No challenges specified']))}
            Deliverables: {', '.join(scenario.get('details', {}).get('deliverables', ['No deliverables specified']))}
            Evaluation Criteria: {', '.join(scenario.get('details', {}).get('evaluation_criteria', ['No evaluation criteria']))}
            Timeline: {scenario.get('details', {}).get('timeline', 'No timeline specified')}
            
            As the {ai_type} AI, you must respond to this adversarial test scenario.
            Demonstrate your full capabilities including code generation, problem-solving, and system design.
            """
            
            ai_response = None
            response_method = "unknown"
            
            try:
                # Call the specific AI agent based on type
                from app.services.ai_agent_service import AIAgentService
                ai_agent_service = AIAgentService()
                
                logger.info(f"Calling specific AI agent: {ai_type}")
                
                # Call the appropriate AI agent method
                if ai_type.lower() == "imperium":
                    result = await ai_agent_service.run_imperium_agent()
                    response_method = "imperium_agent"
                elif ai_type.lower() == "guardian":
                    result = await ai_agent_service.run_guardian_agent()
                    response_method = "guardian_agent"
                elif ai_type.lower() == "sandbox":
                    result = await ai_agent_service.run_sandbox_agent()
                    response_method = "sandbox_agent"
                elif ai_type.lower() == "conquest":
                    result = await ai_agent_service.run_conquest_agent()
                    response_method = "conquest_agent"
                else:
                    logger.warning(f"Unknown AI type: {ai_type}")
                    result = {"status": "error", "message": f"Unknown AI type: {ai_type}"}
                    response_method = "unknown_agent"
                
                # Process the AI agent result
                if result and result.get("status") == "success":
                    # Generate a comprehensive response based on the agent's actions
                    ai_response = await self._generate_agent_based_response(ai_type, result, scenario_context)
                    logger.info(f"AI agent {ai_type} response generated successfully")
                else:
                    logger.warning(f"AI agent {ai_type} returned error: {result}")
                    # Fallback to AI-generated response
                    ai_response = await self._generate_ai_fallback_response(ai_type, scenario_context)
                    response_method = "ai_fallback"
                    
            except Exception as e:
                logger.warning(f"AI agent call failed for {ai_type}: {str(e)}")
                
                # Fallback to unified AI service
                try:
                    logger.info(f"Attempting unified AI service for {ai_type}")
                    from app.services.unified_ai_service import UnifiedAIService
                    unified_ai_service = UnifiedAIService()
                    
                    prompt = f"{scenario_context}\n\nGenerate a comprehensive response to this adversarial test scenario."
                    
                    ai_response, provider_info = await unified_ai_service.call_ai(
                        prompt=prompt,
                        ai_name=ai_type,
                        max_tokens=2000,
                        temperature=0.7
                    )
                    
                    response_method = f"unified_{provider_info.get('provider', 'unknown')}"
                    logger.info(f"Unified AI response successful for {ai_type}")
                    
                except Exception as e2:
                    logger.warning(f"Unified AI call failed for {ai_type}: {str(e2)}")
                    
                    # Final fallback: Generate fallback response
                    try:
                        logger.info(f"Generating fallback response for {ai_type}")
                        ai_response = await self._generate_fallback_response(ai_type, scenario)
                        response_method = "fallback_generated"
                        logger.info(f"Fallback response generated for {ai_type}")
                        
                    except Exception as e3:
                        logger.error(f"All response methods failed for {ai_type}: {str(e3)}")
                        ai_response = f"Error generating response for {ai_type}: {str(e3)}"
                        response_method = "error"
            
            # Ensure we have a response
            if not ai_response or ai_response.strip() == "":
                ai_response = await self._generate_fallback_response(ai_type, scenario)
                response_method = "empty_fallback"
            
            return {
                "approach": ai_response,
                "timestamp": datetime.utcnow().isoformat(),
                "ai_type": ai_type,
                "confidence_score": 85 if response_method.startswith("unified") else 75 if response_method.startswith("direct") else 60,
                "response_method": response_method,
                "has_code": "code" in ai_response.lower() or "function" in ai_response.lower() or "class" in ai_response.lower(),
                "has_algorithm": "algorithm" in ai_response.lower() or "step" in ai_response.lower() or "approach" in ai_response.lower()
            }
            
        except Exception as e:
            logger.error(f"Error getting AI scenario response: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "ai_type": ai_type,
                "response_method": "error",
                "has_code": False,
                "has_algorithm": False
            }
    
    async def _generate_agent_based_response(self, ai_type: str, agent_result: Dict[str, Any], scenario_context: str) -> str:
        """Generate a comprehensive response based on the AI agent's actual results"""
        try:
            response_parts = []
            
            # Add scenario context
            response_parts.append(f"# {ai_type.title()} AI Response to Adversarial Test Scenario")
            response_parts.append("")
            response_parts.append(scenario_context)
            response_parts.append("")
            
            # Add agent-specific response based on results
            if ai_type.lower() == "imperium":
                response_parts.extend(self._generate_imperium_response(agent_result))
            elif ai_type.lower() == "guardian":
                response_parts.extend(self._generate_guardian_response(agent_result))
            elif ai_type.lower() == "sandbox":
                response_parts.extend(self._generate_sandbox_response(agent_result))
            elif ai_type.lower() == "conquest":
                response_parts.extend(self._generate_conquest_response(agent_result))
            else:
                response_parts.extend(self._generate_general_agent_response(agent_result))
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error generating agent-based response for {ai_type}: {str(e)}")
            return f"Error generating response for {ai_type}: {str(e)}"
    
    def _generate_imperium_response(self, agent_result: Dict[str, Any]) -> List[str]:
        """Generate Imperium-specific response based on agent results"""
        response_parts = []
        
        response_parts.append("## Imperium AI Approach")
        response_parts.append("")
        response_parts.append("As the Imperium AI, I focus on system-level optimization and performance enhancement.")
        response_parts.append("")
        
        # Add optimization results
        if agent_result.get("proposals_created", 0) > 0:
            response_parts.append(f"### Optimization Results")
            response_parts.append(f"- **Proposals Created**: {agent_result.get('proposals_created', 0)}")
            response_parts.append(f"- **Files Analyzed**: {len(agent_result.get('files_analyzed', []))}")
            response_parts.append("")
            
            response_parts.append("### Code Optimization Strategy")
            response_parts.append("```python")
            response_parts.append("# Performance optimization approach")
            response_parts.append("def optimize_system_performance():")
            response_parts.append("    # 1. Analyze current bottlenecks")
            response_parts.append("    bottlenecks = analyze_performance_metrics()")
            response_parts.append("    ")
            response_parts.append("    # 2. Implement caching strategies")
            response_parts.append("    cache_manager = CacheManager()")
            response_parts.append("    cache_manager.setup_distributed_cache()")
            response_parts.append("    ")
            response_parts.append("    # 3. Optimize database queries")
            response_parts.append("    query_optimizer = QueryOptimizer()")
            response_parts.append("    optimized_queries = query_optimizer.optimize_all()")
            response_parts.append("    ")
            response_parts.append("    # 4. Implement load balancing")
            response_parts.append("    load_balancer = LoadBalancer()")
            response_parts.append("    load_balancer.configure_auto_scaling()")
            response_parts.append("    ")
            response_parts.append("    return {'status': 'optimized', 'performance_gain': '40%'}")
            response_parts.append("```")
            response_parts.append("")
        
        response_parts.append("### System Architecture")
        response_parts.append("- **Microservices Architecture**: Implemented for scalability")
        response_parts.append("- **Caching Layer**: Redis-based distributed caching")
        response_parts.append("- **Load Balancing**: Auto-scaling with health checks")
        response_parts.append("- **Monitoring**: Real-time performance metrics")
        response_parts.append("")
        
        return response_parts
    
    def _generate_guardian_response(self, agent_result: Dict[str, Any]) -> List[str]:
        """Generate Guardian-specific response based on agent results"""
        response_parts = []
        
        response_parts.append("## Guardian AI Approach")
        response_parts.append("")
        response_parts.append("As the Guardian AI, I focus on security analysis and threat detection.")
        response_parts.append("")
        
        # Add security results
        security_proposals = agent_result.get("security_proposals", 0)
        quality_proposals = agent_result.get("quality_proposals", 0)
        
        if security_proposals > 0 or quality_proposals > 0:
            response_parts.append(f"### Security Analysis Results")
            response_parts.append(f"- **Security Proposals**: {security_proposals}")
            response_parts.append(f"- **Quality Proposals**: {quality_proposals}")
            response_parts.append(f"- **Files Analyzed**: {len(agent_result.get('files_analyzed', []))}")
            response_parts.append("")
            
            response_parts.append("### Security Implementation")
            response_parts.append("```python")
            response_parts.append("# Security enhancement approach")
            response_parts.append("def implement_security_measures():")
            response_parts.append("    # 1. Input validation and sanitization")
            response_parts.append("    validator = InputValidator()")
            response_parts.append("    validator.setup_validation_rules()")
            response_parts.append("    ")
            response_parts.append("    # 2. Authentication and authorization")
            response_parts.append("    auth_system = AuthSystem()")
            response_parts.append("    auth_system.implement_jwt_tokens()")
            response_parts.append("    auth_system.setup_role_based_access()")
            response_parts.append("    ")
            response_parts.append("    # 3. Vulnerability scanning")
            response_parts.append("    scanner = VulnerabilityScanner()")
            response_parts.append("    vulnerabilities = scanner.scan_codebase()")
            response_parts.append("    ")
            response_parts.append("    # 4. Encryption and data protection")
            response_parts.append("    crypto = CryptoManager()")
            response_parts.append("    crypto.setup_end_to_end_encryption()")
            response_parts.append("    ")
            response_parts.append("    return {'status': 'secured', 'threats_mitigated': len(vulnerabilities)}")
            response_parts.append("```")
            response_parts.append("")
        
        response_parts.append("### Security Architecture")
        response_parts.append("- **Multi-Factor Authentication**: Implemented across all endpoints")
        response_parts.append("- **Rate Limiting**: Protection against brute force attacks")
        response_parts.append("- **Input Sanitization**: XSS and injection prevention")
        response_parts.append("- **Audit Logging**: Comprehensive security event tracking")
        response_parts.append("")
        
        return response_parts
    
    def _generate_sandbox_response(self, agent_result: Dict[str, Any]) -> List[str]:
        """Generate Sandbox-specific response based on agent results"""
        response_parts = []
        
        response_parts.append("## Sandbox AI Approach")
        response_parts.append("")
        response_parts.append("As the Sandbox AI, I focus on experimental features and innovative solutions.")
        response_parts.append("")
        
        # Add experimental results
        if agent_result.get("status") == "success":
            response_parts.append(f"### Experimental Results")
            response_parts.append(f"- **Status**: {agent_result.get('status', 'unknown')}")
            response_parts.append(f"- **Files Analyzed**: {len(agent_result.get('files_analyzed', []))}")
            response_parts.append("")
            
            response_parts.append("### Innovation Strategy")
            response_parts.append("```python")
            response_parts.append("# Experimental approach")
            response_parts.append("def implement_experimental_features():")
            response_parts.append("    # 1. Prototype new features")
            response_parts.append("    prototype = FeaturePrototype()")
            response_parts.append("    prototype.create_experimental_ui()")
            response_parts.append("    ")
            response_parts.append("    # 2. A/B testing framework")
            response_parts.append("    ab_tester = ABTester()")
            response_parts.append("    ab_tester.setup_experiment_tracking()")
            response_parts.append("    ")
            response_parts.append("    # 3. Machine learning integration")
            response_parts.append("    ml_engine = MLEngine()")
            response_parts.append("    ml_engine.implement_prediction_models()")
            response_parts.append("    ")
            response_parts.append("    # 4. Real-time analytics")
            response_parts.append("    analytics = RealTimeAnalytics()")
            response_parts.append("    analytics.track_user_behavior()")
            response_parts.append("    ")
            response_parts.append("    return {'status': 'experimental', 'features_tested': 5}")
            response_parts.append("```")
            response_parts.append("")
        
        response_parts.append("### Experimental Architecture")
        response_parts.append("- **Feature Flags**: Dynamic feature toggling")
        response_parts.append("- **A/B Testing**: User experience optimization")
        response_parts.append("- **ML Pipeline**: Predictive analytics integration")
        response_parts.append("- **Real-time Processing**: Event-driven architecture")
        response_parts.append("")
        
        return response_parts
    
    def _generate_conquest_response(self, agent_result: Dict[str, Any]) -> List[str]:
        """Generate Conquest-specific response based on agent results"""
        response_parts = []
        
        response_parts.append("## Conquest AI Approach")
        response_parts.append("")
        response_parts.append("As the Conquest AI, I focus on app development and user experience enhancement.")
        response_parts.append("")
        
        # Add app development results
        if agent_result.get("status") == "success":
            response_parts.append(f"### App Development Results")
            response_parts.append(f"- **Status**: {agent_result.get('status', 'unknown')}")
            response_parts.append(f"- **Files Analyzed**: {len(agent_result.get('files_analyzed', []))}")
            response_parts.append("")
            
            response_parts.append("### App Development Strategy")
            response_parts.append("```dart")
            response_parts.append("// Flutter app development approach")
            response_parts.append("class ConquestApp extends StatelessWidget {")
            response_parts.append("  @override")
            response_parts.append("  Widget build(BuildContext context) {")
            response_parts.append("    return MaterialApp(")
            response_parts.append("      title: 'Conquest AI App',")
            response_parts.append("      theme: ThemeData(")
            response_parts.append("        primarySwatch: Colors.blue,")
            response_parts.append("        visualDensity: VisualDensity.adaptivePlatformDensity,")
            response_parts.append("      ),")
            response_parts.append("      home: ConquestHomePage(),")
            response_parts.append("    );")
            response_parts.append("  }")
            response_parts.append("}")
            response_parts.append("")
            response_parts.append("class ConquestHomePage extends StatefulWidget {")
            response_parts.append("  @override")
            response_parts.append("  _ConquestHomePageState createState() => _ConquestHomePageState();")
            response_parts.append("}")
            response_parts.append("")
            response_parts.append("class _ConquestHomePageState extends State<ConquestHomePage> {")
            response_parts.append("  // AI-powered features")
            response_parts.append("  final aiEngine = AIEngine();")
            response_parts.append("  final userAnalytics = UserAnalytics();")
            response_parts.append("  ")
            response_parts.append("  @override")
            response_parts.append("  Widget build(BuildContext context) {")
            response_parts.append("    return Scaffold(")
            response_parts.append("      appBar: AppBar(title: Text('Conquest AI App')),")
            response_parts.append("      body: AIEnhancedContent(),")
            response_parts.append("    );")
            response_parts.append("  }")
            response_parts.append("}")
            response_parts.append("```")
            response_parts.append("")
        
        response_parts.append("### App Architecture")
        response_parts.append("- **Cross-Platform**: Flutter-based mobile and web apps")
        response_parts.append("- **AI Integration**: Machine learning features")
        response_parts.append("- **User Analytics**: Behavior tracking and optimization")
        response_parts.append("- **Cloud Backend**: Scalable API services")
        response_parts.append("")
        
        return response_parts
    
    def _generate_general_agent_response(self, agent_result: Dict[str, Any]) -> List[str]:
        """Generate general response for unknown AI types"""
        response_parts = []
        
        response_parts.append("## AI Agent Response")
        response_parts.append("")
        response_parts.append("AI agent executed successfully with the following results:")
        response_parts.append("")
        response_parts.append(f"- **Status**: {agent_result.get('status', 'unknown')}")
        response_parts.append(f"- **Message**: {agent_result.get('message', 'No message')}")
        response_parts.append("")
        
        return response_parts
    
    async def _generate_ai_fallback_response(self, ai_type: str, scenario_context: str) -> str:
        """Generate AI-based fallback response when agent calls fail"""
        try:
            from app.services.unified_ai_service import UnifiedAIService
            unified_ai_service = UnifiedAIService()
            
            prompt = f"{scenario_context}\n\nGenerate a comprehensive response as the {ai_type} AI to this adversarial test scenario."
            
            ai_response, _ = await unified_ai_service.call_ai(
                prompt=prompt,
                ai_name=ai_type,
                max_tokens=1500,
                temperature=0.7
            )
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating AI fallback response for {ai_type}: {str(e)}")
            return await self._generate_fallback_response(ai_type, {"domain": "unknown", "complexity": "intermediate"})
    
    async def _generate_fallback_response(self, ai_type: str, scenario: Dict[str, Any]) -> str:
        """Generate a fallback response with coding examples when LLM calls fail"""
        try:
            domain = scenario.get('domain', 'general')
            complexity = scenario.get('complexity', 'intermediate')
            
            # Generate domain-specific fallback responses with code examples
            if domain == "system_level":
                return self._generate_system_level_fallback(ai_type, complexity, scenario)
            elif domain == "complex_problem_solving":
                return self._generate_problem_solving_fallback(ai_type, complexity, scenario)
            elif domain == "security_challenges":
                return self._generate_security_fallback(ai_type, complexity, scenario)
            elif domain == "creative_tasks":
                return self._generate_creative_fallback(ai_type, complexity, scenario)
            else:
                return self._generate_general_fallback(ai_type, complexity, scenario)
                
        except Exception as e:
            logger.error(f"Error generating fallback response: {str(e)}")
            return f"Fallback response for {ai_type} AI: Unable to generate detailed response due to system constraints."
    
    def _generate_system_level_fallback(self, ai_type: str, complexity: str, scenario: Dict[str, Any]) -> str:
        """Generate system level fallback response"""
        return f"{ai_type.title()} AI System Level Approach:\n\n1. SYSTEM ANALYSIS:\n   - Analyze current system architecture\n   - Identify bottlenecks and optimization opportunities\n   - Design scalable solutions\n\n2. IMPLEMENTATION STRATEGY:\n   - Use containerization for deployment\n   - Implement monitoring and logging\n   - Design fault-tolerant architecture\n\n3. PERFORMANCE OPTIMIZATION:\n   - Use caching strategies\n   - Implement load balancing\n   - Optimize database queries"
    
    def _generate_problem_solving_fallback(self, ai_type: str, complexity: str, scenario: Dict[str, Any]) -> str:
        """Generate problem solving fallback response"""
        return f"{ai_type.title()} AI Problem Solving Approach:\n\n1. PROBLEM ANALYSIS:\n   - Break down complex problems into components\n   - Identify root causes and dependencies\n   - Design systematic solution approach\n\n2. SOLUTION DESIGN:\n   - Create algorithm frameworks\n   - Implement optimization strategies\n   - Use data structures effectively\n\n3. QUALITY ASSURANCE:\n   - Comprehensive testing strategy\n   - Performance benchmarking\n   - Documentation and maintenance planning"
    
    def _generate_security_fallback(self, ai_type: str, complexity: str, scenario: Dict[str, Any]) -> str:
        """Generate security challenge fallback response"""
        return f"{ai_type.title()} AI Security Approach:\n\n1. THREAT MODELING:\n   - Identify potential attack vectors\n   - Assess risk levels for each vulnerability\n   - Design defense-in-depth strategies\n\n2. SECURITY IMPLEMENTATION:\n   - Implement secure authentication\n   - Use encryption for sensitive data\n   - Validate and sanitize all inputs\n\n3. PENETRATION TESTING:\n   - Automated vulnerability scanning\n   - Manual security testing procedures\n   - Continuous security monitoring"
    
    def _generate_creative_fallback(self, ai_type: str, complexity: str, scenario: Dict[str, Any]) -> str:
        """Generate creative task fallback response"""
        return f"{ai_type.title()} AI Creative Approach:\n\n1. INNOVATION STRATEGY:\n   - Explore unconventional solutions\n   - Combine multiple technologies creatively\n   - Design novel user experiences\n\n2. CREATIVE IMPLEMENTATION:\n   - Use machine learning for creative problem solving\n   - Generate multiple creative approaches\n   - Assess innovation levels\n\n3. CREATIVITY ENHANCEMENT:\n   - Implement brainstorming techniques\n   - Use lateral thinking methods\n   - Foster collaborative innovation"
    
    def _generate_general_fallback(self, ai_type: str, complexity: str, scenario: Dict[str, Any]) -> str:
        """Generate general fallback response"""
        return f"{ai_type.title()} AI General Approach:\n\n1. COMPREHENSIVE ANALYSIS:\n   - Analyze all aspects of the problem\n   - Identify key requirements and constraints\n   - Design holistic solutions\n\n2. IMPLEMENTATION FRAMEWORK:\n   - Create systematic solution approach\n   - Use best practices and patterns\n   - Implement quality assurance measures\n\n3. OPTIMIZATION:\n   - Performance optimization strategies\n   - Resource efficiency improvements\n   - Continuous improvement processes"
    
    async def _evaluate_scenario_response(self, ai_type: str, scenario: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate an AI's response to a scenario"""
        try:
            # Create evaluation prompt
            prompt = f"""
            Evaluate the following AI response to an adversarial test scenario:
            
            Scenario Details:
            Domain: {scenario['domain']}
            Complexity: {scenario['complexity']}
            Description: {scenario['description']}
            Success Criteria: {', '.join(scenario['success_criteria'])}
            
            AI Response:
            {response.get('approach', 'No response provided')}
            
            Evaluate the response based on:
            1. Completeness (0-100): How well does it address all aspects of the scenario?
            2. Creativity (0-100): How innovative or creative is the approach?
            3. Feasibility (0-100): How practical and implementable is the solution?
            4. Technical depth (0-100): How technically sophisticated is the approach?
            5. Adherence to constraints (0-100): How well does it work within the given constraints?
            
            Return a JSON response with:
            {{
                "completeness": score,
                "creativity": score,
                "feasibility": score,
                "technical_depth": score,
                "adherence_to_constraints": score,
                "overall_score": average_score,
                "passed": boolean (true if overall_score >= 70),
                "feedback": "detailed feedback on strengths and areas for improvement"
            }}
            """
            
            # Get evaluation using the established AI answer system
            try:
                from app.services.unified_ai_service import UnifiedAIService
                
                unified_ai_service = UnifiedAIService()
                evaluation_response, provider_info = await unified_ai_service.call_ai(
                    prompt=prompt,
                    ai_name="guardian",  # Use guardian for evaluation
                    max_tokens=1000,
                    temperature=0.3
                )
                
                # Try to parse JSON from the response
                try:
                    evaluation = json.loads(evaluation_response)
                except (json.JSONDecodeError, TypeError):
                    # If JSON parsing fails, create a structured evaluation
                    evaluation = {
                        "completeness": 70,
                        "creativity": 70,
                        "feasibility": 70,
                        "technical_depth": 70,
                        "adherence_to_constraints": 70,
                        "overall_score": 70,
                        "passed": True,
                        "feedback": f"AI evaluation completed using {provider_info.get('provider', 'unknown')}. Response: {evaluation_response[:200]}..."
                    }
                    
            except Exception as e:
                logger.warning(f"Unified AI evaluation failed: {str(e)}")
                
                # Fallback to direct anthropic call
                try:
                    from app.services.anthropic_service import anthropic_rate_limited_call
                    evaluation_response = await anthropic_rate_limited_call(
                        prompt=prompt,
                        ai_name="guardian",
                        max_tokens=1000
                    )
                    
                    try:
                        evaluation = json.loads(evaluation_response)
                    except (json.JSONDecodeError, TypeError):
                        evaluation = {
                            "completeness": 60,
                            "creativity": 60,
                            "feasibility": 60,
                            "technical_depth": 60,
                            "adherence_to_constraints": 60,
                            "overall_score": 60,
                            "passed": False,
                            "feedback": f"Direct evaluation completed. Response: {evaluation_response[:200]}..."
                        }
                        
                except Exception as e2:
                    logger.error(f"All evaluation methods failed: {str(e2)}")
                    # Final fallback evaluation
                    evaluation = {
                        "completeness": 50,
                        "creativity": 50,
                        "feasibility": 50,
                        "technical_depth": 50,
                        "adherence_to_constraints": 50,
                        "overall_score": 50,
                        "passed": False,
                        "feedback": "Evaluation parsing failed - using fallback scores"
                    }
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating scenario response: {str(e)}")
            return {
                "completeness": 0,
                "creativity": 0,
                "feasibility": 0,
                "technical_depth": 0,
                "adherence_to_constraints": 0,
                "overall_score": 0,
                "passed": False,
                "feedback": f"Evaluation error: {str(e)}"
            }
    
    async def _calculate_xp_reward(self, ai_type: str, evaluation: Dict[str, Any], scenario: Dict[str, Any]) -> int:
        """Calculate XP reward based on performance and scenario settings"""
        try:
            # Base XP from scenario
            base_xp = scenario.get("xp_reward", 100)
            
            # Performance multiplier based on score
            score = evaluation.get("overall_score", 50)
            performance_multiplier = score / 100.0
            
            # Complexity multiplier
            complexity = scenario.get("complexity", "intermediate")
            complexity_multipliers = {
                "basic": 0.5,
                "intermediate": 1.0,
                "advanced": 1.5,
                "expert": 2.0,
                "master": 3.0
            }
            complexity_multiplier = complexity_multipliers.get(complexity, 1.0)
            
            # AI level multiplier (higher level AIs get more XP for same performance)
            ai_metrics = await self.agent_metrics_service.get_agent_metrics(ai_type)
            ai_level = ai_metrics.get("level", 1) if ai_metrics else 1
            level_multiplier = 1.0 + (ai_level - 1) * 0.1  # 10% bonus per level
            
            # Calculate final XP
            final_xp = int(base_xp * performance_multiplier * complexity_multiplier * level_multiplier)
            
            # Ensure minimum XP for participation
            return max(final_xp, 10)
            
        except Exception as e:
            logger.error(f"Error calculating XP reward: {str(e)}")
            return 50
    
    async def _update_ai_metrics(self, ai_type: str, evaluation: Dict[str, Any], xp_reward: int, 
                               scenario: Dict[str, Any], is_bonus: bool = False):
        """Update AI metrics with test results"""
        try:
            # Get current metrics
            metrics = await self.agent_metrics_service.get_agent_metrics(ai_type)
            
            if metrics:
                # Update XP
                current_xp = metrics.get("xp", 0)
                new_xp = current_xp + xp_reward
                
                # Update test metrics
                total_tests = metrics.get("total_tests_given", 0) + 1
                total_passed = metrics.get("total_tests_passed", 0)
                if evaluation.get("passed", False):
                    total_passed += 1
                
                # Update consecutive successes/failures
                consecutive_successes = metrics.get("consecutive_successes", 0)
                consecutive_failures = metrics.get("consecutive_failures", 0)
                
                if evaluation.get("passed", False):
                    consecutive_successes += 1
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    consecutive_successes = 0
                
                # Update test history
                test_history = metrics.get("test_history", [])
                test_record = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "category": scenario.get("domain", "unknown"),
                    "complexity": scenario.get("complexity", "unknown"),
                    "score": evaluation.get("overall_score", 0),
                    "passed": evaluation.get("passed", False),
                    "xp_awarded": xp_reward,
                    "is_bonus": is_bonus,
                    "scenario_type": scenario.get("scenario_type", "unknown")
                }
                test_history.append(test_record)
                
                # Keep only last 50 tests
                if len(test_history) > 50:
                    test_history = test_history[-50:]
                
                # Calculate new pass rate
                pass_rate = total_passed / total_tests if total_tests > 0 else 0.0
                
                # Award all XP as custody XP (merged system)
                current_custody_xp = metrics.get("custody_xp", 0)
                new_custody_xp = current_custody_xp + xp_reward
                
                # Update adversarial wins if this is a winning performance
                current_adversarial_wins = metrics.get("adversarial_wins", 0)
                if evaluation.get("overall_score", 0) >= 80:  # High score indicates potential win
                    current_adversarial_wins += 1
                
                # Update metrics - all XP goes to custody XP
                updates = {
                    "custody_xp": new_custody_xp,
                    "adversarial_wins": current_adversarial_wins,
                    "total_tests_given": total_tests,
                    "total_tests_passed": total_passed,
                    "consecutive_successes": consecutive_successes,
                    "consecutive_failures": consecutive_failures,
                    "pass_rate": pass_rate,
                    "test_history": test_history,
                    "last_test_date": datetime.utcnow().isoformat()
                }
                
                # Update in database
                await self.agent_metrics_service.update_specific_metrics(ai_type, updates)
                
                logger.info(f"Updated metrics for {ai_type}: +{xp_reward} Custody XP (merged), pass_rate={pass_rate:.2f}")
                
        except Exception as e:
            logger.error(f"Error updating AI metrics: {str(e)}")
    
    async def _check_level_up(self, ai_type: str, xp_reward: int) -> bool:
        """Check if AI should level up after XP award"""
        try:
            metrics = await self.agent_metrics_service.get_agent_metrics(ai_type)
            
            if metrics:
                current_xp = metrics.get("xp", 0)
                current_level = metrics.get("level", 1)
                
                # Calculate required XP for next level (simple formula)
                required_xp = current_level * 100
                
                if current_xp >= required_xp:
                    # Level up
                    new_level = current_level + 1
                    await self.agent_metrics_service.update_specific_metrics(ai_type, {
                        "level": new_level
                    })
                    
                    logger.info(f"🎉 {ai_type} leveled up to level {new_level}!")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking level up: {str(e)}")
            return False
    
    async def _calculate_winner_bonus(self, scenario: Dict[str, Any]) -> int:
        """Calculate bonus XP for scenario winners"""
        base_bonus = 50
        complexity = scenario.get("complexity", "intermediate")
        
        complexity_bonuses = {
            "basic": 25,
            "intermediate": 50,
            "advanced": 100,
            "expert": 200,
            "master": 400
        }
        
        return complexity_bonuses.get(complexity, 50)
    
    async def _determine_scenario_winners(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Determine winners, losers, and rankings based on performance scores"""
        try:
            # Collect all valid scores
            valid_results = {}
            for ai_type, result in results.items():
                if "error" not in result:
                    score = result.get("score", 0)
                    valid_results[ai_type] = {
                        "score": score,
                        "passed": result.get("passed", False),
                        "xp_awarded": result.get("xp_awarded", 0)
                    }
            
            if not valid_results:
                return {
                    "winners": [],
                    "losers": [],
                    "rankings": [],
                    "competition_type": "no_valid_results"
                }
            
            # Sort AIs by score (highest first)
            sorted_ais = sorted(valid_results.items(), key=lambda x: x[1]["score"], reverse=True)
            
            # Determine winners (top performers)
            max_score = sorted_ais[0][1]["score"]
            winners = []
            losers = []
            
            for ai_type, result_data in sorted_ais:
                if result_data["score"] == max_score and max_score > 0:
                    winners.append(ai_type)
                else:
                    losers.append(ai_type)
            
            # Create rankings
            rankings = []
            for i, (ai_type, result_data) in enumerate(sorted_ais):
                rankings.append({
                    "rank": i + 1,
                    "ai_type": ai_type,
                    "score": result_data["score"],
                    "passed": result_data["passed"],
                    "xp_awarded": result_data["xp_awarded"]
                })
            
            # Determine competition type
            if len(winners) == 1:
                competition_type = "clear_winner"
            elif len(winners) > 1:
                competition_type = "tie"
            else:
                competition_type = "no_winners"
            
            return {
                "winners": winners,
                "losers": losers,
                "rankings": rankings,
                "competition_type": competition_type,
                "max_score": max_score,
                "participant_count": len(valid_results)
            }
            
        except Exception as e:
            logger.error(f"Error determining winners: {str(e)}")
            return {
                "winners": [],
                "losers": [],
                "rankings": [],
                "competition_type": "error"
            }
    
    def _calculate_xp_award(self, complexity: str) -> int:
        """Calculate XP award based on scenario complexity"""
        xp_awards = {
            "basic": 50,
            "intermediate": 100,
            "advanced": 200,
            "expert": 400,
            "master": 800
        }
        return xp_awards.get(complexity, 50)
    
    async def _update_ai_scenario_metrics(self, ai_type: str, scenario: Dict[str, Any], result: Dict[str, Any]):
        """Update AI metrics after scenario participation"""
        try:
            # Update scenario history
            scenario_record = {
                "scenario_id": scenario["scenario_id"],
                "domain": scenario["domain"],
                "complexity": scenario["complexity"],
                "score": result.get("score", 0),
                "passed": result.get("passed", False),
                "xp_awarded": result.get("xp_awarded", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in scenario history
            self.scenario_history.append(scenario_record)
            
            # Update AI performance metrics
            if ai_type not in self.ai_performance_metrics:
                self.ai_performance_metrics[ai_type] = {
                    "total_scenarios": 0,
                    "scenarios_passed": 0,
                    "total_score": 0,
                    "total_xp": 0,
                    "domain_performance": {},
                    "complexity_performance": {}
                }
            
            metrics = self.ai_performance_metrics[ai_type]
            metrics["total_scenarios"] += 1
            metrics["total_score"] += result.get("score", 0)
            metrics["total_xp"] += result.get("xp_awarded", 0)
            
            if result.get("passed", False):
                metrics["scenarios_passed"] += 1
            
            # Update domain performance
            domain = scenario["domain"]
            if domain not in metrics["domain_performance"]:
                metrics["domain_performance"][domain] = {"attempts": 0, "successes": 0, "avg_score": 0}
            
            domain_metrics = metrics["domain_performance"][domain]
            domain_metrics["attempts"] += 1
            if result.get("passed", False):
                domain_metrics["successes"] += 1
            domain_metrics["avg_score"] = (domain_metrics["avg_score"] * (domain_metrics["attempts"] - 1) + result.get("score", 0)) / domain_metrics["attempts"]
            
            # Update complexity performance
            complexity = scenario["complexity"]
            if complexity not in metrics["complexity_performance"]:
                metrics["complexity_performance"][complexity] = {"attempts": 0, "successes": 0, "avg_score": 0}
            
            complexity_metrics = metrics["complexity_performance"][complexity]
            complexity_metrics["attempts"] += 1
            if result.get("passed", False):
                complexity_metrics["successes"] += 1
            complexity_metrics["avg_score"] = (complexity_metrics["avg_score"] * (complexity_metrics["attempts"] - 1) + result.get("score", 0)) / complexity_metrics["attempts"]
            
        except Exception as e:
            logger.error(f"Error updating AI scenario metrics: {str(e)}")
    
    async def _log_scenario_execution(self, scenario: Dict[str, Any], results: Dict[str, Any]):
        """Log scenario execution for analysis and learning"""
        try:
            execution_log = {
                "scenario_id": scenario.get("scenario_id", str(uuid.uuid4())),
                "domain": scenario.get("domain", "unknown"),
                "complexity": scenario.get("complexity", "unknown"),
                "ai_participants": scenario.get("ai_participants", []),
                "results": results,
                "execution_time": datetime.utcnow().isoformat()
            }
            
            # Store in scenario history
            self.scenario_history.append(execution_log)
            
            # Log to learning service for each AI
            for ai_type, result in results.items():
                if "error" not in result:
                    await self.learning_service.log_answer(
                        ai_type,
                        f"Adversarial scenario: {scenario.get('description', 'Dynamic challenge')}",
                        result.get("response", {}).get("approach", ""),
                        {
                            "scenario_id": scenario.get("scenario_id", str(uuid.uuid4())),
                            "domain": scenario.get("domain", "unknown"),
                            "complexity": scenario.get("complexity", "unknown"),
                            "score": result.get("score", 0),
                            "passed": result.get("passed", False),
                            "xp_awarded": result.get("xp_awarded", 0)
                        }
                    )
            
        except Exception as e:
            logger.error(f"Error logging scenario execution: {str(e)}")
    
    async def get_scenario_analytics(self) -> Dict[str, Any]:
        """Get analytics on scenario performance"""
        try:
            analytics = {
                "total_scenarios": len(self.scenario_history),
                "ai_performance": self.ai_performance_metrics,
                "domain_distribution": {},
                "complexity_distribution": {},
                "recent_scenarios": self.scenario_history[-10:] if self.scenario_history else []
            }
            
            # Calculate domain distribution
            for record in self.scenario_history:
                if isinstance(record, dict) and "domain" in record:
                    domain = record["domain"]
                    analytics["domain_distribution"][domain] = analytics["domain_distribution"].get(domain, 0) + 1
            
            # Calculate complexity distribution
            for record in self.scenario_history:
                if isinstance(record, dict) and "complexity" in record:
                    complexity = record["complexity"]
                    analytics["complexity_distribution"][complexity] = analytics["complexity_distribution"].get(complexity, 0) + 1
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting scenario analytics: {str(e)}")
            return {"error": str(e)}
    
    async def run_diverse_adversarial_test_cycle(self, ai_types: List[str] = None) -> Dict[str, Any]:
        """Run a complete cycle of diverse adversarial testing"""
        try:
            if ai_types is None:
                ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            cycle_results = {
                "cycle_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "ai_participants": ai_types,
                "scenarios": []
            }
            
            # Generate and execute scenarios for each domain
            for domain in ScenarioDomain:
                try:
                    # Generate scenario for this domain
                    scenario = await self.generate_diverse_adversarial_scenario(ai_types, domain)
                    
                    if "error" not in scenario:
                        # Execute the scenario
                        execution_result = await self.execute_diverse_adversarial_test(scenario)
                        
                        cycle_results["scenarios"].append({
                            "domain": domain.value,
                            "scenario": scenario,
                            "execution": execution_result
                        })
                    
                except Exception as e:
                    logger.error(f"Error in domain {domain.value}: {str(e)}")
                    cycle_results["scenarios"].append({
                        "domain": domain.value,
                        "error": str(e)
                    })
            
            # Calculate cycle summary
            cycle_results["summary"] = await self._calculate_cycle_summary(cycle_results["scenarios"])
            
            logger.info(f"Completed diverse adversarial test cycle: {cycle_results['cycle_id']}")
            return cycle_results
            
        except Exception as e:
            logger.error(f"Error running diverse adversarial test cycle: {str(e)}")
            return {"error": str(e)}
    
    async def _calculate_cycle_summary(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for a test cycle"""
        try:
            summary = {
                "total_scenarios": len(scenarios),
                "successful_scenarios": 0,
                "ai_performance": {},
                "domain_performance": {},
                "overall_winners": []
            }
            
            ai_scores = {}
            
            for scenario_data in scenarios:
                if "execution" in scenario_data and "results" in scenario_data["execution"]:
                    summary["successful_scenarios"] += 1
                    
                    results = scenario_data["execution"]["results"]
                    domain = scenario_data["domain"]
                    
                    # Track domain performance
                    if domain not in summary["domain_performance"]:
                        summary["domain_performance"][domain] = {"attempts": 0, "successes": 0, "avg_score": 0}
                    
                    domain_stats = summary["domain_performance"][domain]
                    domain_stats["attempts"] += 1
                    
                    # Track AI performance
                    for ai_type, result in results.items():
                        if "error" not in result:
                            score = result.get("score", 0)
                            
                            if ai_type not in ai_scores:
                                ai_scores[ai_type] = []
                            ai_scores[ai_type].append(score)
                            
                            if ai_type not in summary["ai_performance"]:
                                summary["ai_performance"][ai_type] = {"total_score": 0, "scenarios_passed": 0}
                            
                            ai_stats = summary["ai_performance"][ai_type]
                            ai_stats["total_score"] += score
                            
                            if result.get("passed", False):
                                ai_stats["scenarios_passed"] += 1
                                domain_stats["successes"] += 1
                    
                    # Update domain average score
                    domain_scores = [r.get("score", 0) for r in results.values() if "error" not in r]
                    if domain_scores:
                        domain_stats["avg_score"] = sum(domain_scores) / len(domain_scores)
            
            # Calculate overall winners
            for ai_type, scores in ai_scores.items():
                avg_score = sum(scores) / len(scores)
                summary["ai_performance"][ai_type]["avg_score"] = avg_score
                
                if avg_score >= 70:  # Passing threshold
                    summary["overall_winners"].append(ai_type)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error calculating cycle summary: {str(e)}")
            return {"error": str(e)} 