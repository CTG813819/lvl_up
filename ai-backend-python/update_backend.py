#!/usr/bin/env python3
"""
Script to update the proposals.py file on the EC2 backend
"""

import os
import subprocess
import sys

def run_ssh_command(command):
    """Run SSH command on EC2 instance"""
    try:
        # Replace with your actual EC2 details
        ssh_command = f"ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip '{command}'"
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def update_proposals_file():
    """Update the proposals.py file on the backend"""
    
    # The updated proposals.py content with fixed route ordering
    updated_content = '''"""
Proposals router with ML integration
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload

from ..models.proposal import ProposalCreate, ProposalUpdate, ProposalResponse, ProposalStats
from ..models.sql_models import Proposal
from ..core.database import get_session
from ..services.ml_service import MLService
from ..services.ai_learning_service import AILearningService

logger = structlog.get_logger()
router = APIRouter()

ml_service = MLService()
ai_learning_service = AILearningService()


@router.post("/", response_model=ProposalResponse)
async def create_proposal(proposal: ProposalCreate, db: AsyncSession = Depends(get_session)):
    """Create a new proposal with ML analysis"""
    try:
        # Convert to dict for ML analysis
        proposal_dict = proposal.dict()
        
        # Analyze proposal quality using ML
        ml_analysis = await ml_service.analyze_proposal_quality(proposal_dict)
        
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
            ai_reasoning=proposal.ai_reasoning + f"\\n\\nML Analysis: Quality Score: {ml_analysis.get('quality_score', 0.5):.2f}, Approval Probability: {ml_analysis.get('approval_probability', 0.5):.2f}" if proposal.ai_reasoning else f"ML Analysis: Quality Score: {ml_analysis.get('quality_score', 0.5):.2f}, Approval Probability: {ml_analysis.get('approval_probability', 0.5):.2f}",
            learning_context=proposal.learning_context,
            mistake_pattern=proposal.mistake_pattern,
            improvement_type=proposal.improvement_type,
            confidence=ml_analysis.get("quality_score", 0.5),
            user_feedback_reason=proposal.user_feedback_reason,
            ai_learning_applied=proposal.ai_learning_applied,
            previous_mistakes_avoided=proposal.previous_mistakes_avoided
        )
        
        db.add(new_proposal)
        await db.commit()
        await db.refresh(new_proposal)
        
        logger.info("Proposal created with ML analysis", 
                   proposal_id=str(new_proposal.id),
                   quality_score=ml_analysis.get("quality_score", 0.5))
        
        return ProposalResponse.from_orm(new_proposal)
        
    except Exception as e:
        await db.rollback()
        logger.error("Error creating proposal", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ProposalResponse])
async def get_proposals(
    ai_type: Optional[str] = Query(None, description="Filter by AI type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, le=100, description="Number of proposals to return"),
    skip: int = Query(0, description="Number of proposals to skip"),
    db: AsyncSession = Depends(get_session)
):
    """Get proposals with optional filtering"""
    try:
        # Build query
        query = select(Proposal)
        
        if ai_type:
            query = query.where(Proposal.ai_type == ai_type)
        if status:
            query = query.where(Proposal.status == status)
        
        # Add ordering and pagination
        query = query.order_by(Proposal.created_at.desc()).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        proposals = result.scalars().all()
        
        return [ProposalResponse.from_orm(proposal) for proposal in proposals]
        
    except Exception as e:
        logger.error("Error getting proposals", error=str(e))
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
        learning_metrics = await ai_learning_service.get_learning_stats("Imperium")
        
        return {
            "status": "active",
            "ai_types": {
                "Imperium": {
                    "total_proposals": imperium_count,
                    "learning_progress": learning_metrics.get("learning_progress", 0.0),
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
            "github_integration": "configured" if ai_learning_service.github_token else "not_configured"
        }
        
    except Exception as e:
        logger.error("Error getting AI status", error=str(e))
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
'''
    
    # Create a temporary file with the updated content
    temp_file = "temp_proposals.py"
    with open(temp_file, "w") as f:
        f.write(updated_content)
    
    print("Created temporary file with updated proposals.py content")
    
    # Instructions for manual update
    print("\\n" + "="*60)
    print("MANUAL UPDATE INSTRUCTIONS")
    print("="*60)
    print("1. Copy the content from the temporary file 'temp_proposals.py'")
    print("2. SSH into your EC2 instance:")
    print("   ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip")
    print("3. Navigate to the backend directory:")
    print("   cd ~/ai-backend-python")
    print("4. Edit the proposals.py file:")
    print("   nano app/routers/proposals.py")
    print("5. Replace the entire content with the updated version")
    print("6. Save and exit (Ctrl+X, Y, Enter)")
    print("7. Restart the backend service:")
    print("   sudo systemctl restart ai-backend")
    print("8. Test the endpoints:")
    print("   curl http://localhost:4000/api/proposals/ai-status")
    print("   curl http://localhost:4000/api/learning/data")
    print("   curl http://localhost:4000/api/learning/metrics")
    print("="*60)
    
    # Alternative: Use scp to copy the file directly
    print("\\nALTERNATIVE: Use SCP to copy the file directly")
    print("scp -i ~/.ssh/your-key.pem temp_proposals.py ubuntu@your-ec2-ip:~/ai-backend-python/app/routers/proposals.py")
    print("Then SSH in and restart the service: sudo systemctl restart ai-backend")

if __name__ == "__main__":
    update_proposals_file() 