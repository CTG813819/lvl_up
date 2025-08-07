"""
AI Integration Router
Routes for integrated AI adversarial learning and weapon systems
LIVE SERVICES ONLY - NO FALLBACKS
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
import structlog

# Import LIVE services - NO FALLBACKS
from ..services.ai_adversarial_integration_service import ai_adversarial_integration_service
from ..services.enhanced_project_horus_service import enhanced_project_horus_service
from ..services.project_berserk_enhanced_service import project_berserk_enhanced_service
from ..services.chaos_language_service import chaos_language_service

logger = structlog.get_logger()
router = APIRouter(prefix="/api/ai-integration", tags=["AI Integration"])


class AdversarialTrainingRequest(BaseModel):
    ai_type: str
    force_scenario: Optional[str] = None


class WeaponDeploymentRequest(BaseModel):
    weapon_id: str
    target_system: str
    deployment_option: str
    mode: Optional[str] = "simulation"


class LearningIntegrationRequest(BaseModel):
    ai_types: Optional[List[str]] = None


class FailureDataRequest(BaseModel):
    ai_type: str
    failure_data: Dict[str, Any]
    learning_context: str
    timestamp: str


@router.post("/adversarial-training/run")
async def run_adversarial_training(request: AdversarialTrainingRequest) -> Dict[str, Any]:
    """Run LIVE adversarial training for specific AI"""
    try:
        if not hasattr(ai_adversarial_integration_service, 'initialized') or not ai_adversarial_integration_service.initialized:
            await ai_adversarial_integration_service.initialize()
        
        result = await ai_adversarial_integration_service.integrate_adversarial_scenario_into_ai_learning(
            request.ai_type, 
            request.force_scenario
        )
        
        return {
            "status": "success",
            "message": f"LIVE adversarial training completed for {request.ai_type}",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error running LIVE adversarial training: {e}")
        raise HTTPException(status_code=500, detail=f"LIVE adversarial training failed: {str(e)}")


@router.get("/adversarial-training/progress")
async def get_adversarial_progress() -> Dict[str, Any]:
    """Get LIVE adversarial training progress for all AIs"""
    try:
        if not hasattr(ai_adversarial_integration_service, 'initialized'):
            await ai_adversarial_integration_service.initialize()
        
        report = await ai_adversarial_integration_service.get_adversarial_progress_report()
        
        return {
            "status": "success",
            "progress_report": report
        }
        
    except Exception as e:
        logger.error(f"Error getting LIVE adversarial progress: {e}")
        raise HTTPException(status_code=500, detail=f"LIVE adversarial progress failed: {str(e)}")


@router.get("/horus/weapon-synthesis-report")
async def get_weapon_synthesis_report() -> Dict[str, Any]:
    """Get LIVE weapon synthesis report from Project Horus with NEW weapon generation"""
    try:
        # LIVE WEAPON GENERATION - Create new weapons each time
        logger.info("🚀 LIVE: Generating new weapons from AI learning...")
        
        # Learn from all AI types and synthesize new weapons
        ai_types = ["imperium", "conquest", "sandbox", "guardian"]
        for ai_type in ai_types:
            await enhanced_project_horus_service.learn_from_ai_experiences([ai_type])
        
        # Generate additional synthetic weapons based on internet learning
        await enhanced_project_horus_service.evolve_chaos_language()
        
        # Get updated synthesis report with new weapons
        report = await enhanced_project_horus_service.get_weapon_synthesis_report()
        
        logger.info(f"🔥 LIVE: Generated {report.get('total_weapons', 0)} weapons total")
        
        return {
            "status": "success",
            "synthesis_report": report,
            "generation_timestamp": datetime.utcnow().isoformat(),
            "live_generation": True
        }
        
    except Exception as e:
        logger.error(f"Error generating LIVE weapon synthesis report: {e}")
        raise HTTPException(status_code=500, detail=f"LIVE weapon synthesis failed: {str(e)}")


@router.post("/berserk/deploy-weapon")
async def deploy_weapon(request: WeaponDeploymentRequest) -> Dict[str, Any]:
    """Deploy LIVE weapon with specified deployment option"""
    try:
        result = await project_berserk_enhanced_service.deploy_weapon(
            request.weapon_id,
            request.target_system,
            request.deployment_option
        )
        
        return {
            "status": "success" if result.get("success", False) else "failed",
            "message": "LIVE weapon deployment completed",
            "deployment_result": result
        }
        
    except Exception as e:
        logger.error(f"Error deploying LIVE weapon: {e}")
        raise HTTPException(status_code=500, detail=f"LIVE weapon deployment failed: {str(e)}")


@router.get("/berserk/create-weapons")
async def create_synthetic_weapons(count: int = 3) -> Dict[str, Any]:
    """Create LIVE synthetic self-growing weapons"""
    try:
        result = await project_berserk_enhanced_service.create_synthetic_growing_weapons(count)
        
        return {
            "status": "success",
            "message": f"Created {result.get('weapons_created', 0)} LIVE synthetic weapons",
            "creation_results": result
        }
        
    except Exception as e:
        logger.error(f"Error creating LIVE synthetic weapons: {e}")
        raise HTTPException(status_code=500, detail=f"LIVE synthetic weapons creation failed: {str(e)}")


@router.get("/integration/status")
async def get_integration_status() -> Dict[str, Any]:
    """Get LIVE overall AI integration status"""
    try:
        # Get LIVE status from all services
        adversarial_progress = await ai_adversarial_integration_service.get_adversarial_progress_report()
        horus_report = await enhanced_project_horus_service.get_weapon_synthesis_report()
        berserk_status = await project_berserk_enhanced_service.get_berserk_status_report()
        chaos_language = await chaos_language_service.get_complete_chaos_language_documentation()
        
        return {
            "status": "success",
            "integration_status": {
                "adversarial_training": {
                    "total_ais": len(adversarial_progress.get("ai_progress", {})),
                    "total_scenarios_completed": sum(
                        ai_data.get("scenarios_completed", 0) 
                        for ai_data in adversarial_progress.get("ai_progress", {}).values()
                    ),
                    "overall_success_rate": adversarial_progress.get("aggregate_stats", {}).get("overall_success_rate", 0.0)
                },
                "project_horus": {
                    "total_weapons": horus_report.get("total_weapons", 0),
                    "average_complexity": horus_report.get("average_complexity", 0.0),
                    "chaos_language_version": chaos_language.get("language_core", {}).get("version", "unknown")
                },
                "project_berserk": {
                    "total_weapons": berserk_status.get("total_weapons", 0),
                    "active_deployments": berserk_status.get("active_deployments", 0),
                    "systems_compromised": berserk_status.get("deployment_statistics", {}).get("systems_compromised", 0)
                },
                "frontend_dependency": "removed",
                "backend_integration": "LIVE",
                "periodic_sync": "LIVE",
                "complex_testing": "LIVE",
                "ml_learning_system": "LIVE"
            },
            "ml_learning_metrics": await enhanced_project_horus_service.get_ml_performance_metrics()
        }
        
    except Exception as e:
        logger.error(f"Error getting LIVE integration status: {e}")
        raise HTTPException(status_code=500, detail=f"LIVE integration status failed: {str(e)}")


@router.get("/horus/ml-metrics")
async def get_horus_ml_metrics() -> Dict[str, Any]:
    """Get ML performance metrics from Project Horus"""
    try:
        metrics = await enhanced_project_horus_service.get_ml_performance_metrics()
        return {
            "status": "success",
            "ml_metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting Horus ML metrics: {e}")
        return {"status": "error", "error": str(e)}

# NEW: Failure Learning Endpoints
@router.post("/horus/learn-from-failure")
async def horus_learn_from_failure(failure_data: Dict[str, Any]) -> Dict[str, Any]:
    """Trigger Project Horus to learn from a failure"""
    try:
        result = await enhanced_project_horus_service.learn_from_failure(failure_data)
        return {
            "status": "success",
            "learning_result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error triggering Horus failure learning: {e}")
        return {"status": "error", "error": str(e)}

@router.get("/horus/failure-learning-status")
async def get_horus_failure_learning_status() -> Dict[str, Any]:
    """Get Project Horus failure learning status"""
    try:
        status = await enhanced_project_horus_service.get_failure_learning_status()
        return {
            "status": "success",
            "failure_learning_status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting Horus failure learning status: {e}")
        return {"status": "error", "error": str(e)}

@router.get("/horus/failure-analysis-report")
async def get_horus_failure_analysis_report() -> Dict[str, Any]:
    """Get comprehensive failure analysis report from Project Horus"""
    try:
        report = await enhanced_project_horus_service.get_failure_analysis_report()
        return {
            "status": "success",
            "failure_analysis_report": report,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting Horus failure analysis report: {e}")
        return {"status": "error", "error": str(e)}

@router.post("/berserk/learn-from-failure")
async def berserk_learn_from_failure(failure_data: Dict[str, Any]) -> Dict[str, Any]:
    """Trigger Project Berserk to learn from a failure"""
    try:
        result = await project_berserk_enhanced_service.learn_from_failure(failure_data)
        return {
            "status": "success",
            "learning_result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error triggering Berserk failure learning: {e}")
        return {"status": "error", "error": str(e)}

@router.get("/berserk/failure-learning-status")
async def get_berserk_failure_learning_status() -> Dict[str, Any]:
    """Get Project Berserk failure learning status"""
    try:
        status = await project_berserk_enhanced_service.get_failure_learning_status()
        return {
            "status": "success",
            "failure_learning_status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting Berserk failure learning status: {e}")
        return {"status": "error", "error": str(e)}

@router.get("/berserk/failure-analysis-report")
async def get_berserk_failure_analysis_report() -> Dict[str, Any]:
    """Get comprehensive failure analysis report from Project Berserk"""
    try:
        report = await project_berserk_enhanced_service.get_failure_analysis_report()
        return {
            "status": "success",
            "failure_analysis_report": report,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting Berserk failure analysis report: {e}")
        return {"status": "error", "error": str(e)}

@router.post("/ai/learn-from-failure")
async def ai_learn_from_failure(failure_data: Dict[str, Any]) -> Dict[str, Any]:
    """Trigger all AIs to learn from a failure"""
    try:
        results = {}
        
        # Trigger Horus learning
        horus_result = await enhanced_project_horus_service.learn_from_failure(failure_data)
        results["horus"] = horus_result
        
        # Trigger Berserk learning
        berserk_result = await project_berserk_enhanced_service.learn_from_failure(failure_data)
        results["berserk"] = berserk_result
        
        return {
            "status": "success",
            "ai_learning_results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error triggering AI failure learning: {e}")
        return {"status": "error", "error": str(e)}


@router.get("/chaos-language/documentation")
async def get_chaos_language_documentation() -> Dict[str, Any]:
    """Get LIVE complete dynamic chaos language documentation"""
    try:
        if not hasattr(chaos_language_service, 'initialized'):
            await chaos_language_service.initialize()
        
        documentation = await chaos_language_service.get_complete_chaos_language_documentation()
        
        return {
            "status": "success",
            "chaos_language_documentation": documentation
        }
        
    except Exception as e:
        logger.error(f"Error getting LIVE chaos language documentation: {e}")
        raise HTTPException(status_code=500, detail=f"LIVE chaos language documentation failed: {str(e)}")


@router.post("/chaos-language/collect-constructs")
async def collect_chaos_language_constructs() -> Dict[str, Any]:
    """Collect LIVE new constructs from system and update chaos language"""
    try:
        if not hasattr(chaos_language_service, 'initialized'):
            await chaos_language_service.initialize()
        
        result = await chaos_language_service.collect_new_constructs_from_system()
        
        return {
            "status": "success",
            "message": "LIVE construct collection completed",
            "collection_results": result
        }
        
    except Exception as e:
        logger.error(f"Error collecting LIVE chaos language constructs: {e}")
        raise HTTPException(status_code=500, detail=f"LIVE chaos language construct collection failed: {str(e)}")


@router.post("/chaos-language/force-chapter")
async def force_chaos_language_chapter() -> Dict[str, Any]:
    """Force generation of LIVE new chaos language chapter"""
    try:
        if not hasattr(chaos_language_service, 'initialized'):
            await chaos_language_service.initialize()
        
        result = await chaos_language_service.force_chapter_generation()
        
        return {
            "status": "success",
            "chapter_generation_result": result
        }
        
    except Exception as e:
        logger.error(f"Error forcing LIVE chaos language chapter generation: {e}")
        raise HTTPException(status_code=500, detail=f"LIVE chaos language chapter generation failed: {str(e)}")


@router.post("/horus/learn-from-ais")
async def horus_learn_from_ais(request: LearningIntegrationRequest) -> Dict[str, Any]:
    """Project Horus learns LIVE from other AI experiences"""
    try:
        result = await enhanced_project_horus_service.learn_from_ai_experiences(request.ai_types)
        
        return {
            "status": "success",
            "message": "Project Horus LIVE learning from AI experiences completed",
            "learning_results": result
        }
        
    except Exception as e:
        logger.error(f"Error in Horus LIVE learning from AIs: {e}")
        raise HTTPException(status_code=500, detail=f"Horus LIVE learning failed: {str(e)}")


@router.post("/horus/enhance-weapons")
async def horus_enhance_weapons(complexity_threshold: float = 1.5) -> Dict[str, Any]:
    """Enhance Horus weapons LIVE with internet learning and Docker simulations"""
    try:
        result = await enhanced_project_horus_service.enhance_weapons_with_internet_learning(complexity_threshold)
        
        return {
            "status": "success",
            "message": "LIVE weapon enhancement with internet learning completed",
            "enhancement_results": result
        }
        
    except Exception as e:
        logger.error(f"Error enhancing Horus weapons LIVE: {e}")
        raise HTTPException(status_code=500, detail=f"Horus LIVE weapon enhancement failed: {str(e)}")


@router.post("/berserk/initialize")
async def initialize_berserk() -> Dict[str, Any]:
    """Initialize LIVE Enhanced Project Berserk"""
    try:
        await project_berserk_enhanced_service.initialize()
        
        return {
            "status": "success",
            "message": "Enhanced Project Berserk initialized successfully in LIVE mode"
        }
        
    except Exception as e:
        logger.error(f"Error initializing LIVE Berserk: {e}")
        raise HTTPException(status_code=500, detail=f"LIVE Berserk initialization failed: {str(e)}")


@router.post("/berserk/learn-from-collective")
async def berserk_learn_from_collective(request: LearningIntegrationRequest) -> Dict[str, Any]:
    """Project Berserk learns LIVE from AI collective experiences"""
    try:
        result = await project_berserk_enhanced_service.learn_from_ai_collective(request.ai_types)
        
        return {
            "status": "success",
            "message": "Project Berserk LIVE learning from AI collective completed",
            "learning_results": result
        }
        
    except Exception as e:
        logger.error(f"Error in Berserk LIVE learning from collective: {e}")
        raise HTTPException(status_code=500, detail=f"Berserk LIVE collective learning failed: {str(e)}")


@router.get("/berserk/status")
async def get_berserk_status() -> Dict[str, Any]:
    """Get comprehensive LIVE Project Berserk status report"""
    try:
        status_report = await project_berserk_enhanced_service.get_berserk_status_report()
        
        return {
            "status": "success",
            "berserk_status": status_report
        }
        
    except Exception as e:
        logger.error(f"Error getting LIVE Berserk status: {e}")
        raise HTTPException(status_code=500, detail=f"LIVE Berserk status failed: {str(e)}")


@router.post("/adversarial-training/schedule")
async def schedule_adversarial_training(request: AdversarialTrainingRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Schedule LIVE adversarial training as background task"""
    try:
        background_tasks.add_task(
            ai_adversarial_integration_service.run_scheduled_adversarial_training,
            request.ai_type
        )
        
        return {
            "status": "success",
            "message": f"LIVE adversarial training scheduled for {request.ai_type}",
            "scheduled_at": "background_task"
        }
        
    except Exception as e:
        logger.error(f"Error scheduling LIVE adversarial training: {e}")
        raise HTTPException(status_code=500, detail=f"LIVE adversarial training scheduling failed: {str(e)}")


