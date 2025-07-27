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
        await enhanced_testing_service.initialize()
        print("✅ Enhanced adversarial testing service initialized")
        
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
        if not request.ai_types or len(request.ai_types) < 2:
            raise HTTPException(status_code=400, detail="At least 2 AI types are required")
        
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
        
        # Generate scenario using the enhanced service
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
                complexity_enum
            )
        
        # Execute scenario
        result = await enhanced_testing_service.execute_diverse_adversarial_test(scenario)
        
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Enhanced Adversarial Testing",
        "port": 8001,
        "timestamp": datetime.utcnow().isoformat()
    }

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