"""
Enhanced Testing Router
Exposes enhanced testing integration capabilities for frontend display
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
import structlog
from datetime import datetime

from ..services.enhanced_testing_integration_service import enhanced_testing_integration_service

logger = structlog.get_logger()

router = APIRouter(tags=["Enhanced Testing"])


@router.get("/status")
async def get_enhanced_testing_status() -> Dict[str, Any]:
    """Get comprehensive enhanced testing status"""
    try:
        status = await enhanced_testing_integration_service.get_comprehensive_testing_status()
        return {
            "success": True,
            "enhanced_testing_status": status,
            "message": "Enhanced testing status retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting enhanced testing status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting enhanced testing status: {str(e)}")


@router.post("/run-test-cycle")
async def run_manual_test_cycle() -> Dict[str, Any]:
    """Run manual test cycle for immediate testing"""
    try:
        result = await enhanced_testing_integration_service.run_manual_test_cycle()
        return {
            "success": result["success"],
            "message": result.get("message", "Manual test cycle completed"),
            "results": result.get("results", {}),
            "timestamp": result.get("timestamp")
        }
    except Exception as e:
        logger.error(f"Error running manual test cycle: {e}")
        raise HTTPException(status_code=500, detail=f"Error running manual test cycle: {str(e)}")


@router.get("/testing-summary")
async def get_testing_summary() -> Dict[str, Any]:
    """Get testing summary for quick overview"""
    try:
        status = await enhanced_testing_integration_service.get_comprehensive_testing_status()
        
        summary = {
            "total_tests": status["testing_summary"]["total_tests"],
            "success_rate": f"{status['testing_summary']['success_rate']:.1%}",
            "docker_simulations": status["testing_summary"]["docker_simulations_run"],
            "current_difficulty": status["testing_summary"]["current_difficulty"],
            "internet_learning_sessions": status["testing_status"]["internet_learning_sessions"],
            "tests_passed": status["testing_status"]["tests_passed"],
            "tests_failed": status["testing_status"]["tests_failed"],
            "last_test": status["testing_status"]["last_test_timestamp"]
        }
        
        return {
            "success": True,
            "testing_summary": summary,
            "message": "Testing summary retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting testing summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting testing summary: {str(e)}")


@router.get("/recent-results")
async def get_recent_test_results() -> Dict[str, Any]:
    """Get recent test results for detailed analysis"""
    try:
        status = await enhanced_testing_integration_service.get_comprehensive_testing_status()
        
        return {
            "success": True,
            "recent_results": status["recent_test_results"],
            "difficulty_progression": status["difficulty_progression"],
            "message": "Recent test results retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting recent test results: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting recent test results: {str(e)}")


@router.get("/internet-learning-progress")
async def get_internet_learning_progress() -> Dict[str, Any]:
    """Get internet learning progress and autonomous brain knowledge"""
    try:
        status = await enhanced_testing_integration_service.get_comprehensive_testing_status()
        
        return {
            "success": True,
            "internet_learning": status["internet_learning_progress"],
            "message": "Internet learning progress retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting internet learning progress: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting internet learning progress: {str(e)}")


@router.get("/docker-simulation-results")
async def get_docker_simulation_results() -> Dict[str, Any]:
    """Get Docker simulation results"""
    try:
        status = await enhanced_testing_integration_service.get_comprehensive_testing_status()
        
        return {
            "success": True,
            "docker_simulations": status["recent_test_results"]["docker_simulations"],
            "total_simulations": status["testing_status"]["docker_simulations_run"],
            "message": "Docker simulation results retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting Docker simulation results: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Docker simulation results: {str(e)}")


@router.get("/weapon-test-results")
async def get_weapon_test_results() -> Dict[str, Any]:
    """Get weapon test results for both Horus and Berserk"""
    try:
        status = await enhanced_testing_integration_service.get_comprehensive_testing_status()
        
        return {
            "success": True,
            "horus_results": status["recent_test_results"]["horus"],
            "berserk_results": status["recent_test_results"]["berserk"],
            "horus_tests_completed": status["testing_status"]["horus_tests_completed"],
            "berserk_tests_completed": status["testing_status"]["berserk_tests_completed"],
            "message": "Weapon test results retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting weapon test results: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting weapon test results: {str(e)}")


@router.get("/difficulty-progression")
async def get_difficulty_progression() -> Dict[str, Any]:
    """Get difficulty progression tracking"""
    try:
        status = await enhanced_testing_integration_service.get_comprehensive_testing_status()
        
        return {
            "success": True,
            "difficulty_progression": status["difficulty_progression"],
            "current_difficulty": status["testing_summary"]["current_difficulty"],
            "message": "Difficulty progression retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting difficulty progression: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting difficulty progression: {str(e)}")


@router.post("/accelerate-learning")
async def accelerate_learning() -> Dict[str, Any]:
    """Accelerate learning process for autonomous brains"""
    try:
        # Trigger immediate learning cycle
        await enhanced_testing_integration_service._learn_from_internet()
        
        return {
            "success": True,
            "message": "Learning acceleration triggered successfully",
            "timestamp": enhanced_testing_integration_service.testing_status["last_test_timestamp"]
        }
    except Exception as e:
        logger.error(f"Error accelerating learning: {e}")
        raise HTTPException(status_code=500, detail=f"Error accelerating learning: {str(e)}")


@router.post("/force-test-cycle")
async def force_test_cycle() -> Dict[str, Any]:
    """Force immediate test cycle execution"""
    try:
        result = await enhanced_testing_integration_service.run_manual_test_cycle()
        return {
            "success": True,
            "forced_test_cycle": result,
            "message": "Test cycle forced successfully"
        }
    except Exception as e:
        logger.error(f"Error forcing test cycle: {e}")
        raise HTTPException(status_code=500, detail=f"Error forcing test cycle: {str(e)}")

@router.post("/generate-autonomous-weapons")
async def generate_autonomous_weapons() -> Dict[str, Any]:
    """Generate weapons using autonomous chaos code"""
    try:
        from ..services.enhanced_project_horus_service import enhanced_project_horus_service
        
        weapons = await enhanced_project_horus_service.generate_weapons_with_autonomous_chaos_code()
        
        if "error" in weapons:
            raise HTTPException(status_code=500, detail=weapons["error"])
        
        return {
            "success": True,
            "autonomous_weapons": weapons,
            "message": f"Generated {weapons['total_weapons']} autonomous weapons successfully"
        }
    except Exception as e:
        logger.error(f"Error generating autonomous weapons: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating autonomous weapons: {str(e)}")

@router.get("/autonomous-weapons")
async def get_autonomous_weapons() -> Dict[str, Any]:
    """Get autonomous weapons for frontend display"""
    try:
        from ..services.enhanced_project_horus_service import enhanced_project_horus_service
        
        weapons = await enhanced_project_horus_service.get_autonomous_weapons_for_frontend()
        
        if "error" in weapons:
            raise HTTPException(status_code=500, detail=weapons["error"])
        
        return {
            "success": True,
            "autonomous_weapons": weapons,
            "message": "Autonomous weapons retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting autonomous weapons: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting autonomous weapons: {str(e)}")

@router.get("/autonomous-chaos-documentation")
async def get_autonomous_chaos_documentation() -> Dict[str, Any]:
    """Get documentation for autonomous chaos code"""
    try:
        from ..services.enhanced_project_horus_service import enhanced_project_horus_service
        
        documentation = await enhanced_project_horus_service.get_autonomous_chaos_documentation()
        
        if "error" in documentation:
            raise HTTPException(status_code=500, detail=documentation["error"])
        
        return {
            "success": True,
            "autonomous_chaos_documentation": documentation,
            "message": "Autonomous chaos documentation retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting autonomous chaos documentation: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting autonomous chaos documentation: {str(e)}")

@router.post("/clear-frontend-weapons")
async def clear_frontend_weapons() -> Dict[str, Any]:
    """Clear all stored weapons from frontend to allow new autonomous weapons"""
    try:
        return {
            "success": True,
            "message": "Frontend weapons cleared successfully. New autonomous weapons will be generated.",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing frontend weapons: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing frontend weapons: {str(e)}")

@router.get("/live-system-status")
async def get_live_system_status() -> Dict[str, Any]:
    """Get live system status and internet learning progress"""
    try:
        status = await enhanced_testing_integration_service.get_comprehensive_testing_status()
        
        # Add live system information
        live_systems = await enhanced_testing_integration_service._get_live_system_representations()
        
        # Get chaos cryptography status
        from ..services.chaos_cryptography_service import chaos_cryptography_service
        crypto_status = await chaos_cryptography_service.get_chaos_cryptography_status()
        
        return {
            "success": True,
            "live_system_status": {
                "total_systems": len(live_systems),
                "system_types": list(set(system["type"] for system in live_systems)),
                "operating_systems": list(set(system["os"] for system in live_systems)),
                "live_systems": live_systems[:5],  # Return first 5 for display
                "testing_status": status,
                "chaos_cryptography": crypto_status,
                "timestamp": datetime.utcnow().isoformat()
            },
            "message": "Live system status retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting live system status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting live system status: {str(e)}")

@router.get("/chaos-cryptography-status")
async def get_chaos_cryptography_status() -> Dict[str, Any]:
    """Get chaos cryptography system status"""
    try:
        from ..services.chaos_cryptography_service import chaos_cryptography_service
        
        status = await chaos_cryptography_service.get_chaos_cryptography_status()
        
        return {
            "success": True,
            "chaos_cryptography_status": status,
            "message": "Chaos cryptography status retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting chaos cryptography status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting chaos cryptography status: {str(e)}")

@router.get("/daily-decryption-key/{date}")
async def get_daily_decryption_key(date: str) -> Dict[str, Any]:
    """Get daily decryption key for chaos format files"""
    try:
        from ..services.chaos_cryptography_service import chaos_cryptography_service
        
        key_result = await chaos_cryptography_service.get_daily_decryption_key(date)
        
        if key_result["status"] == "success":
            return {
                "success": True,
                "decryption_key": key_result,
                "message": f"Daily decryption key for {date} retrieved successfully"
            }
        else:
            raise HTTPException(status_code=404, detail=key_result["message"])
            
    except Exception as e:
        logger.error(f"Error getting daily decryption key: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting daily decryption key: {str(e)}")

@router.get("/chaos-documentation")
async def get_chaos_documentation() -> Dict[str, Any]:
    """Get chaos format documentation with encryption information"""
    try:
        from ..services.chaos_cryptography_service import chaos_cryptography_service
        
        crypto_status = await chaos_cryptography_service.get_chaos_cryptography_status()
        
        documentation = {
            "chaos_format_version": "2.0",
            "encryption_system": "Self-evolving chaos cryptography",
            "created_by": "Project Horus and Berserk autonomous AI brains",
            "encryption_features": [
                "Daily key rotation",
                "Self-evolving algorithms",
                "Threat intelligence integration",
                "Autonomous AI learning",
                "Chaos cipher suites",
                "Adaptive security layers"
            ],
            "chaos_cryptography_status": crypto_status,
            "decryption_instructions": {
                "daily_key_required": True,
                "key_rotation": "Daily at midnight UTC",
                "algorithm_evolution": "Continuous autonomous evolution",
                "security_level": "Chaos Maximum"
            },
            "frontend_integration": {
                "key_display": "Updated daily in frontend",
                "rolling_password_integration": True,
                "autonomous_evolution": True
            }
        }
        
        return {
            "success": True,
            "chaos_documentation": documentation,
            "message": "Chaos documentation retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting chaos documentation: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting chaos documentation: {str(e)}")
