"""
Proposal Validation Service
Prevents redundant proposals and ensures AIs learn before creating new suggestions
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from ..models.sql_models import Proposal
from ..services.ai_learning_service import AILearningService

logger = structlog.get_logger()


class ProposalValidationService:
    """Service to validate proposals and prevent redundancy"""
    
    def __init__(self):
        self.ai_learning_service = AILearningService()
        
        # Validation thresholds
        self.similarity_threshold = 0.85  # 85% similarity considered duplicate
        self.min_learning_interval = timedelta(hours=2)  # Minimum time between proposals
        self.max_pending_per_ai = 2  # Max pending proposals per AI type
        self.min_confidence_threshold = 0.6  # Minimum confidence for new proposals
        
    async def validate_proposal(self, proposal_data: Dict, db: AsyncSession) -> Tuple[bool, str, Dict]:
        """
        Validate a proposal before creation
        
        Returns:
            Tuple of (is_valid, reason, validation_details)
        """
        try:
            validation_details = {}
            
            # 1. Check for duplicates
            is_duplicate, duplicate_reason = await self._check_for_duplicates(proposal_data, db)
            if is_duplicate:
                return False, f"Duplicate proposal detected: {duplicate_reason}", validation_details
            
            # 2. Check AI learning status
            ai_ready, learning_reason = await self._check_ai_learning_status(proposal_data, db)
            if not ai_ready:
                return False, f"AI needs to learn more: {learning_reason}", validation_details
            
            # 3. Check proposal limits
            limit_ok, limit_reason = await self._check_proposal_limits(proposal_data, db)
            if not limit_ok:
                return False, f"Proposal limit exceeded: {limit_reason}", validation_details
            
            # 4. Check confidence threshold
            confidence_ok, confidence_reason = await self._check_confidence_threshold(proposal_data)
            if not confidence_ok:
                return False, f"Confidence too low: {confidence_reason}", validation_details
            
            # 5. Check improvement potential
            improvement_ok, improvement_reason = await self._check_improvement_potential(proposal_data, db)
            if not improvement_ok:
                return False, f"Insufficient improvement potential: {improvement_reason}", validation_details
            
            validation_details = {
                "duplicate_check": "passed",
                "learning_status": "ready",
                "proposal_limits": "within_bounds",
                "confidence": "sufficient",
                "improvement_potential": "adequate"
            }
            
            return True, "Proposal validation passed", validation_details
            
        except Exception as e:
            logger.error("Error validating proposal", error=str(e))
            return False, f"Validation error: {str(e)}", {}
    
    async def _check_for_duplicates(self, proposal_data: Dict, db: AsyncSession) -> Tuple[bool, str]:
        """Check if proposal is a duplicate of existing proposals"""
        try:
            ai_type = proposal_data.get("ai_type", "")
            file_path = proposal_data.get("file_path", "")
            code_before = proposal_data.get("code_before", "")
            code_after = proposal_data.get("code_after", "")
            
            # Generate semantic hash
            semantic_input = f"{ai_type}|{file_path}|{code_before}|{code_after}"
            semantic_hash = hashlib.sha256(semantic_input.encode('utf-8')).hexdigest()
            
            # Check for exact semantic matches
            query = select(Proposal).where(
                and_(
                    Proposal.semantic_hash == semantic_hash,
                    Proposal.status.in_(["pending", "test-passed", "test-failed"])
                )
            )
            result = await db.execute(query)
            exact_matches = result.scalars().all()
            
            if exact_matches:
                return True, "Exact semantic match found"
            
            # Check for similar proposals in the same file
            query = select(Proposal).where(
                and_(
                    Proposal.file_path == file_path,
                    Proposal.ai_type == ai_type,
                    Proposal.status.in_(["pending", "test-passed", "test-failed"]),
                    Proposal.created_at >= datetime.utcnow() - timedelta(days=7)
                )
            )
            result = await db.execute(query)
            recent_proposals = result.scalars().all()
            
            for recent_proposal in recent_proposals:
                similarity = self._calculate_similarity(proposal_data, recent_proposal)
                if similarity >= self.similarity_threshold:
                    return True, f"Similar proposal found (similarity: {similarity:.2f})"
            
            return False, "No duplicates found"
            
        except Exception as e:
            logger.error("Error checking for duplicates", error=str(e))
            return False, f"Error in duplicate check: {str(e)}"
    
    async def _check_ai_learning_status(self, proposal_data: Dict, db: AsyncSession) -> Tuple[bool, str]:
        """Check if AI has learned enough to make meaningful proposals"""
        try:
            ai_type = proposal_data.get("ai_type", "")
            
            # Get recent proposals for this AI
            query = select(Proposal).where(
                and_(
                    Proposal.ai_type == ai_type,
                    Proposal.created_at >= datetime.utcnow() - timedelta(days=30)
                )
            ).order_by(Proposal.created_at.desc())
            
            result = await db.execute(query)
            recent_proposals = result.scalars().all()
            
            if not recent_proposals:
                # First proposal from this AI - allow it
                return True, "First proposal from this AI"
            
            # Check if AI has received feedback recently
            recent_feedback = [p for p in recent_proposals if p.user_feedback in ["approved", "rejected"]]
            
            if not recent_feedback:
                # No recent feedback - AI should wait
                return False, "AI needs user feedback before making new proposals"
            
            # Check if enough time has passed since last proposal
            last_proposal = recent_proposals[0]
            time_since_last = datetime.utcnow() - last_proposal.created_at
            
            if time_since_last < self.min_learning_interval:
                return False, f"AI should wait {self.min_learning_interval - time_since_last} before next proposal"
            
            # Check learning metrics
            learning_stats = await self.ai_learning_service.get_learning_stats(ai_type)
            learning_progress = learning_stats.get("learning_progress", 0.0)
            
            if learning_progress < 0.3:  # AI needs more learning
                return False, f"AI learning progress too low ({learning_progress:.2f})"
            
            return True, "AI has sufficient learning"
            
        except Exception as e:
            logger.error("Error checking AI learning status", error=str(e))
            return False, f"Error in learning check: {str(e)}"
    
    async def _check_proposal_limits(self, proposal_data: Dict, db: AsyncSession) -> Tuple[bool, str]:
        """Check if proposal limits are exceeded"""
        try:
            ai_type = proposal_data.get("ai_type", "")
            
            # Count pending proposals for this AI
            query = select(func.count(Proposal.id)).where(
                and_(
                    Proposal.ai_type == ai_type,
                    Proposal.status == "pending"
                )
            )
            result = await db.execute(query)
            pending_count = result.scalar()
            
            if pending_count >= self.max_pending_per_ai:
                return False, f"Maximum pending proposals ({self.max_pending_per_ai}) reached for {ai_type}"
            
            # Check total proposals in last 24 hours
            query = select(func.count(Proposal.id)).where(
                and_(
                    Proposal.ai_type == ai_type,
                    Proposal.created_at >= datetime.utcnow() - timedelta(hours=24)
                )
            )
            result = await db.execute(query)
            daily_count = result.scalar()
            
            if daily_count >= 10:  # Max 10 proposals per AI per day
                return False, f"Daily proposal limit (10) reached for {ai_type}"
            
            return True, "Proposal limits OK"
            
        except Exception as e:
            logger.error("Error checking proposal limits", error=str(e))
            return False, f"Error in limit check: {str(e)}"
    
    async def _check_confidence_threshold(self, proposal_data: Dict) -> Tuple[bool, str]:
        """Check if proposal confidence meets minimum threshold"""
        try:
            confidence = proposal_data.get("confidence", 0.5)
            
            if confidence < self.min_confidence_threshold:
                return False, f"Confidence {confidence:.2f} below threshold {self.min_confidence_threshold}"
            
            return True, f"Confidence {confidence:.2f} meets threshold"
            
        except Exception as e:
            logger.error("Error checking confidence threshold", error=str(e))
            return False, f"Error in confidence check: {str(e)}"
    
    async def _check_improvement_potential(self, proposal_data: Dict, db: AsyncSession) -> Tuple[bool, str]:
        """Check if proposal has sufficient improvement potential"""
        try:
            code_before = proposal_data.get("code_before", "")
            code_after = proposal_data.get("code_after", "")
            improvement_type = proposal_data.get("improvement_type", "general")
            
            # Calculate improvement metrics
            lines_before = len(code_before.split('\n'))
            lines_after = len(code_after.split('\n'))
            chars_before = len(code_before)
            chars_after = len(code_after)
            
            # Check for meaningful changes
            if lines_before == lines_after and chars_before == chars_after:
                return False, "No meaningful changes detected"
            
            # Check for too many changes (might be too risky)
            if abs(lines_after - lines_before) > 50:
                return False, "Too many line changes (risk assessment needed)"
            
            # Check improvement type relevance
            if improvement_type == "general" and abs(lines_after - lines_before) < 3:
                return False, "General improvement with minimal changes"
            
            # Check for common patterns that indicate low-value changes
            if self._is_low_value_change(code_before, code_after):
                return False, "Change appears to be low-value or cosmetic"
            
            return True, "Improvement potential confirmed"
            
        except Exception as e:
            logger.error("Error checking improvement potential", error=str(e))
            return False, f"Error in improvement check: {str(e)}"
    
    def _calculate_similarity(self, proposal_data: Dict, existing_proposal) -> float:
        """Calculate similarity between two proposals"""
        try:
            # Simple string similarity for now
            new_code = proposal_data.get("code_after", "")
            existing_code = existing_proposal.code_after
            
            if not new_code or not existing_code:
                return 0.0
            
            # Calculate Jaccard similarity
            new_words = set(new_code.lower().split())
            existing_words = set(existing_code.lower().split())
            
            if not new_words and not existing_words:
                return 1.0
            
            intersection = len(new_words.intersection(existing_words))
            union = len(new_words.union(existing_words))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.error("Error calculating similarity", error=str(e))
            return 0.0
    
    def _is_low_value_change(self, code_before: str, code_after: str) -> bool:
        """Check if change appears to be low-value"""
        try:
            # Remove whitespace and comments for comparison
            def clean_code(code: str) -> str:
                lines = code.split('\n')
                cleaned_lines = []
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('//') and not stripped.startswith('#'):
                        cleaned_lines.append(stripped)
                return '\n'.join(cleaned_lines)
            
            clean_before = clean_code(code_before)
            clean_after = clean_code(code_after)
            
            # If cleaned codes are identical, it's likely cosmetic
            if clean_before == clean_after:
                return True
            
            # Check for only whitespace/formatting changes
            if clean_before.replace(' ', '') == clean_after.replace(' ', ''):
                return True
            
            return False
            
        except Exception as e:
            logger.error("Error checking low value change", error=str(e))
            return False
    
    async def get_validation_stats(self, db: AsyncSession) -> Dict:
        """Get validation statistics"""
        try:
            # Get recent validation stats
            query = select(Proposal).where(
                Proposal.created_at >= datetime.utcnow() - timedelta(days=7)
            )
            result = await db.execute(query)
            recent_proposals = result.scalars().all()
            
            stats = {
                "total_proposals": len(recent_proposals),
                "by_ai_type": {},
                "by_status": {},
                "validation_rate": 0.0
            }
            
            for proposal in recent_proposals:
                # Count by AI type
                ai_type = proposal.ai_type
                if ai_type not in stats["by_ai_type"]:
                    stats["by_ai_type"][ai_type] = 0
                stats["by_ai_type"][ai_type] += 1
                
                # Count by status
                status = proposal.status
                if status not in stats["by_status"]:
                    stats["by_status"][status] = 0
                stats["by_status"][status] += 1
            
            return stats
            
        except Exception as e:
            logger.error("Error getting validation stats", error=str(e))
            return {} 