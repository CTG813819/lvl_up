#!/usr/bin/env python3
"""
Standalone Enhanced Adversarial Testing Service
Runs on port 8001 for enhanced adversarial testing functionality
"""

import uvicorn
import asyncio
import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from datetime import datetime
import structlog
import random
import json
from pydantic import BaseModel

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import init_database
from app.services.agent_metrics_service import AgentMetricsService
from app.services.enhanced_adversarial_testing_service import EnhancedAdversarialTestingService

logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="Enhanced Adversarial Testing Service",
    description="Standalone service for enhanced adversarial testing on port 8001",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class GenerateAndExecuteRequest(BaseModel):
    ai_types: List[str]
    target_domain: Optional[str] = None
    complexity: Optional[str] = None
    reward_level: str = "standard"
    adaptive: bool = False
    target_weaknesses: Optional[List[str]] = None

# Global service instances
enhanced_testing_service = None
agent_metrics_service = None

async def generate_simple_ai_responses(scenario: Dict[str, Any], ai_types: List[str]) -> Dict[str, Any]:
    """Generate simple AI responses for the scenario"""
    import random
    
    results = {}
    scenario_desc = scenario.get("description", "system challenge")
    domain = scenario.get("domain", "system_level")
    complexity = scenario.get("complexity", "basic")
    
    # Generate scores and XP for each AI
    for ai_type in ai_types:
        # Generate varied scores based on AI type and scenario
        base_score = 70 + (hash(ai_type + domain) % 30)  # Vary scores based on AI type and domain
        score = base_score + random.randint(-5, 5)  # Add some randomness
        
        # Calculate XP reward based on score and complexity
        complexity_multiplier = {"basic": 1, "intermediate": 1.2, "advanced": 1.5, "expert": 2.0, "master": 2.5}.get(complexity, 1)
        xp_reward = int(score * complexity_multiplier)
        
        # Determine if AI passed (score > 60)
        passed = score > 60
        
        # Generate simple response text
        response_text = f"{ai_type.capitalize()} completed the {domain} challenge with a score of {score}."
        
        results[ai_type] = {
            "score": score,
            "passed": passed,
            "xp_awarded": xp_reward,
            "level_up": xp_reward > 100,  # Level up if XP > 100
            "ai_type": ai_type,
            "response_text": response_text,
            "execution_time": "fast",
            "domain": domain,
            "complexity": complexity
        }
    
    # Determine winners and losers
    sorted_results = sorted(results.items(), key=lambda x: x[1]["score"], reverse=True)
    winners = [sorted_results[0][0]] if len(sorted_results) > 0 else []
    losers = [ai for ai in ai_types if ai not in winners]
    
    # Create rankings
    rankings = [{"ai_type": ai, "rank": i+1, "score": data["score"]} for i, (ai, data) in enumerate(sorted_results)]
    
    return {
        "scenario": scenario,
        "results": results,
        "competition_results": {
            "winners": winners,
            "losers": losers,
            "rankings": rankings
        },
        "timestamp": datetime.utcnow().isoformat(),
        "adaptive": scenario.get("adaptive", False),
        "fast_mode": True
    }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global enhanced_testing_service, agent_metrics_service
    
    try:
        print("🔧 Initializing database...")
        await init_database()
        print("✅ Database initialized successfully")
        
        print("🔧 Initializing agent metrics service...")
        agent_metrics_service = AgentMetricsService()
        await agent_metrics_service.initialize()
        print("✅ Agent metrics service initialized")
        
        print("🔧 Initializing enhanced adversarial testing service...")
        enhanced_testing_service = EnhancedAdversarialTestingService()
        await enhanced_testing_service.initialize(fast_mode=True)
        print("✅ Enhanced adversarial testing service initialized (fast mode)")
        
        print("🚀 Enhanced Adversarial Testing Service ready on port 8001")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.get("/")
