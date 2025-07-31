"""
Auto-Apply Service for Real-Time Proposal Application
====================================================

This service automatically applies proposals to the app after user approval,
ensuring only rigorously tested proposals are applied in real-time.

REQUIREMENTS:
- Only proposals with status="accepted" AND test_status="passed"
- Additional final safety test before application
- Real-time monitoring and notifications
- Automatic backup creation
- Learning integration for successful applications
"""

import asyncio
import structlog
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..models.sql_models import Proposal
from .testing_service import TestingService
from .notification_service import notification_service
from .ai_learning_service import AILearningService

logger = structlog.get_logger()


class AutoApplyService:
    """Service for automatically applying proposals after user approval"""
    
    _instance = None
    _initialized = False
    _monitoring_task = None
    _is_monitoring = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AutoApplyService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.ai_learning_service = AILearningService()
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the Auto-Apply service"""
        instance = cls()
        logger.info("Auto-Apply Service initialized")
        return instance
    
    async def start_monitoring(self):
        """Start monitoring for approved proposals to auto-apply"""
        if self._is_monitoring:
            logger.warning("Auto-apply monitoring already running")
            return
        
        self._is_monitoring = True
        logger.info("Starting auto-apply monitoring for approved proposals")
        
        # Start monitoring task
        self._monitoring_task = asyncio.create_task(self._monitor_loop())
    
    async def stop_monitoring(self):
        """Stop monitoring for approved proposals"""
        self._is_monitoring = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped auto-apply monitoring")
    
    async def _monitor_loop(self):
        """Main monitoring loop for approved proposals"""
        while self._is_monitoring:
            try:
                await self._check_and_apply_approved_proposals()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in auto-apply monitoring loop: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _check_and_apply_approved_proposals(self):
        """Check for approved proposals and auto-apply them"""
        try:
            async with get_session() as session:
                # Find proposals that are accepted and have passed testing
                query = select(Proposal).where(
                    Proposal.status == "accepted",
                    Proposal.test_status == "passed",
                    Proposal.user_feedback == "accepted"
                )
                result = await session.execute(query)
                approved_proposals = result.scalars().all()
                
                if approved_proposals:
                    logger.info(f"Found {len(approved_proposals)} approved proposals for auto-application")
                    
                    for proposal in approved_proposals:
                        await self._auto_apply_proposal(proposal, session)
                else:
                    logger.debug("No approved proposals found for auto-application")
                    
        except Exception as e:
            logger.error(f"Error checking for approved proposals: {str(e)}")
    
    async def _auto_apply_proposal(self, proposal: Proposal, session: AsyncSession):
        """Auto-apply a single approved proposal"""
        try:
            logger.info(f"Auto-applying proposal {proposal.id} to {proposal.file_path}")
            
            # Run final safety test
            proposal_data = {
                "id": str(proposal.id),
                "ai_type": proposal.ai_type,
                "file_path": proposal.file_path,
                "code_before": proposal.code_before,
                "code_after": proposal.code_after,
                "improvement_type": proposal.improvement_type,
                "confidence": proposal.confidence,
            }
            
            # Run final safety test
            testing_service_instance = TestingService()
            final_result, final_summary, final_detailed_results = await testing_service_instance.test_proposal(proposal_data)
            
            if final_result.value != "passed":
                logger.error(f"Final safety test failed for auto-apply proposal {proposal.id}: {final_summary}")
                proposal.status = "auto-apply-failed"
                proposal.user_feedback = f"Auto-apply final test failed: {final_summary}"
                proposal.updated_at = datetime.utcnow()
                await session.commit()
                
                # Notify about failed auto-apply
                try:
                    await notification_service.notify_auto_apply_failed(
                        str(proposal.id),
                        proposal.ai_type,
                        proposal.file_path,
                        final_summary
                    )
                except Exception as e:
                    logger.error("Error sending auto-apply failed notification", error=str(e))
                
                return False
            
            # FINAL TEST PASSED - Auto-apply the proposal
            logger.info(f"Final safety test passed, auto-applying proposal {proposal.id}")
            
            # Create backup of original file
            import shutil
            import os
            file_path = proposal.file_path
            backup_path = f"{file_path}.backup.{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_path)
                logger.info(f"Created backup for auto-apply: {backup_path}")
            
            # Apply the code change
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(proposal.code_after)
            
            # Update proposal status
            proposal.status = "auto-applied"
            proposal.user_feedback = "auto-applied"
            proposal.updated_at = datetime.utcnow()
            await session.commit()
            
            # Notify about successful auto-application
            try:
                await notification_service.notify_auto_apply_success(
                    str(proposal.id),
                    proposal.ai_type,
                    proposal.file_path,
                    final_summary
                )
            except Exception as e:
                logger.error("Error sending auto-apply success notification", error=str(e))
            
            # Call learning service for successful auto-application
            try:
                await self.ai_learning_service.learn_from_proposal(
                    str(proposal.id), 
                    "auto-applied"
                )
            except Exception as le:
                logger.warning(f"Learning event not recorded: {le}")
            
            logger.info(f"Successfully auto-applied proposal {proposal.id} to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error auto-applying proposal {proposal.id}: {str(e)}")
            proposal.status = "auto-apply-failed"
            proposal.user_feedback = f"auto-apply-failed: {str(e)}"
            proposal.updated_at = datetime.utcnow()
            await session.commit()
            
            # Call learning service for failure
            try:
                await self.ai_learning_service.learn_from_proposal(
                    str(proposal.id), 
                    "auto-apply-failed", 
                    feedback_reason=str(e)
                )
            except Exception as le:
                logger.warning(f"Learning event not recorded: {le}")
            
            return False
    
    async def get_auto_apply_stats(self) -> Dict[str, Any]:
        """Get statistics about auto-applied proposals"""
        try:
            async with get_session() as session:
                # Count auto-applied proposals
                auto_applied_query = select(Proposal).where(Proposal.status == "auto-applied")
                auto_applied_result = await session.execute(auto_applied_query)
                auto_applied_count = len(auto_applied_result.scalars().all())
                
                # Count auto-apply failed proposals
                auto_apply_failed_query = select(Proposal).where(Proposal.status == "auto-apply-failed")
                auto_apply_failed_result = await session.execute(auto_apply_failed_query)
                auto_apply_failed_count = len(auto_apply_failed_result.scalars().all())
                
                # Count pending auto-applies (accepted but not yet auto-applied)
                pending_auto_apply_query = select(Proposal).where(
                    Proposal.status == "accepted",
                    Proposal.test_status == "passed",
                    Proposal.user_feedback == "accepted"
                )
                pending_auto_apply_result = await session.execute(pending_auto_apply_query)
                pending_auto_apply_count = len(pending_auto_apply_result.scalars().all())
                
                return {
                    "auto_applied_count": auto_applied_count,
                    "auto_apply_failed_count": auto_apply_failed_count,
                    "pending_auto_apply_count": pending_auto_apply_count,
                    "is_monitoring": self._is_monitoring,
                    "last_check": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting auto-apply stats: {str(e)}")
            return {
                "error": str(e),
                "is_monitoring": self._is_monitoring
            }
    
    async def manual_auto_apply_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Manually trigger auto-apply for a specific proposal"""
        try:
            async with get_session() as session:
                # Get proposal
                query = select(Proposal).where(Proposal.id == proposal_id)
                result = await session.execute(query)
                proposal = result.scalar_one_or_none()
                
                if not proposal:
                    return {
                        "success": False,
                        "error": "Proposal not found"
                    }
                
                # Check if proposal is eligible for auto-apply
                if proposal.status != "accepted" or proposal.test_status != "passed":
                    return {
                        "success": False,
                        "error": "Proposal must be accepted and have passed testing"
                    }
                
                # Auto-apply the proposal
                success = await self._auto_apply_proposal(proposal, session)
                
                return {
                    "success": success,
                    "proposal_id": str(proposal.id),
                    "file_path": proposal.file_path,
                    "message": "Proposal auto-applied successfully" if success else "Auto-apply failed"
                }
                
        except Exception as e:
            logger.error(f"Error in manual auto-apply: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
auto_apply_service = AutoApplyService() 