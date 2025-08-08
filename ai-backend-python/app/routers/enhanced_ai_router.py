"""
Enhanced AI Router
Provides endpoints for proactive and creative AI behavior
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List
import structlog
from datetime import datetime

from ..core.database import get_db
from ..services.enhanced_ai_coordinator import EnhancedAICoordinator
from ..services.ai_learning_service import AILearningService

logger = structlog.get_logger()
router = APIRouter(prefix="/enhanced-ai", tags=["Enhanced AI"])


@router.post("/run-cycle")
async def run_enhanced_ai_cycle(background_tasks: BackgroundTasks):
    """Run enhanced AI cycle where AIs are proactive and creative"""
    try:
        logger.info("🚀 Triggering Enhanced AI Cycle - AIs will be proactive and creative!")
        
        # Run the enhanced AI cycle
        coordinator = EnhancedAICoordinator()
        result = await coordinator.run_enhanced_ai_cycle()
        
        # Add background task for learning
        background_tasks.add_task(_learn_from_enhanced_cycle, result)
        
        return {
            "status": "success",
            "message": "Enhanced AI cycle started successfully",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error running enhanced AI cycle: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-ai/{ai_type}")
async def run_enhanced_ai_agent(ai_type: str, background_tasks: BackgroundTasks):
    """Run a specific AI agent with enhanced capabilities"""
    try:
        logger.info(f"🤖 Running enhanced {ai_type} AI agent")
        
        coordinator = EnhancedAICoordinator()
        
        # Get AI directive
        if ai_type not in coordinator.ai_directives:
            raise HTTPException(status_code=400, detail=f"Unknown AI type: {ai_type}")
        
        directive = coordinator.ai_directives[ai_type]
        result = await coordinator._run_enhanced_ai_agent(ai_type, directive)
        
        # Add background task for learning
        background_tasks.add_task(_learn_from_ai_agent, ai_type, result)
        
        return {
            "status": "success",
            "message": f"Enhanced {ai_type} AI agent completed",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error running enhanced {ai_type} AI agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-creative-code/{ai_type}")
async def generate_creative_code(ai_type: str):
    """Generate creative code for a specific AI type"""
    try:
        logger.info(f"✨ Generating creative code for {ai_type}")
        
        coordinator = EnhancedAICoordinator()
        
        if ai_type not in coordinator.ai_directives:
            raise HTTPException(status_code=400, detail=f"Unknown AI type: {ai_type}")
        
        directive = coordinator.ai_directives[ai_type]
        new_code_generated = await coordinator._generate_creative_code(ai_type, directive)
        
        return {
            "status": "success",
            "message": f"Generated {new_code_generated} new code files for {ai_type}",
            "ai_type": ai_type,
            "new_code_generated": new_code_generated,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating creative code for {ai_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_enhanced_ai_status():
    """Get status of enhanced AI system"""
    try:
        coordinator = EnhancedAICoordinator()
        
        status = {
            "ai_directives": coordinator.ai_directives,
            "system_status": "active",
            "capabilities": {
                "proactive_scanning": True,
                "creative_code_generation": True,
                "rigorous_testing": True,
                "live_deployment": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting enhanced AI status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply-proposal/{proposal_id}")
async def apply_proposal_live(proposal_id: str):
    """Apply a specific proposal live"""
    try:
        logger.info(f"🚀 Applying proposal {proposal_id} live")
        
        from ..models.sql_models import Proposal
        from sqlalchemy import select
        
        async with get_db() as db:
            # Get proposal
            query = select(Proposal).where(Proposal.id == proposal_id)
            result = await db.execute(query)
            proposal = result.scalar_one_or_none()
            
            if not proposal:
                raise HTTPException(status_code=404, detail="Proposal not found")
            
            # Check if proposal passed testing
            if proposal.test_status != "passed":
                raise HTTPException(
                    status_code=400, 
                    detail="Proposal must pass testing before being applied"
                )
            
            # Apply the proposal
            coordinator = EnhancedAICoordinator()
            success = await coordinator._apply_proposal_live(proposal)
            
            if success:
                proposal.status = "applied"
                proposal.user_feedback = "applied"
                await db.commit()
                
                return {
                    "status": "success",
                    "message": f"Proposal {proposal_id} applied successfully",
                    "proposal_id": proposal_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to apply proposal"
                )
        
    except Exception as e:
        logger.error(f"Error applying proposal {proposal_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def _learn_from_enhanced_cycle(result: Dict[str, Any]):
    """Learn from enhanced AI cycle results"""
    try:
        learning_service = AILearningService()
        
        # Extract learning data
        total_proposals = result.get("total_proposals_created", 0)
        total_new_code = result.get("total_new_code_generated", 0)
        ai_results = result.get("ai_results", {})
        
        # Create learning entry
        learning_entry = {
            "ai_type": "enhanced_coordinator",
            "learning_type": "enhanced_cycle",
            "pattern": f"enhanced_cycle_{total_proposals}_proposals_{total_new_code}_new_code",
            "context": "Enhanced AI cycle with proactive and creative behavior",
            "feedback": f"Created {total_proposals} proposals, generated {total_new_code} new code files",
            "confidence": 0.9,
            "created_at": datetime.utcnow()
        }
        
        await learning_service.learn_from_pattern(**learning_entry)
        
        logger.info(f"📚 Learned from enhanced AI cycle: {total_proposals} proposals, {total_new_code} new code")
        
    except Exception as e:
        logger.error(f"Error learning from enhanced cycle: {str(e)}")


async def _learn_from_ai_agent(ai_type: str, result: Dict[str, Any]):
    """Learn from individual AI agent results"""
    try:
        learning_service = AILearningService()
        
        # Extract learning data
        proposals_created = result.get("proposals_created", 0)
        new_code_generated = result.get("new_code_generated", 0)
        proposals_applied = result.get("proposals_applied", 0)
        
        # Create learning entry
        learning_entry = {
            "ai_type": ai_type,
            "learning_type": "enhanced_agent",
            "pattern": f"enhanced_{ai_type}_{proposals_created}_proposals_{new_code_generated}_new_code",
            "context": f"Enhanced {ai_type} agent with proactive and creative behavior",
            "feedback": f"Created {proposals_created} proposals, generated {new_code_generated} new code, applied {proposals_applied}",
            "confidence": 0.8,
            "created_at": datetime.utcnow()
        }
        
        await learning_service.learn_from_pattern(**learning_entry)
        
        logger.info(f"📚 Learned from enhanced {ai_type} agent: {proposals_created} proposals, {new_code_generated} new code")
        
    except Exception as e:
        logger.error(f"Error learning from {ai_type} agent: {str(e)}") 