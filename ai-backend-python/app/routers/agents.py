"""
AI Agents Router - Endpoints for autonomous AI agents
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
import structlog
from datetime import datetime

from app.services.ai_agent_service import AIAgentService
from app.services.background_service import BackgroundService
from app.services.ai_learning_service import AILearningService
from app.services.ai_growth_service import AIGrowthService
from app.services.github_service import GitHubService
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()
router = APIRouter()

ai_agent_service = AIAgentService()
background_service = BackgroundService()
ai_learning_service = AILearningService()
ai_growth_service = AIGrowthService()
github_service = GitHubService()


@router.post("/run-all")
async def run_all_agents():
    """Run all AI agents manually"""
    try:
        logger.info("🚀 Manual trigger: Running all AI agents")
        result = await ai_agent_service.run_all_agents()
        return result
    except Exception as e:
        logger.error("Error running all agents", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run/{agent_type}")
async def run_specific_agent(agent_type: str):
    """Run a specific AI agent"""
    try:
        agent_type = agent_type.lower()
        
        if agent_type == "imperium":
            result = await ai_agent_service.run_imperium_agent()
        elif agent_type == "guardian":
            result = await ai_agent_service.run_guardian_agent()
        elif agent_type == "sandbox":
            result = await ai_agent_service.run_sandbox_agent()
        elif agent_type == "conquest":
            result = await ai_agent_service.run_conquest_agent()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
        
        logger.info(f"🚀 Manual trigger: Running {agent_type} agent")
        return result
    except Exception as e:
        logger.error(f"Error running {agent_type} agent", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/autonomous/start")
async def start_autonomous_cycle():
    """Start the autonomous AI cycle"""
    try:
        logger.info("🤖 Starting autonomous AI cycle")
        await background_service.start_autonomous_cycle()
        return {"status": "success", "message": "Autonomous cycle started"}
    except Exception as e:
        logger.error("Error starting autonomous cycle", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/autonomous/stop")
async def stop_autonomous_cycle():
    """Stop the autonomous AI cycle"""
    try:
        logger.info("🛑 Stopping autonomous AI cycle")
        await background_service.stop_autonomous_cycle()
        return {"status": "success", "message": "Autonomous cycle stopped"}
    except Exception as e:
        logger.error("Error stopping autonomous cycle", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/autonomous/status")
async def get_autonomous_status():
    """Get autonomous cycle status"""
    try:
        status = await background_service.get_system_status()
        return status
    except Exception as e:
        logger.error("Error getting autonomous status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/manual-cycle")
async def run_manual_cycle():
    """Run a manual AI agent cycle"""
    try:
        logger.info("🔄 Running manual AI agent cycle")
        result = await background_service.run_manual_cycle()
        return result
    except Exception as e:
        logger.error("Error running manual cycle", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_agents_status():
    """Get overall AI agents status"""
    try:
        # Test each agent
        agents_status = {}
        
        # Test Imperium
        try:
            imperium_result = await ai_agent_service.run_imperium_agent()
            agents_status["imperium"] = {
                "status": "healthy" if imperium_result["status"] == "success" else "warning",
                "last_run": imperium_result.get("timestamp", "unknown")
            }
        except Exception as e:
            agents_status["imperium"] = {"status": "error", "error": str(e)}
        
        # Test Guardian
        try:
            guardian_result = await ai_agent_service.run_guardian_agent()
            agents_status["guardian"] = {
                "status": "healthy" if guardian_result["status"] == "success" else "warning",
                "last_run": guardian_result.get("timestamp", "unknown")
            }
        except Exception as e:
            agents_status["guardian"] = {"status": "error", "error": str(e)}
        
        # Test Sandbox
        try:
            sandbox_result = await ai_agent_service.run_sandbox_agent()
            agents_status["sandbox"] = {
                "status": "healthy" if sandbox_result["status"] == "success" else "warning",
                "last_run": sandbox_result.get("timestamp", "unknown"),
                "ai_experiments_run": sandbox_result.get("ai_experiments_run", 0),
                "ai_code_generation": "enabled"
            }
        except Exception as e:
            agents_status["sandbox"] = {"status": "error", "error": str(e)}
        
        # Test Conquest
        try:
            conquest_result = await ai_agent_service.run_conquest_agent()
            agents_status["conquest"] = {
                "status": "healthy" if conquest_result["status"] == "success" else "warning",
                "last_run": conquest_result.get("timestamp", "unknown")
            }
        except Exception as e:
            agents_status["conquest"] = {"status": "error", "error": str(e)}
        
        return {
            "status": "success",
            "agents": agents_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting agents status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sandbox/test-ai-code-generation")
async def test_sandbox_ai_code_generation(request: Dict[str, Any]):
    """Test the sandbox agent's AI code generation capabilities"""
    try:
        from app.services.advanced_code_generator import AdvancedCodeGenerator
        
        description = request.get('description', 'A simple Flutter app')
        complexity = request.get('complexity', 'medium')
        
        # Test AI code generation directly
        generator = AdvancedCodeGenerator()
        generated_code = await generator.generate_dart_code(description, complexity)
        
        # Analyze the generated code
        analysis = await ai_agent_service._analyze_generated_code(generated_code, {
            "description": description,
            "complexity": complexity,
            "expected_features": request.get('expected_features', [])
        })
        
        return {
            "status": "success",
            "message": "Sandbox AI code generation test completed",
            "description": description,
            "complexity": complexity,
            "generated_code": generated_code,
            "code_length": len(generated_code),
            "analysis": analysis,
            "quality_score": analysis.get("quality_score", 0.0),
            "agent": "Sandbox"
        }
        
    except Exception as e:
        logger.error("Error testing sandbox AI code generation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sandbox/run-ai-experiments")
