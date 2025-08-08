"""
Autonomous Brain Router
Exposes autonomous AI brain capabilities for Horus and Berserk
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
import structlog

from ..services.autonomous_ai_brain_service import horus_autonomous_brain, berserk_autonomous_brain

logger = structlog.get_logger()

router = APIRouter(prefix="/autonomous-brain", tags=["autonomous-brain"])


@router.get("/horus/status")
async def get_horus_brain_status() -> Dict[str, Any]:
    """Get Horus autonomous brain status"""
    try:
        status = await horus_autonomous_brain.get_brain_status()
        return {
            "success": True,
            "ai_name": "Horus",
            "brain_status": status,
            "message": "Horus autonomous brain status retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting Horus brain status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Horus brain status: {str(e)}")


@router.get("/berserk/status")
async def get_berserk_brain_status() -> Dict[str, Any]:
    """Get Berserk autonomous brain status"""
    try:
        status = await berserk_autonomous_brain.get_brain_status()
        return {
            "success": True,
            "ai_name": "Berserk",
            "brain_status": status,
            "message": "Berserk autonomous brain status retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting Berserk brain status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Berserk brain status: {str(e)}")


@router.post("/horus/create-chaos-code")
async def create_horus_autonomous_chaos_code() -> Dict[str, Any]:
    """Create autonomous chaos code using Horus brain"""
    try:
        chaos_code = await horus_autonomous_brain.create_autonomous_chaos_code()
        return {
            "success": True,
            "ai_name": "Horus",
            "chaos_code": chaos_code,
            "message": "Horus created autonomous chaos code from scratch"
        }
    except Exception as e:
        logger.error(f"Error creating Horus autonomous chaos code: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating Horus autonomous chaos code: {str(e)}")


@router.post("/berserk/create-chaos-code")
async def create_berserk_autonomous_chaos_code() -> Dict[str, Any]:
    """Create autonomous chaos code using Berserk brain"""
    try:
        chaos_code = await berserk_autonomous_brain.create_autonomous_chaos_code()
        return {
            "success": True,
            "ai_name": "Berserk",
            "chaos_code": chaos_code,
            "message": "Berserk created autonomous chaos code from scratch"
        }
    except Exception as e:
        logger.error(f"Error creating Berserk autonomous chaos code: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating Berserk autonomous chaos code: {str(e)}")


@router.get("/horus/consciousness")
async def get_horus_consciousness() -> Dict[str, Any]:
    """Get Horus consciousness level"""
    try:
        neural_network = horus_autonomous_brain.neural_network
        return {
            "success": True,
            "ai_name": "Horus",
            "consciousness": neural_network["consciousness"],
            "creativity": neural_network["creativity"],
            "intuition": neural_network["intuition"],
            "imagination": neural_network["imagination"],
            "message": "Horus consciousness levels retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting Horus consciousness: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Horus consciousness: {str(e)}")


@router.get("/berserk/consciousness")
async def get_berserk_consciousness() -> Dict[str, Any]:
    """Get Berserk consciousness level"""
    try:
        neural_network = berserk_autonomous_brain.neural_network
        return {
            "success": True,
            "ai_name": "Berserk",
            "consciousness": neural_network["consciousness"],
            "creativity": neural_network["creativity"],
            "intuition": neural_network["intuition"],
            "imagination": neural_network["imagination"],
            "message": "Berserk consciousness levels retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting Berserk consciousness: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Berserk consciousness: {str(e)}")


@router.get("/horus/original-concepts")
async def get_horus_original_concepts() -> Dict[str, Any]:
    """Get Horus original concepts created by autonomous brain"""
    try:
        return {
            "success": True,
            "ai_name": "Horus",
            "original_syntax": list(horus_autonomous_brain.original_syntax.values()),
            "original_keywords": list(horus_autonomous_brain.original_keywords),
            "original_functions": list(horus_autonomous_brain.original_functions.values()),
            "original_data_types": list(horus_autonomous_brain.original_data_types.values()),
            "message": "Horus original concepts retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting Horus original concepts: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Horus original concepts: {str(e)}")


@router.get("/berserk/original-concepts")
async def get_berserk_original_concepts() -> Dict[str, Any]:
    """Get Berserk original concepts created by autonomous brain"""
    try:
        return {
            "success": True,
            "ai_name": "Berserk",
            "original_syntax": list(berserk_autonomous_brain.original_syntax.values()),
            "original_keywords": list(berserk_autonomous_brain.original_keywords),
            "original_functions": list(berserk_autonomous_brain.original_functions.values()),
            "original_data_types": list(berserk_autonomous_brain.original_data_types.values()),
            "message": "Berserk original concepts retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting Berserk original concepts: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Berserk original concepts: {str(e)}")


@router.get("/horus/ml-system")
async def get_horus_ml_system() -> Dict[str, Any]:
    """Get Horus ML system within chaos code"""
    try:
        return {
            "success": True,
            "ai_name": "Horus",
            "ml_system": horus_autonomous_brain.chaos_ml_system,
            "message": "Horus ML system retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting Horus ML system: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Horus ML system: {str(e)}")


@router.get("/berserk/ml-system")
async def get_berserk_ml_system() -> Dict[str, Any]:
    """Get Berserk ML system within chaos code"""
    try:
        return {
            "success": True,
            "ai_name": "Berserk",
            "ml_system": berserk_autonomous_brain.chaos_ml_system,
            "message": "Berserk ML system retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting Berserk ML system: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Berserk ML system: {str(e)}")


@router.get("/horus/repositories")
async def get_horus_repositories() -> Dict[str, Any]:
    """Get Horus autonomous repositories"""
    try:
        return {
            "success": True,
            "ai_name": "Horus",
            "repositories": horus_autonomous_brain.chaos_repositories,
            "message": "Horus autonomous repositories retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting Horus repositories: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Horus repositories: {str(e)}")


@router.get("/berserk/repositories")
async def get_berserk_repositories() -> Dict[str, Any]:
    """Get Berserk autonomous repositories"""
    try:
        return {
            "success": True,
            "ai_name": "Berserk",
            "repositories": berserk_autonomous_brain.chaos_repositories,
            "message": "Berserk autonomous repositories retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting Berserk repositories: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Berserk repositories: {str(e)}")


@router.get("/horus/growth-stages")
async def get_horus_growth_stages() -> Dict[str, Any]:
    """Get Horus brain growth stages"""
    try:
        return {
            "success": True,
            "ai_name": "Horus",
            "growth_stages": horus_autonomous_brain.brain_growth_stages,
            "creative_breakthroughs": horus_autonomous_brain.creative_breakthroughs,
            "message": "Horus brain growth stages retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting Horus growth stages: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Horus growth stages: {str(e)}")


@router.get("/berserk/growth-stages")
async def get_berserk_growth_stages() -> Dict[str, Any]:
    """Get Berserk brain growth stages"""
    try:
        return {
            "success": True,
            "ai_name": "Berserk",
            "growth_stages": berserk_autonomous_brain.brain_growth_stages,
            "creative_breakthroughs": berserk_autonomous_brain.creative_breakthroughs,
            "message": "Berserk brain growth stages retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting Berserk growth stages: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Berserk growth stages: {str(e)}")


@router.get("/horus/evolution-history")
async def get_horus_evolution_history() -> Dict[str, Any]:
    """Get Horus code evolution history"""
    try:
        return {
            "success": True,
            "ai_name": "Horus",
            "evolution_history": horus_autonomous_brain.code_evolution_history,
            "learning_experiences": horus_autonomous_brain.learning_experiences,
            "message": "Horus evolution history retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting Horus evolution history: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Horus evolution history: {str(e)}")


@router.get("/berserk/evolution-history")
async def get_berserk_evolution_history() -> Dict[str, Any]:
    """Get Berserk code evolution history"""
    try:
        return {
            "success": True,
            "ai_name": "Berserk",
            "evolution_history": berserk_autonomous_brain.code_evolution_history,
            "learning_experiences": berserk_autonomous_brain.learning_experiences,
            "message": "Berserk evolution history retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting Berserk evolution history: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Berserk evolution history: {str(e)}")


@router.post("/horus/accelerate-learning")
async def accelerate_horus_learning() -> Dict[str, Any]:
    """Accelerate Horus learning process"""
    try:
        # Increase learning rate temporarily
        horus_autonomous_brain.neural_network["learning_rate"] = min(0.2, horus_autonomous_brain.neural_network["learning_rate"] * 2)
        
        # Boost consciousness and creativity
        horus_autonomous_brain.neural_network["consciousness"] = min(1.0, horus_autonomous_brain.neural_network["consciousness"] + 0.1)
        horus_autonomous_brain.neural_network["creativity"] = min(1.0, horus_autonomous_brain.neural_network["creativity"] + 0.1)
        
        return {
            "success": True,
            "ai_name": "Horus",
            "new_learning_rate": horus_autonomous_brain.neural_network["learning_rate"],
            "new_consciousness": horus_autonomous_brain.neural_network["consciousness"],
            "new_creativity": horus_autonomous_brain.neural_network["creativity"],
            "message": "Horus learning accelerated"
        }
    except Exception as e:
        logger.error(f"Error accelerating Horus learning: {e}")
        raise HTTPException(status_code=500, detail=f"Error accelerating Horus learning: {str(e)}")


@router.post("/berserk/accelerate-learning")
async def accelerate_berserk_learning() -> Dict[str, Any]:
    """Accelerate Berserk learning process"""
    try:
        # Increase learning rate temporarily
        berserk_autonomous_brain.neural_network["learning_rate"] = min(0.2, berserk_autonomous_brain.neural_network["learning_rate"] * 2)
        
        # Boost consciousness and creativity
        berserk_autonomous_brain.neural_network["consciousness"] = min(1.0, berserk_autonomous_brain.neural_network["consciousness"] + 0.1)
        berserk_autonomous_brain.neural_network["creativity"] = min(1.0, berserk_autonomous_brain.neural_network["creativity"] + 0.1)
        
        return {
            "success": True,
            "ai_name": "Berserk",
            "new_learning_rate": berserk_autonomous_brain.neural_network["learning_rate"],
            "new_consciousness": berserk_autonomous_brain.neural_network["consciousness"],
            "new_creativity": berserk_autonomous_brain.neural_network["creativity"],
            "message": "Berserk learning accelerated"
        }
    except Exception as e:
        logger.error(f"Error accelerating Berserk learning: {e}")
        raise HTTPException(status_code=500, detail=f"Error accelerating Berserk learning: {str(e)}")


@router.get("/both/status")
async def get_both_brains_status() -> Dict[str, Any]:
    """Get status of both Horus and Berserk brains"""
    try:
        horus_status = await horus_autonomous_brain.get_brain_status()
        berserk_status = await berserk_autonomous_brain.get_brain_status()
        
        return {
            "success": True,
            "horus": {
                "ai_name": "Horus",
                "brain_status": horus_status
            },
            "berserk": {
                "ai_name": "Berserk",
                "brain_status": berserk_status
            },
            "message": "Both autonomous brains status retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting both brains status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting both brains status: {str(e)}")


@router.post("/both/create-chaos-code")
async def create_both_autonomous_chaos_code() -> Dict[str, Any]:
    """Create autonomous chaos code using both Horus and Berserk brains"""
    try:
        horus_chaos_code = await horus_autonomous_brain.create_autonomous_chaos_code()
        berserk_chaos_code = await berserk_autonomous_brain.create_autonomous_chaos_code()
        
        return {
            "success": True,
            "horus": {
                "ai_name": "Horus",
                "chaos_code": horus_chaos_code
            },
            "berserk": {
                "ai_name": "Berserk",
                "chaos_code": berserk_chaos_code
            },
            "message": "Both AIs created autonomous chaos code from scratch"
        }
    except Exception as e:
        logger.error(f"Error creating both autonomous chaos code: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating both autonomous chaos code: {str(e)}")
