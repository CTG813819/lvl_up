"""
Proposals router with ML integration
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
import json
from datetime import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload

from app.models.proposal import ProposalCreate, ProposalUpdate, ProposalResponse, ProposalStats
from app.models.sql_models import Proposal
from app.core.database import get_session
from app.services.ml_service import MLService
from app.services.ai_learning_service import AILearningService

logger = structlog.get_logger()
router = APIRouter()

ml_service = MLService()
ai_learning_service = AILearningService()


@router.post("/", response_model=ProposalResponse)
async def create_proposal(proposal: ProposalCreate, db: AsyncSession = Depends(get_session)):
    """Create a new proposal with ML analysis and workflow limiting, with deduplication and confidence clamping"""
    try:
        # Check current pending proposal count
        pending_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
        pending_result = await db.execute(pending_query)
        pending_count = pending_result.scalar()
        
        # Limit to 10 pending proposals
        if pending_count >= 10:
            raise HTTPException(
                status_code=429, 
                detail="Maximum pending proposals reached (10). Please review existing proposals before creating new ones."
            )
        
        # Deduplication: check for existing proposal with same code_hash or semantic_hash
        duplicate_query = select(Proposal).where(
            (Proposal.code_hash == proposal.code_hash) | (Proposal.semantic_hash == proposal.semantic_hash),
            Proposal.status != "rejected"
        )
        duplicate_result = await db.execute(duplicate_query)
        duplicate = duplicate_result.scalar_one_or_none()
        if duplicate:
            raise HTTPException(status_code=409, detail="Duplicate proposal already exists.")
        
        # Convert to dict for ML analysis
        proposal_dict = proposal.dict()
        
        # Analyze proposal quality using ML
        ml_analysis = await ml_service.analyze_proposal_quality(proposal_dict)
        
        # Clamp confidence
        confidence = ml_analysis.get("quality_score", 0.5)
        confidence = min(max(confidence, 0.0), 1.0)
        
        # Create new proposal instance with SQLAlchemy model
        new_proposal = Proposal(
            ai_type=proposal.ai_type,
            file_path=proposal.file_path,
            code_before=proposal.code_before,
            code_after=proposal.code_after,
            status=proposal.status,
            result=proposal.result,
            user_feedback=proposal.user_feedback,
            test_status=proposal.test_status,
            test_output=proposal.test_output,
            code_hash=proposal.code_hash,
            semantic_hash=proposal.semantic_hash,
            diff_score=proposal.diff_score,
            duplicate_of=proposal.duplicate_of,
            ai_reasoning=proposal.ai_reasoning + f"\n\nML Analysis: Quality Score: {confidence:.2f}, Approval Probability: {ml_analysis.get('approval_probability', 0.5):.2f}" if proposal.ai_reasoning else f"ML Analysis: Quality Score: {confidence:.2f}, Approval Probability: {ml_analysis.get('approval_probability', 0.5):.2f}",
            learning_context=proposal.learning_context,
            mistake_pattern=proposal.mistake_pattern,
            improvement_type=proposal.improvement_type,
            confidence=confidence,
            user_feedback_reason=proposal.user_feedback_reason,
            ai_learning_applied=proposal.ai_learning_applied,
            previous_mistakes_avoided=proposal.previous_mistakes_avoided
        )
        
        db.add(new_proposal)
        await db.commit()
        await db.refresh(new_proposal)
        
        logger.info("Proposal created with ML analysis", 
                   proposal_id=str(new_proposal.id),
                   quality_score=confidence,
                   pending_count=pending_count + 1)
        
        return ProposalResponse.from_orm(new_proposal)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("Error creating proposal", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ProposalResponse])
async def list_proposals(status: Optional[str] = None, ai_type: Optional[str] = None):
    session = get_session()
    async with session as s:
        query = select(Proposal).order_by(Proposal.created_at.desc())
        if status:
            query = query.where(Proposal.status == status)
        if ai_type:
            query = query.where(Proposal.ai_type == ai_type)
        result = await s.execute(query)
        proposals = result.scalars().all()
        return [ProposalResponse.from_orm(p) for p in proposals]

@router.post("/{proposal_id}/accept")
async def accept_proposal(proposal_id: str):
    session = get_session()
    async with session as s:
        # Check if this is an agent ID (sandbox, imperium, guardian, conquest)
        agent_types = ["sandbox", "imperium", "guardian", "conquest"]
        if proposal_id.lower() in agent_types:
            # This is an agent approval - run the agent instead
            try:
                from app.services.ai_agent_service import AIAgentService
                ai_agent_service = AIAgentService()
                
                agent_type = proposal_id.lower()
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
                
                return {
                    "status": "success",
                    "test_status": "passed",
                    "test_output": f"Agent {agent_type} executed successfully",
                    "overall_result": "passed",
                    "agent_result": result,
                    "message": f"Agent {agent_type} has been triggered and executed"
                }
            except Exception as e:
                logger.error(f"Error running agent {proposal_id}: {str(e)}")
                return {
                    "status": "error",
                    "test_status": "error",
                    "test_output": f"Agent execution failed: {str(e)}",
                    "overall_result": "failed"
                }
        
        # Original proposal approval logic
        proposal = await s.get(Proposal, proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        # Set status to testing first
        proposal.status = "testing"
        proposal.user_feedback = "accepted"
        proposal.test_status = "pending"
        await s.commit()
        
        try:
            # Import testing service
            from app.services.testing_service import testing_service
            
            # Prepare proposal data for testing
            proposal_data = {
                "id": str(proposal.id),
                "ai_type": proposal.ai_type,
                "file_path": proposal.file_path,
                "code_before": proposal.code_before,
                "code_after": proposal.code_after,
                "improvement_type": proposal.improvement_type,
                "confidence": proposal.confidence,
            }
            
            # Run tests
            overall_result, summary, detailed_results = await testing_service.test_proposal(proposal_data)
            
            # Update proposal based on test results
            if overall_result.value == "passed":
                proposal.status = "accepted"
                proposal.test_status = "passed"
                proposal.test_output = summary
            elif overall_result.value == "failed":
                proposal.status = "test-failed"
                proposal.test_status = "failed"
                proposal.test_output = summary
            else:  # error or skipped
                proposal.status = "test-failed"
                proposal.test_status = "error"
                proposal.test_output = summary
            
            # Store detailed test results as JSON
            detailed_results_json = [result.to_dict() for result in detailed_results]
            proposal.result = json.dumps(detailed_results_json)
            
            await s.commit()
            
            return {
                "status": "success", 
                "test_status": proposal.test_status, 
                "test_output": proposal.test_output,
                "overall_result": overall_result.value,
                "detailed_results": detailed_results_json
            }
            
        except Exception as e:
            # If testing fails, mark as test error
            proposal.status = "test-failed"
            proposal.test_status = "error"
            proposal.test_output = f"Test execution failed: {str(e)}"
            await s.commit()
            
            logger.error(f"Error testing proposal {proposal_id}: {str(e)}")
            return {
                "status": "error",
                "test_status": "error",
                "test_output": f"Test execution failed: {str(e)}"
            }

@router.post("/{proposal_id}/reject")
async def reject_proposal(proposal_id: str):
    session = get_session()
    async with session as s:
        # Check if this is an agent ID (sandbox, imperium, guardian, conquest)
        agent_types = ["sandbox", "imperium", "guardian", "conquest"]
        if proposal_id.lower() in agent_types:
            # This is an agent rejection - just log it
            agent_type = proposal_id.lower()
            logger.info(f"Agent {agent_type} was rejected by user")
            return {
                "status": "success", 
                "message": f"Agent {agent_type} rejection logged for AI learning.",
                "agent_type": agent_type
            }
        
        # Original proposal rejection logic
        proposal = await s.get(Proposal, proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        proposal.status = "rejected"
        proposal.user_feedback = "rejected"
        await s.commit()
        # Log for learning/experimentation (simulate)
        return {"status": "success", "message": "Proposal rejected and logged for AI learning."}


@router.get("/ai-status")
async def get_ai_status(db: AsyncSession = Depends(get_session)):
    """Get AI status and learning information"""
    try:
        # Get counts for different AI types
        imperium_query = select(func.count(Proposal.id)).where(Proposal.ai_type == "Imperium")
        imperium_result = await db.execute(imperium_query)
        imperium_count = imperium_result.scalar()
        
        sandbox_query = select(func.count(Proposal.id)).where(Proposal.ai_type == "Sandbox")
        sandbox_result = await db.execute(sandbox_query)
        sandbox_count = sandbox_result.scalar()
        
        guardian_query = select(func.count(Proposal.id)).where(Proposal.ai_type == "Guardian")
        guardian_result = await db.execute(guardian_query)
        guardian_count = guardian_result.scalar()
        
        # Get recent activity
        recent_query = select(Proposal).order_by(Proposal.created_at.desc()).limit(5)
        recent_result = await db.execute(recent_query)
        recent_proposals = recent_result.scalars().all()
        
        # Get learning metrics
        try:
            learning_metrics = await ai_learning_service.get_learning_stats("Imperium")
            learning_progress = learning_metrics.get("recent_approval_rate", 0.0)
        except Exception as e:
            logger.warning("Could not get learning stats", error=str(e))
            learning_progress = 0.0
        
        return {
            "status": "active",
            "ai_types": {
                "Imperium": {
                    "total_proposals": imperium_count,
                    "learning_progress": learning_progress,
                    "last_activity": recent_proposals[0].created_at.isoformat() if recent_proposals else None
                },
                "Sandbox": {
                    "total_proposals": sandbox_count,
                    "learning_progress": 0.0,
                    "last_activity": None
                },
                "Guardian": {
                    "total_proposals": guardian_count,
                    "learning_progress": 0.0,
                    "last_activity": None
                }
            },
            "recent_activity": [
                {
                    "id": str(prop.id),
                    "ai_type": prop.ai_type,
                    "status": prop.status,
                    "created_at": prop.created_at.isoformat()
                }
                for prop in recent_proposals
            ],
            "system_health": "healthy",
            "ml_models": "active",
            "github_integration": "not_configured"
        }
        
    except Exception as e:
        logger.error("Error getting AI status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(proposal_id: str, db: AsyncSession = Depends(get_session)):
    """Get a specific proposal by ID"""
    try:
        from uuid import UUID
        
        # Convert string to UUID
        proposal_uuid = UUID(proposal_id)
        
        # Query for proposal
        query = select(Proposal).where(Proposal.id == proposal_uuid)
        result = await db.execute(query)
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        return ProposalResponse.from_orm(proposal)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid proposal ID format")
    except Exception as e:
        logger.error("Error getting proposal", error=str(e), proposal_id=proposal_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{proposal_id}", response_model=ProposalResponse)
async def update_proposal(proposal_id: str, proposal_update: ProposalUpdate, db: AsyncSession = Depends(get_session)):
    """Update a proposal and trigger learning"""
    try:
        from uuid import UUID
        
        # Convert string to UUID
        proposal_uuid = UUID(proposal_id)
        
        # Get existing proposal
        query = select(Proposal).where(Proposal.id == proposal_uuid)
        result = await db.execute(query)
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        # Update proposal fields
        update_data = proposal_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(proposal, field, value)
        
        await db.commit()
        await db.refresh(proposal)
        
        # Trigger learning if status changed
        if "status" in update_data:
            await ai_learning_service.learn_from_proposal(
                proposal_id, 
                update_data["status"], 
                update_data.get("user_feedback_reason")
            )
        
        logger.info("Proposal updated", proposal_id=proposal_id, status=update_data.get("status"))
        
        return ProposalResponse.from_orm(proposal)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid proposal ID format")
    except Exception as e:
        await db.rollback()
        logger.error("Error updating proposal", error=str(e), proposal_id=proposal_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{proposal_id}")
async def delete_proposal(proposal_id: str, db: AsyncSession = Depends(get_session)):
    """Delete a proposal"""
    try:
        from uuid import UUID
        
        # Convert string to UUID
        proposal_uuid = UUID(proposal_id)
        
        # Get existing proposal
        query = select(Proposal).where(Proposal.id == proposal_uuid)
        result = await db.execute(query)
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        # Delete proposal
        await db.delete(proposal)
        await db.commit()
        
        logger.info("Proposal deleted", proposal_id=proposal_id)
        
        return {"message": "Proposal deleted successfully"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid proposal ID format")
    except Exception as e:
        await db.rollback()
        logger.error("Error deleting proposal", error=str(e), proposal_id=proposal_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary", response_model=ProposalStats)
async def get_proposal_stats(db: AsyncSession = Depends(get_session)):
    """Get proposal statistics"""
    try:
        from sqlalchemy import func
        
        # Get counts for different statuses
        total_query = select(func.count(Proposal.id))
        total_result = await db.execute(total_query)
        total = total_result.scalar()
        
        pending_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
        pending_result = await db.execute(pending_query)
        pending = pending_result.scalar()
        
        approved_query = select(func.count(Proposal.id)).where(Proposal.status == "approved")
        approved_result = await db.execute(approved_query)
        approved = approved_result.scalar()
        
        rejected_query = select(func.count(Proposal.id)).where(Proposal.status == "rejected")
        rejected_result = await db.execute(rejected_query)
        rejected = rejected_result.scalar()
        
        applied_query = select(func.count(Proposal.id)).where(Proposal.status == "applied")
        applied_result = await db.execute(applied_query)
        applied = applied_result.scalar()
        
        test_passed_query = select(func.count(Proposal.id)).where(Proposal.status == "test-passed")
        test_passed_result = await db.execute(test_passed_query)
        test_passed = test_passed_result.scalar()
        
        test_failed_query = select(func.count(Proposal.id)).where(Proposal.status == "test-failed")
        test_failed_result = await db.execute(test_failed_query)
        test_failed = test_failed_result.scalar()
        
        return ProposalStats(
            total=total,
            pending=pending,
            approved=approved,
            rejected=rejected,
            applied=applied,
            test_passed=test_passed,
            test_failed=test_failed
        )
        
    except Exception as e:
        logger.error("Error getting proposal stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{proposal_id}/analyze")
async def analyze_proposal(proposal_id: str, db: AsyncSession = Depends(get_session)):
    """Analyze a proposal using ML"""
    try:
        from uuid import UUID
        
        # Convert string to UUID
        proposal_uuid = UUID(proposal_id)
        
        # Get proposal
        query = select(Proposal).where(Proposal.id == proposal_uuid)
        result = await db.execute(query)
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        # Convert to dict for ML analysis
        proposal_dict = {
            "ai_type": proposal.ai_type,
            "file_path": proposal.file_path,
            "code_before": proposal.code_before,
            "code_after": proposal.code_after,
            "status": proposal.status,
            "improvement_type": proposal.improvement_type,
            "confidence": proposal.confidence
        }
        
        # Analyze using ML service
        analysis = await ml_service.analyze_proposal_quality(proposal_dict)
        
        return {
            "proposal_id": proposal_id,
            "analysis": analysis,
            "recommendation": "approve" if analysis.get("quality_score", 0) > 0.7 else "review"
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid proposal ID format")
    except Exception as e:
        logger.error("Error analyzing proposal", error=str(e), proposal_id=proposal_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{proposal_id}/apply")
async def apply_proposal(proposal_id: str):
    session = get_session()
    async with session as s:
        proposal = await s.get(Proposal, proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        if proposal.status != "accepted":
            raise HTTPException(status_code=400, detail="Proposal must be accepted before applying")
        try:
            # Write code_after to file_path
            file_path = proposal.file_path
            code_after = proposal.code_after
            if not file_path or not code_after:
                raise Exception("Proposal missing file_path or code_after")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code_after)
            proposal.status = "applied"
            proposal.user_feedback = "applied"
            proposal.updated_at = datetime.utcnow()
            await s.commit()
            # Call learning service
            try:
                from app.services.ai_learning_service import AILearningService
                ai_learning_service = AILearningService()
                await ai_learning_service.learn_from_proposal(proposal_id, "applied")
            except Exception as le:
                logger.warning(f"Learning event not recorded: {le}")
            return {"status": "success", "message": "Patch applied and learning event recorded."}
        except Exception as e:
            proposal.status = "apply-failed"
            proposal.user_feedback = f"apply-failed: {str(e)}"
            proposal.updated_at = datetime.utcnow()
            await s.commit()
            # Call learning service for failure
            try:
                from app.services.ai_learning_service import AILearningService
                ai_learning_service = AILearningService()
                await ai_learning_service.learn_from_proposal(proposal_id, "apply-failed", feedback_reason=str(e))
            except Exception as le:
                logger.warning(f"Learning event not recorded: {le}")
            logger.error(f"Error applying patch: {e}")
            raise HTTPException(status_code=500, detail=f"Patch failed: {e}")
