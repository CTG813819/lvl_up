"""
Approval router for approval workflow and management
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.sql_models import Proposal

logger = structlog.get_logger()
router = APIRouter()


@router.get("/")
async def get_approval_overview():
    """Get approval system overview"""
    try:
        return {
            "status": "success",
            "message": "Approval workflow system is active",
            "timestamp": datetime.utcnow().isoformat(),
            "features": [
                "proposal_approval",
                "workflow_management",
                "approval_history",
                "approval_rules",
                "approval_analytics"
            ]
        }
    except Exception as e:
        logger.error("Error getting approval overview", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending")
async def get_pending_approvals(session: AsyncSession = Depends(get_db)):
    """Get pending approvals"""
    try:
        # Get pending and test-passed proposals
        pending_result = await session.execute(
            select(Proposal)
            .where(Proposal.status.in_(["pending", "test-passed"]))
            .order_by(Proposal.created_at.desc())
            .limit(20)
        )
        pending_proposals = pending_result.scalars().all()
        
        return {
            "status": "success",
            "data": {
                "pending_count": len(pending_proposals),
                "approvals": [
                    {
                        "id": str(p.id),
                        "ai_type": p.ai_type,
                        "file_path": p.file_path,
                        "created_at": p.created_at.isoformat() if p.created_at else None,
                        "priority": "normal",
                        "estimated_review_time": "15 minutes"
                    }
                    for p in pending_proposals
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting pending approvals", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve/{proposal_id}")
async def approve_proposal(
    proposal_id: str,
    approval_notes: str = "",
    session: AsyncSession = Depends(get_db)
):
    """Approve a proposal"""
    try:
        # Get the proposal
        result = await session.execute(
            select(Proposal).where(Proposal.id == proposal_id)
        )
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        if proposal.status not in ["pending", "test-passed"]:
            raise HTTPException(status_code=400, detail="Proposal is not pending approval or test-passed")
        
        # Update proposal status
        proposal.status = "approved"
        await session.commit()
        
        return {
            "status": "success",
            "data": {
                "proposal_id": proposal_id,
                "action": "approved",
                "approval_notes": approval_notes,
                "approved_at": datetime.utcnow().isoformat(),
                "approved_by": "system"
            }
        }
    except Exception as e:
        logger.error("Error approving proposal", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reject/{proposal_id}")
async def reject_proposal(
    proposal_id: str,
    rejection_reason: str,
    session: AsyncSession = Depends(get_db)
):
    """Reject a proposal"""
    try:
        # Get the proposal
        result = await session.execute(
            select(Proposal).where(Proposal.id == proposal_id)
        )
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        if proposal.status not in ["pending", "test-passed"]:
            raise HTTPException(status_code=400, detail="Proposal is not pending approval or test-passed")
        
        # Update proposal status
        proposal.status = "rejected"
        await session.commit()
        
        return {
            "status": "success",
            "data": {
                "proposal_id": proposal_id,
                "action": "rejected",
                "rejection_reason": rejection_reason,
                "rejected_at": datetime.utcnow().isoformat(),
                "rejected_by": "system"
            }
        }
    except Exception as e:
        logger.error("Error rejecting proposal", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_approval_history(session: AsyncSession = Depends(get_db)):
    """Get approval history"""
    try:
        # Get approved and rejected proposals
        history_result = await session.execute(
            select(Proposal)
            .where(Proposal.status.in_(["approved", "rejected"]))
            .order_by(Proposal.created_at.desc())
            .limit(50)
        )
        approval_history = history_result.scalars().all()
        
        return {
            "status": "success",
            "data": {
                "total_approvals": len([p for p in approval_history if p.status == "approved"]),
                "total_rejections": len([p for p in approval_history if p.status == "rejected"]),
                "approval_rate": len([p for p in approval_history if p.status == "approved"]) / len(approval_history) * 100 if approval_history else 0,
                "history": [
                    {
                        "id": str(p.id),
                        "ai_type": p.ai_type,
                        "action": p.status,
                        "created_at": p.created_at.isoformat() if p.created_at else None
                    }
                    for p in approval_history
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting approval history", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_approval_analytics(session: AsyncSession = Depends(get_db)):
    """Get approval analytics"""
    try:
        # Get approval statistics by AI type
        ai_type_result = await session.execute(
            select(Proposal.ai_type, Proposal.status, func.count(Proposal.id))
            .group_by(Proposal.ai_type, Proposal.status)
        )
        ai_type_stats = ai_type_result.all()
        
        # Process statistics
        stats_by_ai_type = {}
        for ai_type, status, count in ai_type_stats:
            if ai_type not in stats_by_ai_type:
                stats_by_ai_type[ai_type] = {"approved": 0, "rejected": 0, "pending": 0}
            stats_by_ai_type[ai_type][status] = count
        
        return {
            "status": "success",
            "data": {
                "approval_stats": stats_by_ai_type,
                "overall_metrics": {
                    "total_proposals": sum(sum(stats.values()) for stats in stats_by_ai_type.values()),
                    "approval_rate": 85.2,
                    "average_approval_time": "2.5 hours",
                    "peak_approval_hours": ["09:00", "14:00", "16:00"]
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting approval analytics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 