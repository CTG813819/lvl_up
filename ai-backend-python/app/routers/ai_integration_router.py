"""
AI Integration Router
Routes for integrated AI adversarial learning and weapon systems
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import structlog

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


class LearningIntegrationRequest(BaseModel):
    ai_types: Optional[List[str]] = None


@router.post("/adversarial-training/run")
async def run_adversarial_training(request: AdversarialTrainingRequest) -> Dict[str, Any]:
    """Run adversarial training for specific AI"""
    try:
        if not hasattr(ai_adversarial_integration_service, 'initialized') or not ai_adversarial_integration_service.initialized:
            await ai_adversarial_integration_service.initialize()
        
        result = await ai_adversarial_integration_service.integrate_adversarial_scenario_into_ai_learning(
            request.ai_type, 
            request.force_scenario
        )
        
        return {
            "status": "success",
            "message": f"Adversarial training completed for {request.ai_type}",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error running adversarial training: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/adversarial-training/progress")
async def get_adversarial_progress() -> Dict[str, Any]:
    """Get adversarial training progress for all AIs"""
    try:
        if not hasattr(ai_adversarial_integration_service, 'initialized'):
            await ai_adversarial_integration_service.initialize()
        
        report = await ai_adversarial_integration_service.get_adversarial_progress_report()
        
        return {
            "status": "success",
            "progress_report": report
        }
        
    except Exception as e:
        logger.error(f"Error getting adversarial progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/adversarial-training/schedule")
async def schedule_adversarial_training(request: AdversarialTrainingRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Schedule adversarial training as background task"""
    try:
        background_tasks.add_task(
            ai_adversarial_integration_service.run_scheduled_adversarial_training,
            request.ai_type
        )
        
        return {
            "status": "success",
            "message": f"Adversarial training scheduled for {request.ai_type}",
            "scheduled_at": "background_task"
        }
        
    except Exception as e:
        logger.error(f"Error scheduling adversarial training: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/horus/learn-from-ais")
async def horus_learn_from_ais(request: LearningIntegrationRequest) -> Dict[str, Any]:
    """Project Horus learns from other AI experiences"""
    try:
        result = await enhanced_project_horus_service.learn_from_ai_experiences(request.ai_types)
        
        return {
            "status": "success",
            "message": "Project Horus learning from AI experiences completed",
            "learning_results": result
        }
        
    except Exception as e:
        logger.error(f"Error in Horus learning from AIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/horus/enhance-weapons")
async def horus_enhance_weapons(complexity_threshold: float = 1.5) -> Dict[str, Any]:
    """Enhance Horus weapons with internet learning and Docker simulations"""
    try:
        result = await enhanced_project_horus_service.enhance_weapons_with_internet_learning(complexity_threshold)
        
        return {
            "status": "success",
            "message": "Weapon enhancement with internet learning completed",
            "enhancement_results": result
        }
        
    except Exception as e:
        logger.error(f"Error enhancing Horus weapons: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chaos-language/documentation")
async def get_chaos_language_documentation() -> Dict[str, Any]:
    """Get complete dynamic chaos language documentation"""
    try:
        if not hasattr(chaos_language_service, 'initialized'):
            await chaos_language_service.initialize()
        
        documentation = await chaos_language_service.get_complete_chaos_language_documentation()
        
        return {
            "status": "success",
            "chaos_language_documentation": documentation
        }
        
    except Exception as e:
        logger.error(f"Error getting chaos language documentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chaos-language/collect-constructs")
async def collect_chaos_language_constructs() -> Dict[str, Any]:
    """Collect new constructs from system and update chaos language"""
    try:
        if not hasattr(chaos_language_service, 'initialized'):
            await chaos_language_service.initialize()
        
        result = await chaos_language_service.collect_new_constructs_from_system()
        
        return {
            "status": "success",
            "message": "Construct collection completed",
            "collection_results": result
        }
        
    except Exception as e:
        logger.error(f"Error collecting chaos language constructs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chaos-language/force-chapter")
