"""
Guardian AI Service for health checks and repair suggestions
"""

import structlog
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
import json
import re
from uuid import UUID

from app.models.sql_models import GuardianSuggestion, Proposal, Learning, ErrorLearning
from app.core.database import get_session

logger = structlog.get_logger()


class GuardianAIService:
    """Guardian AI service for comprehensive health checks and repairs"""
    
    def __init__(self):
        self.health_check_rules = {
            "mission": self._check_mission_health,
            "entry": self._check_entry_health,
            "mastery": self._check_mastery_health,
            "proposal": self._check_proposal_health,
            "learning": self._check_learning_health
        }
    
    async def run_comprehensive_health_check(self, session: AsyncSession) -> Dict[str, Any]:
        """Run comprehensive health checks on all system components"""
        try:
            logger.info("Starting comprehensive Guardian AI health check")
            
            results = {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_health": "healthy",
                "issues_found": 0,
                "suggestions_created": 0,
                "checks_performed": {},
                "summary": {}
            }
            
            # Check each component type
            for component_type, check_function in self.health_check_rules.items():
                logger.info(f"Running health check for {component_type}")
                component_results = await check_function(session)
                results["checks_performed"][component_type] = component_results
                results["issues_found"] += component_results.get("issues_found", 0)
                results["suggestions_created"] += component_results.get("suggestions_created", 0)
            
            # Determine overall health
            if results["issues_found"] == 0:
                results["overall_health"] = "healthy"
            elif results["issues_found"] <= 5:
                results["overall_health"] = "warning"
            else:
                results["overall_health"] = "critical"
            
            # Generate summary
            results["summary"] = {
                "total_components_checked": len(self.health_check_rules),
                "healthy_components": sum(1 for r in results["checks_performed"].values() 
                                        if r.get("health_status") == "healthy"),
                "components_with_issues": sum(1 for r in results["checks_performed"].values() 
                                            if r.get("issues_found", 0) > 0),
                "critical_issues": sum(r.get("critical_issues", 0) for r in results["checks_performed"].values()),
                "high_priority_issues": sum(r.get("high_priority_issues", 0) for r in results["checks_performed"].values())
            }
            
            logger.info("Comprehensive health check completed", 
                       overall_health=results["overall_health"],
                       issues_found=results["issues_found"])
            
            return results
            
        except Exception as e:
            logger.error("Error running comprehensive health check", error=str(e))
            raise
    
    async def _check_proposal_health(self, session: AsyncSession) -> Dict[str, Any]:
        """Check health of proposal system"""
        try:
            issues_found = 0
            suggestions_created = 0
            critical_issues = 0
            high_priority_issues = 0
            
            # Check for proposals with missing required fields
            proposals_result = await session.execute(
                select(Proposal).where(
                    or_(
                        Proposal.ai_type.is_(None),
                        Proposal.file_path.is_(None),
                        Proposal.code_before.is_(None)
                    )
                )
            )
            invalid_proposals = proposals_result.scalars().all()
            
            for proposal in invalid_proposals:
                issues_found += 1
                high_priority_issues += 1
                
                await self._create_suggestion(
                    session=session,
                    issue_type="proposal",
                    affected_item_type="proposal",
                    affected_item_id=str(proposal.id),
                    affected_item_name=f"Proposal {proposal.id[:8]}",
                    issue_description="Proposal missing required fields",
                    current_value=json.dumps({
                        "ai_type": proposal.ai_type,
                        "file_path": proposal.file_path,
                        "has_code_before": bool(proposal.code_before)
                    }),
                    proposed_fix="Add missing required fields or mark for deletion",
                    severity="high",
                    health_check_type="required_fields_validation"
                )
                suggestions_created += 1
            
            # Check for proposals with inconsistent status
            status_result = await session.execute(
                select(Proposal).where(
                    and_(
                        Proposal.status == "tested",
                        Proposal.test_status == "not-run"
                    )
                )
            )
            inconsistent_proposals = status_result.scalars().all()
            
            for proposal in inconsistent_proposals:
                issues_found += 1
                
                await self._create_suggestion(
                    session=session,
                    issue_type="proposal",
                    affected_item_type="proposal",
                    affected_item_id=str(proposal.id),
                    affected_item_name=f"Proposal {proposal.id[:8]}",
                    issue_description="Proposal status inconsistent with test status",
                    current_value=f"status={proposal.status}, test_status={proposal.test_status}",
                    proposed_fix="Update test status to match proposal status",
                    severity="medium",
                    health_check_type="status_consistency_check"
                )
                suggestions_created += 1
            
            # Check for duplicate proposals
            duplicate_result = await session.execute(
                select(Proposal.code_hash, func.count(Proposal.id))
                .where(Proposal.code_hash.isnot(None))
                .group_by(Proposal.code_hash)
                .having(func.count(Proposal.id) > 1)
            )
            duplicates = duplicate_result.all()
            
            for code_hash, count in duplicates:
                issues_found += 1
                
                await self._create_suggestion(
                    session=session,
                    issue_type="proposal",
                    affected_item_type="proposal_group",
                    affected_item_id=code_hash,
                    affected_item_name=f"Duplicate proposals (count: {count})",
                    issue_description=f"Found {count} proposals with identical code hash",
                    current_value=f"code_hash: {code_hash}, count: {count}",
                    proposed_fix="Review and merge duplicate proposals",
                    severity="medium",
                    health_check_type="duplicate_detection"
                )
                suggestions_created += 1
            
            return {
                "health_status": "healthy" if issues_found == 0 else "warning",
                "issues_found": issues_found,
                "suggestions_created": suggestions_created,
                "critical_issues": critical_issues,
                "high_priority_issues": high_priority_issues,
                "total_proposals": await self._count_proposals(session)
            }
            
        except Exception as e:
            logger.error("Error checking proposal health", error=str(e))
            return {"health_status": "error", "error": str(e)}
    
    async def _check_learning_health(self, session: AsyncSession) -> Dict[str, Any]:
        """Check health of learning system"""
        try:
            issues_found = 0
            suggestions_created = 0
            
            # Check for learning entries with low confidence but high success rate
            learning_result = await session.execute(
                select(Learning).where(
                    and_(
                        Learning.confidence < 0.3,
                        Learning.success_rate > 0.8
                    )
                )
            )
            inconsistent_learning = learning_result.scalars().all()
            
            for learning in inconsistent_learning:
                issues_found += 1
                
                await self._create_suggestion(
                    session=session,
                    issue_type="learning",
                    affected_item_type="learning",
                    affected_item_id=str(learning.id),
                    affected_item_name=f"Learning {learning.learning_type}",
                    issue_description="Learning entry has low confidence but high success rate",
                    current_value=f"confidence={learning.confidence}, success_rate={learning.success_rate}",
                    proposed_fix="Update confidence score based on success rate",
                    severity="low",
                    health_check_type="confidence_consistency_check"
                )
                suggestions_created += 1
            
            # Check for error learning with high frequency but no solution
            error_result = await session.execute(
                select(ErrorLearning).where(
                    and_(
                        ErrorLearning.frequency > 5,
                        ErrorLearning.solution.is_(None)
                    )
                )
            )
            unsolved_errors = error_result.scalars().all()
            
            for error in unsolved_errors:
                issues_found += 1
                
                await self._create_suggestion(
                    session=session,
                    issue_type="learning",
                    affected_item_type="error_learning",
                    affected_item_id=str(error.id),
                    affected_item_name=f"Error: {error.error_pattern}",
                    issue_description="Frequent error without documented solution",
                    current_value=f"frequency={error.frequency}, pattern={error.error_pattern}",
                    proposed_fix="Investigate and document solution for this error pattern",
                    severity="high",
                    health_check_type="error_solution_check"
                )
                suggestions_created += 1
            
            return {
                "health_status": "healthy" if issues_found == 0 else "warning",
                "issues_found": issues_found,
                "suggestions_created": suggestions_created,
                "total_learning_entries": await self._count_learning_entries(session),
                "total_error_entries": await self._count_error_learning_entries(session)
            }
            
        except Exception as e:
            logger.error("Error checking learning health", error=str(e))
            return {"health_status": "error", "error": str(e)}
    
    async def _check_mission_health(self, session: AsyncSession) -> Dict[str, Any]:
        """Check health of mission system (placeholder for future implementation)"""
        # This would check mission data when mission models are implemented
        return {
            "health_status": "healthy",
            "issues_found": 0,
            "suggestions_created": 0,
            "note": "Mission health checks will be implemented when mission models are added"
        }
    
    async def _check_entry_health(self, session: AsyncSession) -> Dict[str, Any]:
        """Check health of entry system (placeholder for future implementation)"""
        # This would check entry data when entry models are implemented
        return {
            "health_status": "healthy",
            "issues_found": 0,
            "suggestions_created": 0,
            "note": "Entry health checks will be implemented when entry models are added"
        }
    
    async def _check_mastery_health(self, session: AsyncSession) -> Dict[str, Any]:
        """Check health of mastery system (placeholder for future implementation)"""
        # This would check mastery data when mastery models are implemented
        return {
            "health_status": "healthy",
            "issues_found": 0,
            "suggestions_created": 0,
            "note": "Mastery health checks will be implemented when mastery models are added"
        }
    
    async def _create_suggestion(
        self,
        session: AsyncSession,
        issue_type: str,
        affected_item_type: str,
        affected_item_id: str,
        affected_item_name: str,
        issue_description: str,
        current_value: str,
        proposed_fix: str,
        severity: str = "medium",
        health_check_type: str = "general_health_check"
    ) -> GuardianSuggestion:
        """Create a new Guardian suggestion"""
        try:
            suggestion = GuardianSuggestion(
                issue_type=issue_type,
                affected_item_type=affected_item_type,
                affected_item_id=affected_item_id,
                affected_item_name=affected_item_name,
                issue_description=issue_description,
                current_value=current_value,
                proposed_fix=proposed_fix,
                severity=severity,
                health_check_type=health_check_type,
                status="pending"
            )
            
            session.add(suggestion)
            await session.commit()
            
            logger.info("Created Guardian suggestion", 
                       suggestion_id=str(suggestion.id),
                       issue_type=issue_type,
                       severity=severity)
            
            return suggestion
            
        except Exception as e:
            logger.error("Error creating Guardian suggestion", error=str(e))
            await session.rollback()
            raise
    
    async def get_pending_suggestions(
        self, 
        session: AsyncSession, 
        limit: int = 50,
        offset: int = 0,
        severity_filter: Optional[str] = None,
        issue_type_filter: Optional[str] = None
    ) -> List[GuardianSuggestion]:
        """Get pending Guardian suggestions with optional filtering"""
        try:
            query = select(GuardianSuggestion).where(GuardianSuggestion.status == "pending")
            
            if severity_filter:
                query = query.where(GuardianSuggestion.severity == severity_filter)
            
            if issue_type_filter:
                query = query.where(GuardianSuggestion.issue_type == issue_type_filter)
            
            query = query.order_by(
                GuardianSuggestion.severity.desc(),
                GuardianSuggestion.created_at.desc()
            ).offset(offset).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error("Error getting pending suggestions", error=str(e))
            raise
    
    async def approve_suggestion(
        self,
        session: AsyncSession,
        suggestion_id: str,
        approved_by: str,
        user_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Approve a Guardian suggestion and apply the fix"""
        try:
            # Get the suggestion
            result = await session.execute(
                select(GuardianSuggestion).where(GuardianSuggestion.id == suggestion_id)
            )
            suggestion = result.scalar_one_or_none()
            
            if not suggestion:
                raise ValueError("Suggestion not found")
            
            if suggestion.status != "pending":
                raise ValueError("Suggestion is not pending")
            
            # Update suggestion status
            suggestion.status = "approved"
            suggestion.approved_by = approved_by
            suggestion.approved_at = datetime.utcnow()
            suggestion.user_feedback = user_feedback
            
            # Apply the fix
            fix_result = await self._apply_fix(session, suggestion)
            
            # Update suggestion with fix results
            suggestion.fix_applied = True
            suggestion.fix_applied_at = datetime.utcnow()
            suggestion.fix_result = fix_result.get("message", "Fix applied")
            suggestion.fix_success = fix_result.get("success", False)
            
            await session.commit()
            
            logger.info("Approved and applied Guardian suggestion", 
                       suggestion_id=str(suggestion.id),
                       approved_by=approved_by,
                       fix_success=suggestion.fix_success)
            
            return {
                "status": "success",
                "suggestion_id": str(suggestion.id),
                "fix_applied": True,
                "fix_success": suggestion.fix_success,
                "fix_result": suggestion.fix_result
            }
            
        except Exception as e:
            logger.error("Error approving suggestion", error=str(e))
            await session.rollback()
            raise
    
    async def reject_suggestion(
        self,
        session: AsyncSession,
        suggestion_id: str,
        rejected_by: str,
        user_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Reject a Guardian suggestion"""
        try:
            # Get the suggestion
            result = await session.execute(
                select(GuardianSuggestion).where(GuardianSuggestion.id == suggestion_id)
            )
            suggestion = result.scalar_one_or_none()
            
            if not suggestion:
                raise ValueError("Suggestion not found")
            
            if suggestion.status != "pending":
                raise ValueError("Suggestion is not pending")
            
            # Update suggestion status
            suggestion.status = "rejected"
            suggestion.approved_by = rejected_by
            suggestion.approved_at = datetime.utcnow()
            suggestion.user_feedback = user_feedback
            
            await session.commit()
            
            logger.info("Rejected Guardian suggestion", 
                       suggestion_id=str(suggestion.id),
                       rejected_by=rejected_by)
            
            return {
                "status": "success",
                "suggestion_id": str(suggestion.id),
                "message": "Suggestion rejected"
            }
            
        except Exception as e:
            logger.error("Error rejecting suggestion", error=str(e))
            await session.rollback()
            raise
    
    async def _apply_fix(self, session: AsyncSession, suggestion: GuardianSuggestion) -> Dict[str, Any]:
        """Apply the proposed fix for a suggestion"""
        try:
            if suggestion.issue_type == "proposal":
                return await self._apply_proposal_fix(session, suggestion)
            elif suggestion.issue_type == "learning":
                return await self._apply_learning_fix(session, suggestion)
            else:
                return {
                    "success": False,
                    "message": f"Fix application not implemented for issue type: {suggestion.issue_type}"
                }
                
        except Exception as e:
            logger.error("Error applying fix", error=str(e))
            return {
                "success": False,
                "message": f"Error applying fix: {str(e)}"
            }
    
    async def _apply_proposal_fix(self, session: AsyncSession, suggestion: GuardianSuggestion) -> Dict[str, Any]:
        """Apply fix for proposal-related issues"""
        try:
            if suggestion.health_check_type == "status_consistency_check":
                # Fix status inconsistency
                proposal_result = await session.execute(
                    select(Proposal).where(Proposal.id == suggestion.affected_item_id)
                )
                proposal = proposal_result.scalar_one_or_none()
                
                if proposal and proposal.status == "tested" and proposal.test_status == "not-run":
                    proposal.test_status = "passed"
                    await session.commit()
                    return {
                        "success": True,
                        "message": "Updated test status to match proposal status"
                    }
            
            return {
                "success": False,
                "message": "Fix not implemented for this proposal issue type"
            }
            
        except Exception as e:
            logger.error("Error applying proposal fix", error=str(e))
            return {
                "success": False,
                "message": f"Error applying proposal fix: {str(e)}"
            }
    
    async def _apply_learning_fix(self, session: AsyncSession, suggestion: GuardianSuggestion) -> Dict[str, Any]:
        """Apply fix for learning-related issues"""
        try:
            if suggestion.health_check_type == "confidence_consistency_check":
                # Fix confidence inconsistency
                learning_result = await session.execute(
                    select(Learning).where(Learning.id == suggestion.affected_item_id)
                )
                learning = learning_result.scalar_one_or_none()
                
                if learning and learning.confidence < 0.3 and learning.success_rate > 0.8:
                    learning.confidence = min(learning.success_rate, 0.9)
                    await session.commit()
                    return {
                        "success": True,
                        "message": "Updated confidence score based on success rate"
                    }
            
            return {
                "success": False,
                "message": "Fix not implemented for this learning issue type"
            }
            
        except Exception as e:
            logger.error("Error applying learning fix", error=str(e))
            return {
                "success": False,
                "message": f"Error applying learning fix: {str(e)}"
            }
    
    async def _count_proposals(self, session: AsyncSession) -> int:
        """Count total proposals"""
        result = await session.execute(select(func.count(Proposal.id)))
        return result.scalar()
    
    async def _count_learning_entries(self, session: AsyncSession) -> int:
        """Count total learning entries"""
        result = await session.execute(select(func.count(Learning.id)))
        return result.scalar()
    
    async def _count_error_learning_entries(self, session: AsyncSession) -> int:
        """Count total error learning entries"""
        result = await session.execute(select(func.count(ErrorLearning.id)))
        return result.scalar()
    
    async def get_suggestion_statistics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get statistics about Guardian suggestions"""
        try:
            # Count by status
            status_result = await session.execute(
                select(GuardianSuggestion.status, func.count(GuardianSuggestion.id))
                .group_by(GuardianSuggestion.status)
            )
            status_counts = dict(status_result.all())
            
            # Count by severity
            severity_result = await session.execute(
                select(GuardianSuggestion.severity, func.count(GuardianSuggestion.id))
                .group_by(GuardianSuggestion.severity)
            )
            severity_counts = dict(severity_result.all())
            
            # Count by issue type
            type_result = await session.execute(
                select(GuardianSuggestion.issue_type, func.count(GuardianSuggestion.id))
                .group_by(GuardianSuggestion.issue_type)
            )
            type_counts = dict(type_result.all())
            
            # Recent activity
            recent_result = await session.execute(
                select(func.count(GuardianSuggestion.id))
                .where(GuardianSuggestion.created_at >= datetime.utcnow() - timedelta(days=7))
            )
            recent_count = recent_result.scalar()
            
            return {
                "total_suggestions": sum(status_counts.values()),
                "by_status": status_counts,
                "by_severity": severity_counts,
                "by_issue_type": type_counts,
                "recent_suggestions": recent_count,
                "approval_rate": (
                    status_counts.get("approved", 0) / 
                    (status_counts.get("approved", 0) + status_counts.get("rejected", 0))
                    if (status_counts.get("approved", 0) + status_counts.get("rejected", 0)) > 0
                    else 0
                )
            }
            
        except Exception as e:
            logger.error("Error getting suggestion statistics", error=str(e))
            raise 