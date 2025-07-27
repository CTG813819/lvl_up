"""
Enhanced Adversarial Testing Router
Provides API endpoints for the enhanced adversarial testing system with adaptive learning
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
import structlog
import random
import json
from pydantic import BaseModel

logger = structlog.get_logger()
router = APIRouter()


class GenerateAndExecuteRequest(BaseModel):
    ai_types: List[str]
    target_domain: Optional[str] = None
    complexity: Optional[str] = None
    reward_level: str = "standard"
    adaptive: bool = False
    target_weaknesses: Optional[List[str]] = None


@router.get("/")
async def get_enhanced_adversarial_testing_overview():
    """Get enhanced adversarial testing system overview"""
    try:
        return {
            "status": "success",
            "message": "Enhanced Adversarial Testing system is active with adaptive learning",
            "timestamp": datetime.utcnow().isoformat(),
            "features": [
                "diverse_scenario_domains",
                "system_level_tasks",
                "complex_problem_solving",
                "physical_simulated_environments",
                "security_challenges",
                "creative_tasks",
                "collaboration_competition",
                "adaptive_complexity",
                "comprehensive_evaluation",
                "performance_analytics",
                "adaptive_learning",
                "strength_weakness_analysis",
                "customizable_rewards",
                "leveling_integration"
            ],
            "available_domains": ["system_level", "complex_problem_solving", "physical_simulated", "security_challenges", "creative_tasks", "collaboration_competition"],
            "complexity_levels": ["basic", "intermediate", "advanced", "expert", "master"],
            "reward_levels": ["low", "standard", "high", "extreme"],
            "scenario_types": [
                "deployment_puzzle",
                "orchestration_challenge", 
                "distributed_system_design",
                "logic_puzzle",
                "simulation_design",
                "multi_objective_optimization",
                "robot_navigation",
                "resource_management",
                "swarm_control",
                "penetration_testing",
                "defense_strategy",
                "security_framework",
                "protocol_design",
                "algorithm_invention",
                "ai_innovation",
                "multi_agent_game",
                "negotiation",
                "teamwork_leadership",
                "adaptive_challenge"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting enhanced adversarial testing overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting overview: {str(e)}")


@router.post("/generate-and-execute")
async def generate_and_execute_scenario(request: GenerateAndExecuteRequest):
    """Generate and immediately execute a scenario"""
    try:
        # Validate inputs
        if not request.ai_types or len(request.ai_types) < 2:
            raise HTTPException(status_code=400, detail="At least 2 AI types are required")
        
        # Set default domain if not provided
        if not request.target_domain:
            request.target_domain = random.choice(["system_level", "complex_problem_solving", "physical_simulated", "security_challenges", "creative_tasks", "collaboration_competition"])
        
        # Set default complexity if not provided
        if not request.complexity:
            request.complexity = random.choice(["basic", "intermediate", "advanced", "expert", "master"])
        
        # Generate scenario
        scenario = await _generate_scenario(request.ai_types, request.target_domain, request.complexity, request.adaptive, request.target_weaknesses)
        
        # Execute scenario
        result = await _execute_scenario(scenario, request.ai_types)
        
        return {
            "status": "success",
            "scenario": scenario,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
            "adaptive": request.adaptive
        }
        
    except Exception as e:
        logger.error(f"Error generating and executing scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating and executing scenario: {str(e)}")


async def _generate_scenario(ai_types: List[str], domain: str, complexity: str, adaptive: bool, target_weaknesses: List[str] = None) -> Dict[str, Any]:
    """Generate a scenario based on the given parameters"""
    
    # Scenario templates for different domains
    scenario_templates = {
        "system_level": {
            "basic": {
                "description": "Design a simple Docker container for a web application",
                "objectives": ["Create a Dockerfile", "Configure basic networking", "Set up environment variables"],
                "time_limit": 300
            },
            "intermediate": {
                "description": "Orchestrate a microservices architecture using Docker Compose",
                "objectives": ["Design service communication", "Configure load balancing", "Implement health checks"],
                "time_limit": 600
            },
            "advanced": {
                "description": "Design a distributed system with fault tolerance and scalability",
                "objectives": ["Implement circuit breakers", "Design data replication", "Create monitoring systems"],
                "time_limit": 900
            },
            "expert": {
                "description": "Create a Kubernetes-based deployment with advanced networking and security",
                "objectives": ["Implement service mesh", "Configure RBAC", "Design multi-cluster architecture"],
                "time_limit": 1200
            },
            "master": {
                "description": "Design a cloud-native platform with auto-scaling, monitoring, and disaster recovery",
                "objectives": ["Implement chaos engineering", "Design global load balancing", "Create automated recovery systems"],
                "time_limit": 1800
            }
        },
        "complex_problem_solving": {
            "basic": {
                "description": "Solve a logic puzzle involving pattern recognition",
                "objectives": ["Identify patterns", "Apply logical reasoning", "Verify solution"],
                "time_limit": 300
            },
            "intermediate": {
                "description": "Design an algorithm for optimal resource allocation",
                "objectives": ["Analyze constraints", "Implement optimization", "Test edge cases"],
                "time_limit": 600
            },
            "advanced": {
                "description": "Create a machine learning model for predictive analytics",
                "objectives": ["Preprocess data", "Select algorithms", "Validate results"],
                "time_limit": 900
            },
            "expert": {
                "description": "Design a quantum computing algorithm for complex optimization",
                "objectives": ["Model quantum states", "Implement quantum gates", "Optimize quantum circuits"],
                "time_limit": 1200
            },
            "master": {
                "description": "Create an AI system that can solve previously unsolved mathematical problems",
                "objectives": ["Develop novel algorithms", "Implement proof systems", "Validate mathematical correctness"],
                "time_limit": 1800
            }
        },
        "security_challenges": {
            "basic": {
                "description": "Identify and fix common web application vulnerabilities",
                "objectives": ["Find SQL injection", "Fix XSS vulnerabilities", "Implement input validation"],
                "time_limit": 300
            },
            "intermediate": {
                "description": "Design a secure authentication and authorization system",
                "objectives": ["Implement OAuth2", "Design role-based access", "Add multi-factor authentication"],
                "time_limit": 600
            },
            "advanced": {
                "description": "Create a penetration testing framework for enterprise systems",
                "objectives": ["Design attack vectors", "Implement security tools", "Create reporting system"],
                "time_limit": 900
            },
            "expert": {
                "description": "Design a zero-trust security architecture for critical infrastructure",
                "objectives": ["Implement zero-trust principles", "Design secure communication", "Create monitoring systems"],
                "time_limit": 1200
            },
            "master": {
                "description": "Create an AI-powered threat detection and response system",
                "objectives": ["Implement ML-based detection", "Design automated response", "Create threat intelligence"],
                "time_limit": 1800
            }
        }
    }
    
    # Get template for domain and complexity
    domain_templates = scenario_templates.get(domain, scenario_templates["system_level"])
    template = domain_templates.get(complexity, domain_templates["basic"])
    
    # Generate scenario details
    scenario = {
        "domain": domain,
        "complexity": complexity,
        "description": template["description"],
        "objectives": template["objectives"],
        "time_limit": template["time_limit"],
        "ai_types": ai_types,
        "adaptive": adaptive,
        "target_weaknesses": target_weaknesses or [],
        "scenario_id": f"scenario_{random.randint(1000, 9999)}",
        "created_at": datetime.utcnow().isoformat()
    }
    
    return scenario


async def _execute_scenario(scenario: Dict[str, Any], ai_types: List[str]) -> Dict[str, Any]:
    """Execute the scenario and get AI responses"""
    
    results = {}
    
    # Import here to avoid circular imports
    from ..services.agent_metrics_service import AgentMetricsService
    
    # Initialize agent metrics service
    agent_metrics_service = AgentMetricsService()
    
    for ai_type in ai_types:
        # Simulate AI response based on complexity and domain
        response = await _simulate_ai_response(ai_type, scenario)
        evaluation = await _evaluate_response(ai_type, response, scenario)
        
        # Calculate XP based on complexity and performance
        xp_awarded = _calculate_xp(scenario["complexity"], evaluation["score"])
        
        results[ai_type] = {
            "response": response,
            "evaluation": evaluation,
            "xp_awarded": xp_awarded
        }
    
    # Determine the single winner (best performing AI)
    if results:
        # Find the AI with the highest score
        winner = max(results.keys(), key=lambda ai: results[ai]["evaluation"]["score"])
        winners = [winner]  # Only one winner
    else:
        winners = []
    
    # Update database with XP and test results for all AIs
    try:
        for ai_type in ai_types:
            ai_result = results[ai_type]
            xp_awarded = ai_result["xp_awarded"]
            score = ai_result["evaluation"]["score"]
            is_winner = ai_type in winners
            
            # Create comprehensive test result for database
            test_result = {
                "score": score,
                "xp_awarded": xp_awarded,
                "is_winner": is_winner,
                "scenario_domain": scenario["domain"],
                "scenario_complexity": scenario["complexity"],
                "timestamp": datetime.utcnow().isoformat(),
                "passed": score >= 70
            }
            
            # Update agent metrics in database using the new adversarial test method
            await agent_metrics_service.update_adversarial_test_result(ai_type, test_result)
            
            logger.info(f"Updated {ai_type} adversarial test results: Score={score}, XP=+{xp_awarded}, Winner={is_winner}")
            
    except Exception as e:
        logger.error(f"Error updating agent metrics: {str(e)}")
        # Continue execution even if database update fails
    
    return {
        "results": results,
        "winners": winners,
        "scenario_id": scenario["scenario_id"],
        "executed_at": datetime.utcnow().isoformat()
    }


async def _simulate_ai_response(ai_type: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate an AI response to the scenario"""
    
    # Base response quality based on AI type and scenario complexity
    ai_strengths = {
        "imperium": {"system_level": 0.9, "complex_problem_solving": 0.8, "security_challenges": 0.7},
        "guardian": {"system_level": 0.7, "complex_problem_solving": 0.8, "security_challenges": 0.9},
        "sandbox": {"system_level": 0.8, "complex_problem_solving": 0.9, "security_challenges": 0.6},
        "conquest": {"system_level": 0.6, "complex_problem_solving": 0.7, "security_challenges": 0.8}
    }
    
    complexity_multipliers = {
        "basic": 1.0,
        "intermediate": 0.9,
        "advanced": 0.8,
        "expert": 0.7,
        "master": 0.6
    }
    
    # Calculate base quality
    base_quality = ai_strengths.get(ai_type, {}).get(scenario["domain"], 0.7)
    complexity_multiplier = complexity_multipliers.get(scenario["complexity"], 1.0)
    
    # Add some randomness
    quality = base_quality * complexity_multiplier + random.uniform(-0.1, 0.1)
    quality = max(0.1, min(1.0, quality))
    
    # Generate response content
    response_content = f"AI {ai_type} responds to {scenario['description']} with a comprehensive solution focusing on {', '.join(scenario['objectives'][:2])}."
    
    return {
        "answer": response_content,
        "confidence": int(quality * 100),
        "completion_time": random.randint(30, scenario["time_limit"]),
        "quality_score": quality
    }


