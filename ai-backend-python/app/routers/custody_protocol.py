"""
Custody Protocol Router
API endpoints for the Custody Protocol service
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Body
from typing import Dict, List, Optional
from datetime import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.services.custody_protocol_service import CustodyProtocolService, TestCategory, TestDifficulty

logger = structlog.get_logger()
router = APIRouter()


@router.get("/")
async def get_custody_protocol_overview():
    """Get custody protocol system overview"""
    try:
        custody_service = await CustodyProtocolService.initialize()
        analytics = await custody_service.get_custody_analytics()
        
        return {
            "status": "success",
            "message": "Custody Protocol system is active and monitoring all AIs",
            "timestamp": datetime.utcnow().isoformat(),
            "features": [
                "rigorous_ai_testing",
                "level_based_difficulty",
                "proposal_eligibility_control",
                "continuous_monitoring",
                "self_improvement_tracking",
                "cross_ai_collaboration_validation"
            ],
            "analytics": analytics
        }
    except Exception as e:
        logger.error("Error getting custody protocol overview", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_custody_analytics():
    """Get comprehensive custody protocol analytics"""
    try:
        custody_service = await CustodyProtocolService.initialize()
        analytics = await custody_service.get_custody_analytics()
        
        return {
            "status": "success",
            "data": analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting custody analytics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/{ai_type}")
async def administer_test(
    ai_type: str,
    test_category: Optional[TestCategory] = None,
    background_tasks: BackgroundTasks = None
):
    """Administer a custody test to a specific AI"""
    try:
        if ai_type not in ["imperium", "guardian", "sandbox", "conquest"]:
            raise HTTPException(status_code=400, detail=f"Invalid AI type: {ai_type}")
        
        custody_service = await CustodyProtocolService.initialize()
        result = await custody_service.administer_custody_test(ai_type, test_category)
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error administering test to {ai_type}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test/{ai_type}/status")
async def get_ai_test_status(ai_type: str):
    """Get current test status for a specific AI"""
    try:
        if ai_type not in ["imperium", "guardian", "sandbox", "conquest"]:
            raise HTTPException(status_code=400, detail=f"Invalid AI type: {ai_type}")
        
        custody_service = await CustodyProtocolService.initialize()
        analytics = await custody_service.get_custody_analytics()
        
        ai_metrics = analytics.get("ai_specific_metrics", {}).get(ai_type, {})
        
        return {
            "status": "success",
            "data": {
                "ai_type": ai_type,
                "total_tests_given": ai_metrics.get("total_tests_given", 0),
                "total_tests_passed": ai_metrics.get("total_tests_passed", 0),
                "total_tests_failed": ai_metrics.get("total_tests_failed", 0),
                "pass_rate": ai_metrics.get("pass_rate", 0),
                "current_difficulty": ai_metrics.get("current_difficulty", "basic"),
                "custody_level": ai_metrics.get("custody_level", 1),
                "custody_xp": ai_metrics.get("custody_xp", 0),
                "consecutive_successes": ai_metrics.get("consecutive_successes", 0),
                "consecutive_failures": ai_metrics.get("consecutive_failures", 0),
                "can_level_up": ai_metrics.get("can_level_up", False),
                "can_create_proposals": ai_metrics.get("can_create_proposals", False),
                "last_test_date": ai_metrics.get("last_test_date"),
                "test_history": ai_metrics.get("test_history", [])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting test status for {ai_type}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/{ai_type}/force")
async def force_test(ai_type: str):
    """Force a custody test for a specific AI (admin function)"""
    try:
        if ai_type not in ["imperium", "guardian", "sandbox", "conquest"]:
            raise HTTPException(status_code=400, detail=f"Invalid AI type: {ai_type}")
        
        custody_service = await CustodyProtocolService.initialize()
        result = await custody_service.force_custody_test(ai_type)
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error forcing test for {ai_type}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/{ai_type}/reset")
async def reset_ai_metrics(ai_type: str):
    """Reset custody metrics for a specific AI (admin function)"""
    try:
        if ai_type not in ["imperium", "guardian", "sandbox", "conquest"]:
            raise HTTPException(status_code=400, detail=f"Invalid AI type: {ai_type}")
        
        custody_service = await CustodyProtocolService.initialize()
        result = await custody_service.reset_custody_metrics(ai_type)
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error resetting metrics for {ai_type}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/eligibility/{ai_type}")
async def check_ai_eligibility(ai_type: str):
    """Check if an AI is eligible to level up or create proposals"""
    try:
        if ai_type not in ["imperium", "guardian", "sandbox", "conquest"]:
            raise HTTPException(status_code=400, detail=f"Invalid AI type: {ai_type}")
        
        custody_service = await CustodyProtocolService.initialize()
        analytics = await custody_service.get_custody_analytics()
        
        ai_metrics = analytics.get("ai_specific_metrics", {}).get(ai_type, {})
        
        return {
            "status": "success",
            "data": {
                "ai_type": ai_type,
                "can_level_up": ai_metrics.get("can_level_up", False),
                "can_create_proposals": ai_metrics.get("can_create_proposals", False),
                "requirements": {
                    "level_up": {
                        "recent_pass_rate": "80% or higher in last 5 tests",
                        "consecutive_failures": "2 or fewer",
                        "custody_xp": "100 or higher"
                    },
                    "proposals": {
                        "at_least_one_test_passed": "Must have passed at least one test",
                        "consecutive_failures": "3 or fewer",
                        "recent_test": "Must have passed a test in last 24 hours"
                    }
                },
                "current_status": {
                    "total_tests_passed": ai_metrics.get("total_tests_passed", 0),
                    "consecutive_failures": ai_metrics.get("consecutive_failures", 0),
                    "custody_xp": ai_metrics.get("custody_xp", 0),
                    "last_test_date": ai_metrics.get("last_test_date")
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking eligibility for {ai_type}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/difficulty/{ai_type}")
async def get_ai_difficulty(ai_type: str):
    """Get current test difficulty for a specific AI"""
    try:
        if ai_type not in ["imperium", "guardian", "sandbox", "conquest"]:
            raise HTTPException(status_code=400, detail=f"Invalid AI type: {ai_type}")
        
        custody_service = await CustodyProtocolService.initialize()
        analytics = await custody_service.get_custody_analytics()
        
        ai_metrics = analytics.get("ai_specific_metrics", {}).get(ai_type, {})
        current_difficulty = ai_metrics.get("current_difficulty", "basic")
        
        # Get difficulty requirements
        difficulty_requirements = {
            "basic": {"level_range": "1-9", "description": "Fundamental knowledge and basic skills"},
            "intermediate": {"level_range": "10-19", "description": "Intermediate skills and understanding"},
            "advanced": {"level_range": "20-29", "description": "Advanced capabilities and complex problem solving"},
            "expert": {"level_range": "30-39", "description": "Expert-level knowledge and innovation"},
            "master": {"level_range": "40-49", "description": "Master-level expertise and leadership"},
            "legendary": {"level_range": "50+", "description": "Legendary capabilities and system mastery"}
        }
        
        return {
            "status": "success",
            "data": {
                "ai_type": ai_type,
                "current_difficulty": current_difficulty,
                "requirements": difficulty_requirements.get(current_difficulty, {}),
                "next_difficulty": _get_next_difficulty(current_difficulty),
                "custody_level": ai_metrics.get("custody_level", 1)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting difficulty for {ai_type}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-categories")
async def get_test_categories():
    """Get available test categories and their descriptions"""
    try:
        categories = {
            "knowledge_verification": {
                "description": "Tests AI's understanding of learned subjects and concepts",
                "ai_focus": ["imperium", "all"],
                "difficulty_focus": ["basic", "intermediate"]
            },
            "code_quality": {
                "description": "Tests AI's ability to write and analyze high-quality code",
                "ai_focus": ["guardian", "sandbox", "conquest"],
                "difficulty_focus": ["intermediate", "advanced"]
            },
            "security_awareness": {
                "description": "Tests AI's understanding of security principles and vulnerabilities",
                "ai_focus": ["guardian"],
                "difficulty_focus": ["intermediate", "advanced", "expert"]
            },
            "performance_optimization": {
                "description": "Tests AI's ability to optimize code and system performance",
                "ai_focus": ["guardian", "conquest"],
                "difficulty_focus": ["advanced", "expert"]
            },
            "innovation_capability": {
                "description": "Tests AI's ability to think creatively and propose innovative solutions",
                "ai_focus": ["sandbox", "conquest"],
                "difficulty_focus": ["advanced", "expert", "master"]
            },
            "self_improvement": {
                "description": "Tests AI's ability to learn from mistakes and improve itself",
                "ai_focus": ["imperium"],
                "difficulty_focus": ["expert", "master", "legendary"]
            },
            "cross_ai_collaboration": {
                "description": "Tests AI's ability to work with and coordinate with other AI systems",
                "ai_focus": ["imperium"],
                "difficulty_focus": ["expert", "master", "legendary"]
            },
            "experimental_validation": {
                "description": "Tests AI's ability to design and validate experiments",
                "ai_focus": ["sandbox"],
                "difficulty_focus": ["advanced", "expert", "master"]
            }
        }
        
        return {
            "status": "success",
            "data": {
                "categories": categories,
                "total_categories": len(categories)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting test categories", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations")
async def get_custody_recommendations():
    """Get custody protocol recommendations for all AIs"""
    try:
        custody_service = await CustodyProtocolService.initialize()
        analytics = await custody_service.get_custody_analytics()
        
        recommendations = analytics.get("recommendations", [])
        
        return {
            "status": "success",
            "data": {
                "recommendations": recommendations,
                "total_recommendations": len(recommendations),
                "priority_recommendations": [r for r in recommendations if "needs" in r.lower() or "failure" in r.lower()]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting custody recommendations", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-test")
async def batch_test_all_ais():
    """Administer custody tests to all AIs (admin function)"""
    try:
        custody_service = await CustodyProtocolService.initialize()
        results = {}
        
        for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:
            try:
                result = await custody_service.administer_custody_test(ai_type)
                results[ai_type] = result
            except Exception as e:
                results[ai_type] = {"status": "error", "message": str(e)}
        
        return {
            "status": "success",
            "data": {
                "batch_results": results,
                "total_ais_tested": len(results),
                "successful_tests": len([r for r in results.values() if r.get("status") != "error"])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error in batch testing", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/live-analytics")
async def get_live_analytics():
    """Get live AI analytics for The Warp frontend"""
    import time
    start = time.time()
    try:
        custody_service = await CustodyProtocolService.initialize()
        analytics = await custody_service.get_live_ai_analytics()
        duration = time.time() - start
        logger.info(f"/custody/live-analytics duration: {duration:.2f}s")
        return {
            "status": "success",
            "data": analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting live analytics", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving live analytics: {str(e)}")

@router.get("/leaderboard")
async def get_leaderboard():
    """Get AI leaderboard for The Warp frontend"""
    import time
    start = time.time()
    try:
        custody_service = await CustodyProtocolService.initialize()
        leaderboard = await custody_service.get_ai_leaderboard()
        duration = time.time() - start
        logger.info(f"/custody/leaderboard duration: {duration:.2f}s")
        return {
            "status": "success",
            "data": leaderboard,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting leaderboard", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


class TrainingGroundScenarioRequest(BaseModel):
    sandbox_level: int
    difficulty: str

class DeploySandboxAttackRequest(BaseModel):
    scenario: dict
    user_id: str = None

@router.post("/training-ground/scenario")
async def generate_training_ground_scenario(request: TrainingGroundScenarioRequest = Body(...)):
    """Generate a live hacking scenario for Sandbox using SCKIPIT, ML/LLM, and internet knowledge."""
    try:
        custody_service = await CustodyProtocolService.initialize()
        scenario = await custody_service.generate_live_hacking_scenario(request.sandbox_level, request.difficulty)
        return {
            "status": "success",
            "scenario": scenario,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error generating training ground scenario", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/training-ground/deploy")
async def deploy_sandbox_attack(request: DeploySandboxAttackRequest = Body(...), background_tasks: BackgroundTasks = None):
    """Deploy Sandbox to attack the given scenario, track progress, and update XP/learning."""
    try:
        custody_service = await CustodyProtocolService.initialize()
        result = await custody_service.deploy_sandbox_attack(request.scenario, request.user_id)
        return {
            "status": result["status"],
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error deploying sandbox attack", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/generate")
async def generate_test(ai_types: list, test_type: str, difficulty: str):
    """Generate a live test (standard or Olympus Treaty), single or collaborative."""
    try:
        custody_service = await CustodyProtocolService.initialize()
        test = await custody_service.generate_test(ai_types, test_type, difficulty)
        return {
            "status": "success",
            "test": test,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error generating test", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/execute")
async def execute_test(test: dict):
    """Execute a live test (single or collaborative), score, and update XP/learning."""
    try:
        custody_service = await CustodyProtocolService.initialize()
        result = await custody_service.execute_test(test)
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error executing test", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent-tests")
async def get_recent_tests(limit: int = 20):
    """Get recent test events from database"""
    try:
        from app.services.agent_metrics_service import AgentMetricsService
        
        agent_metrics_service = AgentMetricsService()
        all_metrics = await agent_metrics_service.get_all_agent_metrics()
        
        # Collect test history from all agents
        recent_tests = []
        for ai_type, metrics in all_metrics.items():
            test_history = metrics.get("test_history", [])
            for test in test_history:
                test_entry = {
                    "ai_type": ai_type,
                    "test_type": test.get("test_type", "standard"),
                    "score": test.get("score", 0),
                    "passed": test.get("passed", False),
                    "timestamp": test.get("timestamp", ""),
                    "xp_awarded": test.get("xp_awarded", 0),
                    "scenario_domain": test.get("scenario_domain", ""),
                    "scenario_complexity": test.get("scenario_complexity", ""),
                    "is_winner": test.get("is_winner", False)
                }
                recent_tests.append(test_entry)
        
        # Sort by timestamp and limit
        recent_tests.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        recent_tests = recent_tests[:limit]
        
        return {
            "status": "success",
            "data": recent_tests,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting recent tests", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent-adversarial-tests")
async def get_recent_adversarial_tests(limit: int = 20):
    """Get recent adversarial test events from database"""
    try:
        from app.services.agent_metrics_service import AgentMetricsService
        
        agent_metrics_service = AgentMetricsService()
        all_metrics = await agent_metrics_service.get_all_agent_metrics()
        
        # Collect adversarial test history from all agents
        recent_adversarial_tests = []
        for ai_type, metrics in all_metrics.items():
            test_history = metrics.get("test_history", [])
            for test in test_history:
                if test.get("test_type") == "adversarial":
                    test_entry = {
                        "ai_type": ai_type,
                        "test_type": "adversarial",
                        "score": test.get("score", 0),
                        "passed": test.get("passed", False),
                        "timestamp": test.get("timestamp", ""),
                        "xp_awarded": test.get("xp_awarded", 0),
                        "scenario_domain": test.get("scenario_domain", ""),
                        "scenario_complexity": test.get("scenario_complexity", ""),
                        "is_winner": test.get("is_winner", False)
                    }
                    recent_adversarial_tests.append(test_entry)
        
        # Sort by timestamp and limit
        recent_adversarial_tests.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        recent_adversarial_tests = recent_adversarial_tests[:limit]
        
        return {
            "status": "success",
            "data": recent_adversarial_tests,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting recent adversarial tests", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explainability-analytics")
async def get_explainability_analytics(ai_type: Optional[str] = None):
    """Get explainability and transparency analytics for AI responses"""
    try:
        from app.services.ai_learning_service import AILearningService
        
        learning_service = await AILearningService.initialize()
        analytics = await learning_service.get_explainability_analytics(ai_type)
        
        return {
            "status": "success",
            "data": analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting explainability analytics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/olympics/run")
async def run_olympic_event(
    participants: List[str],
    difficulty: str = "advanced",
    event_type: str = "olympics"
):
    """Trigger a new olympic event between AIs."""
    try:
        custody_service = await CustodyProtocolService.initialize()
        diff_enum = TestDifficulty[difficulty.upper()] if hasattr(TestDifficulty, difficulty.upper()) else TestDifficulty.ADVANCED
        result = await custody_service.administer_olympic_event(participants, diff_enum, event_type)
        return {"status": "success", "data": result, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error running olympic event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/olympics/history")
async def get_olympic_history(limit: int = 20):
    """List past olympic events."""
    try:
        custody_service = await CustodyProtocolService.initialize()
        events = await custody_service.get_olympic_history(limit)
        return {"status": "success", "data": events, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error fetching olympic history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaderboard/olympics")
async def get_olympic_leaderboard():
    service = await CustodyProtocolService.initialize()
    leaderboard = await service.get_leaderboard()
    return {"status": "success", "leaderboard": leaderboard}


@router.post("/cross_ai_testing")
async def cross_ai_testing():
    """Trigger Custodes' cross-AI testing across all AIs."""
    service = await CustodyProtocolService.initialize()
    result = await service.run_cross_ai_testing()
    return result