async def get_enhanced_adversarial_testing_overview():
    """Get enhanced adversarial testing system overview"""
    try:
        return {
            "status": "success",
            "message": "Enhanced Adversarial Testing system is active with adaptive learning",
            "timestamp": datetime.utcnow().isoformat(),
            "port": 8001,
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

@app.post("/generate-and-execute")
async def generate_and_execute_scenario(request: GenerateAndExecuteRequest):
    """Generate and immediately execute a scenario"""
    try:
        if not enhanced_testing_service:
            raise HTTPException(status_code=503, detail="Enhanced testing service not initialized")
        
        # Validate inputs
        if not request.ai_types or len(request.ai_types) < 1:
            raise HTTPException(status_code=400, detail="At least 1 AI type is required")
        
        # Set default domain if not provided
        if not request.target_domain:
            request.target_domain = random.choice(["system_level", "complex_problem_solving", "physical_simulated", "security_challenges", "creative_tasks", "collaboration_competition"])
        
        # Set default complexity if not provided
        if not request.complexity:
            request.complexity = random.choice(["basic", "intermediate", "advanced", "expert", "master"])
        
        # Convert string values to enum objects
        from app.services.enhanced_adversarial_testing_service import ScenarioDomain, ScenarioComplexity
        
        target_domain_enum = None
        if request.target_domain:
            try:
                target_domain_enum = ScenarioDomain(request.target_domain)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid domain: {request.target_domain}")
        
        complexity_enum = None
        if request.complexity:
            try:
                complexity_enum = ScenarioComplexity(request.complexity)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid complexity: {request.complexity}")
        
        # Generate scenario using the enhanced service (fast mode)
        if request.adaptive:
            scenario = await enhanced_testing_service.generate_adaptive_scenario(
                request.ai_types, 
                request.target_weaknesses, 
                request.reward_level
            )
        else:
            scenario = await enhanced_testing_service.generate_diverse_adversarial_scenario(
                request.ai_types,
                target_domain_enum,
                complexity_enum,
                fast_mode=True
            )
        
        # Execute scenario with simple AI responses
        result = await generate_simple_ai_responses(scenario, request.ai_types)
        
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

@app.get("/recent-scenarios")
async def get_recent_scenarios(limit: int = 10):
    """Get recent scenarios"""
    try:
        if not enhanced_testing_service:
            raise HTTPException(status_code=503, detail="Enhanced testing service not initialized")
        
        # Get scenario analytics which includes recent scenarios
        analytics = await enhanced_testing_service.get_scenario_analytics()
        
        return {
            "status": "success",
            "recent_scenarios": analytics.get("recent_scenarios", []),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting recent scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting recent scenarios: {str(e)}")

@app.get("/domains")
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

@app.get("/complexities")
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

@app.get("/reward-levels")
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

@app.post("/activate")
async def activate_service(request: Dict[str, Any] = Body(...)):
    """Activate the enhanced adversarial testing service"""
    try:
        action = request.get('action', 'start')
        
        if action == 'start':
            # Service is already running, just return success
            return {
                "status": "success",
                "message": "Enhanced adversarial testing service is already running on port 8001",
                "service_status": "running",
                "port": 8001
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
            
    except Exception as e:
        logger.error(f"Error in activation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Enhanced Adversarial Testing",
        "port": 8001,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint for debugging"""
    return {
        "status": "success",
        "message": "Enhanced adversarial testing service is responding",
        "timestamp": datetime.utcnow().isoformat(),
        "port": 8001
    }

@app.post("/test-generate")
async def test_generate_scenario():
    """Simple test scenario generation for debugging"""
    try:
        return {
            "status": "success",
            "scenario": {
                "id": "test-scenario-001",
                "domain": "system_level",
                "complexity": "basic",
                "description": "Test scenario for debugging",
                "objectives": ["Test service connectivity"],
                "constraints": ["Time limit: 30 seconds"],
                "success_criteria": ["Service responds within timeout"],
                "time_limit": 30,
                "required_skills": ["basic_testing"],
                "scenario_type": "debug_test"
            },
            "result": {
                "status": "completed",
                "message": "Test scenario completed successfully",
                "timestamp": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in test generate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test generate error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Adversarial Testing Service on Port 8001...")
    print("=================================================================")
    
    uvicorn.run(
        "standalone_enhanced_adversarial_testing:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    ) 