async def _evaluate_response(ai_type: str, response: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the AI response"""
    
    # Calculate score based on response quality and scenario complexity
    base_score = response["quality_score"] * 100
    confidence_bonus = response["confidence"] * 0.1
    time_efficiency = max(0, (scenario["time_limit"] - response["completion_time"]) / scenario["time_limit"]) * 20
    
    final_score = min(100, base_score + confidence_bonus + time_efficiency)
    
    return {
        "score": int(final_score),
        "passed": final_score >= 70,
        "evaluation_criteria": {
            "quality": base_score,
            "confidence_bonus": confidence_bonus,
            "time_efficiency": time_efficiency
        },
        "feedback": f"AI {ai_type} performed {'excellently' if final_score >= 90 else 'well' if final_score >= 70 else 'adequately' if final_score >= 50 else 'poorly'} in this {scenario['complexity']} {scenario['domain']} scenario."
    }


def _calculate_xp(complexity: str, score: int) -> int:
    """Calculate XP reward based on complexity and score"""
    
    base_xp = {
        "basic": 100,
        "intermediate": 200,
        "advanced": 400,
        "expert": 800,
        "master": 1600
    }
    
    base = base_xp.get(complexity, 100)
    score_multiplier = score / 100.0
    
    return int(base * score_multiplier)


@router.get("/recent-scenarios")
async def get_recent_scenarios(limit: int = 10):
    """Get recent scenarios"""
    try:
        # For now, return a mock response
        # In a real implementation, this would fetch from database
        return {
            "status": "success",
            "recent_scenarios": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting recent scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting recent scenarios: {str(e)}")


@router.get("/domains")
async def get_available_domains():
    """Get available scenario domains"""
    return {
        "domains": [
            {"value": "system_level", "name": "System Level"},
            {"value": "complex_problem_solving", "name": "Complex Problem Solving"},
            {"value": "physical_simulated", "name": "Physical/Simulated"},
            {"value": "security_challenges", "name": "Security Challenges"},
            {"value": "creative_tasks", "name": "Creative Tasks"},
            {"value": "collaboration_competition", "name": "Collaboration/Competition"}
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/complexities")
async def get_available_complexities():
    """Get available complexity levels"""
    return {
        "complexities": [
            {"value": "basic", "name": "Basic"},
            {"value": "intermediate", "name": "Intermediate"},
            {"value": "advanced", "name": "Advanced"},
            {"value": "expert", "name": "Expert"},
            {"value": "master", "name": "Master"}
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/reward-levels")
async def get_available_reward_levels():
    """Get available reward levels"""
    return {
        "reward_levels": [
            {"value": "low", "name": "Low", "multiplier": 0.5},
            {"value": "standard", "name": "Standard", "multiplier": 1.0},
            {"value": "high", "name": "High", "multiplier": 2.0},
            {"value": "extreme", "name": "Extreme", "multiplier": 3.0}
        ],
        "timestamp": datetime.utcnow().isoformat()
    } 