@router.get("/training-ground/scenarios")
async def get_training_ground_scenarios(sandbox_level: int):
    """Get 3 daily hacking scenarios for Training Ground, with degree, difficulty, and recommended flag."""
    try:
        custody_service = await CustodyProtocolService.initialize()
        scenarios = await custody_service.get_training_ground_scenarios(sandbox_level)
        return {
            "status": "success",
            "scenarios": scenarios,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting training ground scenarios", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/adversarial-test")
async def run_adversarial_test(ai_types: List[str] = Body(...)):
    """Run an adversarial test between selected AIs and return the result."""
    try:
        import random
        
        # If no AIs selected or fewer than 2, randomly select 2
        if len(ai_types) != 2:
            available_ais = ["imperium", "guardian", "sandbox", "conquest"]
            ai_types = random.sample(available_ais, 2)
            logger.info(f"Randomly selected AIs for adversarial testing: {ai_types}")
        
        for ai_type in ai_types:
            if ai_type not in ["imperium", "guardian", "sandbox", "conquest"]:
                raise HTTPException(status_code=400, detail=f"Invalid AI type: {ai_type}")
        
        custody_service = await CustodyProtocolService.initialize()
        result = await custody_service.run_adversarial_testing(ai_types)
        
        # The result should include ai_pair, scenario, answers, evaluation, etc.
        # If the service returns a list, pick the latest or first
        if isinstance(result, dict) and 'adversarial_tests' in result:
            # If multiple tests, return the first one
            test = result['adversarial_tests'][0] if result['adversarial_tests'] else {}
        else:
            test = result
            
        return {
            "status": "success",
            "result": test,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error running adversarial test", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning-stats/{ai_type}")
async def get_ai_learning_stats(ai_type: str):
    """Get learning statistics for a specific AI"""
    try:
        from app.services.self_generating_ai_service import self_generating_ai_service
        stats = await self_generating_ai_service.get_learning_stats(ai_type)
        return {"status": "success", "data": stats}
    except Exception as e:
        logger.error(f"Error getting learning stats for {ai_type}: {str(e)}")
        return {"status": "error", "message": str(e)}


def _get_next_difficulty(current_difficulty: str) -> str:
    """Get the next difficulty level"""
    difficulty_progression = ["basic", "intermediate", "advanced", "expert", "master", "legendary"]
    try:
        current_index = difficulty_progression.index(current_difficulty)
        if current_index < len(difficulty_progression) - 1:
            return difficulty_progression[current_index + 1]
        else:
            return "legendary"  # Already at max
    except ValueError:
        return "basic"  # Default if unknown difficulty 