async def run_sandbox_ai_experiments():
    """Run AI code generation experiments in sandbox"""
    try:
        # Run AI experiments using the sandbox agent
        ai_experiments = await ai_agent_service._run_ai_code_generation_experiments()
        
        # Calculate summary statistics
        total_experiments = len(ai_experiments)
        successful_experiments = sum(1 for exp in ai_experiments if exp.get("success", False))
        average_quality = sum(exp.get("analysis", {}).get("quality_score", 0) for exp in ai_experiments) / total_experiments if total_experiments > 0 else 0
        
        return {
            "status": "success",
            "message": f"Sandbox AI experiments completed: {successful_experiments}/{total_experiments} successful",
            "experiments": ai_experiments,
            "summary": {
                "total_experiments": total_experiments,
                "successful_experiments": successful_experiments,
                "success_rate": successful_experiments / total_experiments if total_experiments > 0 else 0,
                "average_quality_score": average_quality,
                "complexity_distribution": {
                    "simple": sum(1 for exp in ai_experiments if exp.get("complexity") == "simple"),
                    "medium": sum(1 for exp in ai_experiments if exp.get("complexity") == "medium"),
                    "complex": sum(1 for exp in ai_experiments if exp.get("complexity") == "complex")
                }
            },
            "agent": "Sandbox"
        }
        
    except Exception as e:
        logger.error("Error running sandbox AI experiments", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sandbox/analyze-code-quality")
async def analyze_sandbox_code_quality(request: Dict[str, Any]):
    """Analyze the quality of generated code in sandbox"""
    try:
        code = request.get('code', '')
        test_case = {
            "description": request.get('description', ''),
            "complexity": request.get('complexity', 'medium'),
            "expected_features": request.get('expected_features', [])
        }
        
        # Analyze the code using sandbox agent's analysis method
        analysis = await ai_agent_service._analyze_generated_code(code, test_case)
        
        return {
            "status": "success",
            "message": "Code quality analysis completed",
            "code_length": len(code),
            "analysis": analysis,
            "quality_score": analysis.get("quality_score", 0.0),
            "features_found": analysis.get("features_found", []),
            "potential_issues": analysis.get("potential_issues", []),
            "suggestions": analysis.get("suggestions", []),
            "agent": "Sandbox"
        }
        
    except Exception as e:
        logger.error("Error analyzing code quality in sandbox", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sandbox/ai-capabilities")
async def get_sandbox_ai_capabilities():
    """Get sandbox agent's AI code generation capabilities"""
    try:
        return {
            "status": "success",
            "agent": "Sandbox",
            "capabilities": {
                "code_generation": "Available for Flutter/Dart development",
                "ai_learning": "Active learning system",
                "ml_integration": "Advanced ML capabilities",
                "local_models": "Available for basic code generation",
                "template_generation": "Fallback template system"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting sandbox AI capabilities", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 


@router.get("/cycle-status", summary="Get current AI cycle/status", tags=["Agents"])
async def get_ai_cycle_status():
    """
    Returns the current cycle/status for all AIs from live data
    """
    try:
        # Get real status from background service
        background_status = await background_service.get_system_status()
        
        # Get learning service status
        learning_status = await ai_learning_service.get_learning_status()
        
        # Get agent status from AI agent service
        agents_status = {}
        
        # Check each agent's status
        for agent_type in ["imperium", "guardian", "sandbox", "conquest"]:
            try:
                if agent_type == "imperium":
                    result = await ai_agent_service.run_imperium_agent()
                elif agent_type == "guardian":
                    result = await ai_agent_service.run_guardian_agent()
                elif agent_type == "sandbox":
                    result = await ai_agent_service.run_sandbox_agent()
                elif agent_type == "conquest":
                    result = await ai_agent_service.run_conquest_agent()
                
                agents_status[agent_type.title()] = {
                    "status": "active" if result.get("status") == "success" else "idle",
                    "last_action": f"{agent_type}_run",
                    "timestamp": result.get("timestamp", datetime.utcnow().isoformat())
                }
            except Exception as e:
                agents_status[agent_type.title()] = {
                    "status": "error",
                    "last_action": "unknown",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
        
        return {
            "agents": agents_status,
            "background_service": background_status,
            "learning_service": learning_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting AI cycle status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get AI cycle status") 