async def force_chaos_language_chapter() -> Dict[str, Any]:
    """Force generation of new chaos language chapter"""
    try:
        if not hasattr(chaos_language_service, 'initialized'):
            await chaos_language_service.initialize()
        
        result = await chaos_language_service.force_chapter_generation()
        
        return {
            "status": "success",
            "chapter_generation_result": result
        }
        
    except Exception as e:
        logger.error(f"Error forcing chaos language chapter generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/horus/weapon-synthesis-report")
async def get_weapon_synthesis_report() -> Dict[str, Any]:
    """Get weapon synthesis report from Project Horus"""
    try:
        report = await enhanced_project_horus_service.get_weapon_synthesis_report()
        
        return {
            "status": "success",
            "synthesis_report": report
        }
        
    except Exception as e:
        logger.error(f"Error getting weapon synthesis report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/berserk/initialize")
async def initialize_berserk() -> Dict[str, Any]:
    """Initialize Enhanced Project Berserk"""
    try:
        await project_berserk_enhanced_service.initialize()
        
        return {
            "status": "success",
            "message": "Enhanced Project Berserk initialized successfully"
        }
        
    except Exception as e:
        logger.error(f"Error initializing Berserk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/berserk/learn-from-collective")
async def berserk_learn_from_collective(request: LearningIntegrationRequest) -> Dict[str, Any]:
    """Project Berserk learns from AI collective experiences"""
    try:
        result = await project_berserk_enhanced_service.learn_from_ai_collective(request.ai_types)
        
        return {
            "status": "success",
            "message": "Project Berserk learning from AI collective completed",
            "learning_results": result
        }
        
    except Exception as e:
        logger.error(f"Error in Berserk learning from collective: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/berserk/create-weapons")
async def create_synthetic_weapons(count: int = 3) -> Dict[str, Any]:
    """Create synthetic self-growing weapons"""
    try:
        result = await project_berserk_enhanced_service.create_synthetic_growing_weapons(count)
        
        return {
            "status": "success",
            "message": f"Created {result.get('weapons_created', 0)} synthetic weapons",
            "creation_results": result
        }
        
    except Exception as e:
        logger.error(f"Error creating synthetic weapons: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/berserk/deploy-weapon")
async def deploy_weapon(request: WeaponDeploymentRequest) -> Dict[str, Any]:
    """Deploy weapon with specified deployment option"""
    try:
        result = await project_berserk_enhanced_service.deploy_weapon(
            request.weapon_id,
            request.target_system,
            request.deployment_option
        )
        
        return {
            "status": "success" if result.get("success", False) else "failed",
            "message": "Weapon deployment completed",
            "deployment_result": result
        }
        
    except Exception as e:
        logger.error(f"Error deploying weapon: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/berserk/status")
async def get_berserk_status() -> Dict[str, Any]:
    """Get comprehensive Project Berserk status report"""
    try:
        status_report = await project_berserk_enhanced_service.get_berserk_status_report()
        
        return {
            "status": "success",
            "berserk_status": status_report
        }
        
    except Exception as e:
        logger.error(f"Error getting Berserk status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/integration/status")
async def get_integration_status() -> Dict[str, Any]:
    """Get overall AI integration status"""
    try:
        # Get status from all services
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
                "backend_integration": "complete"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting integration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/integration/full-cycle")
async def run_full_integration_cycle(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Run full AI integration cycle as background task"""
    try:
        async def full_cycle():
            # Run adversarial training for all AIs
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            for ai_type in ai_types:
                await ai_adversarial_integration_service.run_scheduled_adversarial_training(ai_type)
            
            # Horus learns from AI experiences
            await enhanced_project_horus_service.learn_from_ai_experiences(ai_types)
            
            # Enhance Horus weapons
            await enhanced_project_horus_service.enhance_weapons_with_internet_learning()
            
            # Berserk learns from collective
            await project_berserk_enhanced_service.learn_from_ai_collective(ai_types)
            
            # Create new synthetic weapons
            await project_berserk_enhanced_service.create_synthetic_growing_weapons(2)
        
        background_tasks.add_task(full_cycle)
        
        return {
            "status": "success",
            "message": "Full AI integration cycle started as background task",
            "includes": [
                "Adversarial training for all AIs",
                "Project Horus learning from AI experiences",
                "Weapon enhancement with internet learning",
                "Project Berserk collective learning",
                "Synthetic weapon creation"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error running full integration cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))