@router.post("/integration/full-cycle")
async def run_full_integration_cycle(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Run LIVE full AI integration cycle as background task"""
    try:
        async def full_cycle():
            # Run LIVE adversarial training for all AIs
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            for ai_type in ai_types:
                await ai_adversarial_integration_service.run_scheduled_adversarial_training(ai_type)
            
            # Horus learns LIVE from AI experiences
            await enhanced_project_horus_service.learn_from_ai_experiences(ai_types)
            
            # Enhance Horus weapons LIVE
            await enhanced_project_horus_service.enhance_weapons_with_internet_learning()
            
            # Berserk learns LIVE from collective
            await project_berserk_enhanced_service.learn_from_ai_collective(ai_types)
            
            # Create new LIVE synthetic weapons
            await project_berserk_enhanced_service.create_synthetic_growing_weapons(2)
        
        background_tasks.add_task(full_cycle)
        
        return {
            "status": "success",
            "message": "LIVE full AI integration cycle started as background task",
            "includes": [
                "LIVE Adversarial training for all AIs",
                "LIVE Project Horus learning from AI experiences",
                "LIVE Weapon enhancement with internet learning",
                "LIVE Project Berserk collective learning",
                "LIVE Synthetic weapon creation"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error running LIVE full integration cycle: {e}")
        raise HTTPException(status_code=500, detail=f"LIVE full integration cycle failed: {str(e)}")