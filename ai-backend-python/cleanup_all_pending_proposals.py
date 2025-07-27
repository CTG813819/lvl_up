#!/usr/bin/env python3
"""
Comprehensive Pending Proposal Cleanup Script
=============================================

This script provides a robust system to remove all pending proposals from the backend
and start from zero. It includes:

1. Complete cleanup of all proposal states
2. Detailed reporting and logging
3. Backup functionality before deletion
4. Multiple cleanup strategies
5. Verification of cleanup results
6. System health checks

Usage:
    python cleanup_all_pending_proposals.py [--strategy=aggressive|conservative|selective]
    python cleanup_all_pending_proposals.py --backup-only
    python cleanup_all_pending_proposals.py --verify-only
"""

import asyncio
import json
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import structlog

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.database import get_db, SessionLocal, init_database
from app.models.sql_models import Proposal, Learning, ErrorLearning, Experiment
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

# Configure logging
logger = structlog.get_logger()

class ProposalCleanupService:
    """Comprehensive proposal cleanup service"""
    
    def __init__(self):
        self.cleanup_stats = {
            "total_proposals": 0,
            "pending_proposals": 0,
            "test_passed_proposals": 0,
            "test_failed_proposals": 0,
            "testing_proposals": 0,
            "approved_proposals": 0,
            "rejected_proposals": 0,
            "expired_proposals": 0,
            "deleted_proposals": 0,
            "backup_created": False,
            "backup_path": None,
            "errors": [],
            "warnings": []
        }
        
    async def initialize_database(self) -> bool:
        """Initialize database connection"""
        try:
            await init_database()
            # Verify SessionLocal is properly initialized
            if SessionLocal is None:
                logger.error("❌ SessionLocal is None after init_database")
                self.cleanup_stats["errors"].append("SessionLocal is None after init_database")
                return False
            logger.info("✅ Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            self.cleanup_stats["errors"].append(f"Database initialization failed: {e}")
            return False
    
    async def get_proposal_statistics(self, db: AsyncSession) -> Dict:
        """Get comprehensive proposal statistics"""
        try:
            # Get counts by status
            status_counts = {}
            for status in ["pending", "test-passed", "test-failed", "testing", "approved", "rejected", "expired"]:
                query = select(func.count(Proposal.id)).where(Proposal.status == status)
                result = await db.execute(query)
                count = result.scalar() or 0
                status_counts[status] = count
            
            # Get total count
            total_query = select(func.count(Proposal.id))
            total_result = await db.execute(total_query)
            total_count = total_result.scalar() or 0
            
            # Get AI type distribution
            ai_type_query = select(Proposal.ai_type, func.count(Proposal.id)).group_by(Proposal.ai_type)
            ai_type_result = await db.execute(ai_type_query)
            ai_type_distribution = dict(ai_type_result.all())
            
            # Get age distribution
            now = datetime.utcnow()
            age_ranges = {
                "less_than_1_hour": 0,
                "1_to_6_hours": 0,
                "6_to_24_hours": 0,
                "more_than_24_hours": 0
            }
            
            all_proposals_query = select(Proposal.created_at)
            all_proposals_result = await db.execute(all_proposals_query)
            all_proposals = all_proposals_result.scalars().all()
            
            for proposal in all_proposals:
                if proposal.created_at:
                    age = now - proposal.created_at
                    if age < timedelta(hours=1):
                        age_ranges["less_than_1_hour"] += 1
                    elif age < timedelta(hours=6):
                        age_ranges["1_to_6_hours"] += 1
                    elif age < timedelta(hours=24):
                        age_ranges["6_to_24_hours"] += 1
                    else:
                        age_ranges["more_than_24_hours"] += 1
            
            return {
                "total_proposals": total_count,
                "status_counts": status_counts,
                "ai_type_distribution": ai_type_distribution,
                "age_distribution": age_ranges,
                "timestamp": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting proposal statistics: {e}")
            self.cleanup_stats["errors"].append(f"Statistics error: {e}")
            return {}
    
    async def create_backup(self, db: AsyncSession) -> bool:
        """Create backup of all proposals before deletion"""
        try:
            logger.info("📦 Creating backup of all proposals...")
            
            # Get all proposals
            query = select(Proposal)
            result = await db.execute(query)
            proposals = result.scalars().all()
            
            # Convert to serializable format
            backup_data = []
            for proposal in proposals:
                proposal_dict = {
                    "id": str(proposal.id),
                    "ai_type": proposal.ai_type,
                    "file_path": proposal.file_path,
                    "code_before": proposal.code_before,
                    "code_after": proposal.code_after,
                    "description": proposal.description,
                    "status": proposal.status,
                    "user_feedback": proposal.user_feedback,
                    "test_status": proposal.test_status,
                    "test_output": proposal.test_output,
                    "result": proposal.result,
                    "code_hash": proposal.code_hash,
                    "semantic_hash": proposal.semantic_hash,
                    "diff_score": proposal.diff_score,
                    "duplicate_of": str(proposal.duplicate_of) if proposal.duplicate_of else None,
                    "ai_reasoning": proposal.ai_reasoning,
                    "learning_context": proposal.learning_context,
                    "mistake_pattern": proposal.mistake_pattern,
                    "improvement_type": proposal.improvement_type,
                    "confidence": proposal.confidence,
                    "user_feedback_reason": proposal.user_feedback_reason,
                    "ai_learning_applied": proposal.ai_learning_applied,
                    "previous_mistakes_avoided": proposal.previous_mistakes_avoided,
                    "ai_learning_summary": proposal.ai_learning_summary,
                    "change_type": proposal.change_type,
                    "change_scope": proposal.change_scope,
                    "affected_components": proposal.affected_components,
                    "learning_sources": proposal.learning_sources,
                    "expected_impact": proposal.expected_impact,
                    "risk_assessment": proposal.risk_assessment,
                    "application_response": proposal.application_response,
                    "application_timestamp": proposal.application_timestamp.isoformat() if proposal.application_timestamp else None,
                    "application_result": proposal.application_result,
                    "post_application_analysis": proposal.post_application_analysis,
                    "files_analyzed": proposal.files_analyzed,
                    "created_at": proposal.created_at.isoformat() if proposal.created_at else None,
                    "updated_at": proposal.updated_at.isoformat() if proposal.updated_at else None
                }
                backup_data.append(proposal_dict)
            
            # Create backup file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"proposal_backup_{timestamp}.json"
            
            with open(backup_path, 'w') as f:
                json.dump({
                    "backup_timestamp": datetime.now().isoformat(),
                    "total_proposals": len(backup_data),
                    "proposals": backup_data
                }, f, indent=2)
            
            self.cleanup_stats["backup_created"] = True
            self.cleanup_stats["backup_path"] = backup_path
            
            logger.info(f"✅ Backup created successfully: {backup_path}")
            logger.info(f"📊 Backed up {len(backup_data)} proposals")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            self.cleanup_stats["errors"].append(f"Backup failed: {e}")
            return False
    
    async def cleanup_aggressive(self, db: AsyncSession) -> bool:
        """Aggressive cleanup: Remove ALL proposals regardless of status"""
        try:
            logger.info("🗑️ Starting aggressive cleanup (removing ALL proposals)...")
            
            # Get all proposals
            query = select(Proposal)
            result = await db.execute(query)
            all_proposals = result.scalars().all()
            
            total_count = len(all_proposals)
            logger.info(f"📊 Found {total_count} proposals to delete")
            
            # Delete all proposals
            delete_query = delete(Proposal)
            await db.execute(delete_query)
            await db.commit()
            
            self.cleanup_stats["deleted_proposals"] = total_count
            self.cleanup_stats["total_proposals"] = total_count
            
            logger.info(f"✅ Aggressive cleanup completed: {total_count} proposals deleted")
            return True
            
        except Exception as e:
            logger.error(f"❌ Aggressive cleanup failed: {e}")
            self.cleanup_stats["errors"].append(f"Aggressive cleanup failed: {e}")
            await db.rollback()
            return False
    
    async def cleanup_conservative(self, db: AsyncSession) -> bool:
        """Conservative cleanup: Remove only pending, test-failed, and expired proposals"""
        try:
            logger.info("🧹 Starting conservative cleanup...")
            
            # Define statuses to remove
            statuses_to_remove = ["pending", "test-failed", "expired"]
            
            deleted_count = 0
            
            for status in statuses_to_remove:
                # Get proposals with this status
                query = select(Proposal).where(Proposal.status == status)
                result = await db.execute(query)
                proposals = result.scalars().all()
                
                count = len(proposals)
                if count > 0:
                    logger.info(f"🗑️ Deleting {count} proposals with status '{status}'")
                    
                    # Delete proposals with this status
                    delete_query = delete(Proposal).where(Proposal.status == status)
                    await db.execute(delete_query)
                    
                    deleted_count += count
                    self.cleanup_stats[f"{status.replace('-', '_')}_proposals"] = count
            
            await db.commit()
            self.cleanup_stats["deleted_proposals"] = deleted_count
            
            logger.info(f"✅ Conservative cleanup completed: {deleted_count} proposals deleted")
            return True
            
        except Exception as e:
            logger.error(f"❌ Conservative cleanup failed: {e}")
            self.cleanup_stats["errors"].append(f"Conservative cleanup failed: {e}")
            await db.rollback()
            return False
    
    async def cleanup_selective(self, db: AsyncSession, hours_old: int = 24) -> bool:
        """Selective cleanup: Remove proposals older than specified hours"""
        try:
            logger.info(f"🎯 Starting selective cleanup (removing proposals older than {hours_old} hours)...")
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_old)
            
            # Get old proposals
            query = select(Proposal).where(Proposal.created_at < cutoff_time)
            result = await db.execute(query)
            old_proposals = result.scalars().all()
            
            total_count = len(old_proposals)
            logger.info(f"📊 Found {total_count} proposals older than {hours_old} hours")
            
            if total_count == 0:
                logger.info("✅ No old proposals found to delete")
                return True
            
            # Group by status for reporting
            status_counts = {}
            for proposal in old_proposals:
                status = proposal.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            logger.info(f"📊 Old proposals by status: {status_counts}")
            
            # Delete old proposals
            delete_query = delete(Proposal).where(Proposal.created_at < cutoff_time)
            await db.execute(delete_query)
            await db.commit()
            
            self.cleanup_stats["deleted_proposals"] = total_count
            for status, count in status_counts.items():
                self.cleanup_stats[f"{status.replace('-', '_')}_proposals"] = count
            
            logger.info(f"✅ Selective cleanup completed: {total_count} old proposals deleted")
            return True
            
        except Exception as e:
            logger.error(f"❌ Selective cleanup failed: {e}")
            self.cleanup_stats["errors"].append(f"Selective cleanup failed: {e}")
            await db.rollback()
            return False
    
    async def verify_cleanup(self, db: AsyncSession) -> Dict:
        """Verify cleanup results"""
        try:
            logger.info("🔍 Verifying cleanup results...")
            
            # Get current statistics
            current_stats = await self.get_proposal_statistics(db)
            
            # Check if cleanup was successful
            verification_results = {
                "total_remaining": current_stats.get("total_proposals", 0),
                "pending_remaining": current_stats.get("status_counts", {}).get("pending", 0),
                "test_failed_remaining": current_stats.get("status_counts", {}).get("test-failed", 0),
                "expired_remaining": current_stats.get("status_counts", {}).get("expired", 0),
                "cleanup_successful": False,
                "warnings": []
            }
            
            # Determine if cleanup was successful based on strategy
            if self.cleanup_stats["deleted_proposals"] > 0:
                if current_stats.get("total_proposals", 0) == 0:
                    verification_results["cleanup_successful"] = True
                    logger.info("✅ Verification: All proposals successfully removed")
                elif current_stats.get("status_counts", {}).get("pending", 0) == 0:
                    verification_results["cleanup_successful"] = True
                    logger.info("✅ Verification: All pending proposals successfully removed")
                else:
                    verification_results["warnings"].append("Some proposals still remain")
                    logger.warning("⚠️ Verification: Some proposals still remain")
            
            return verification_results
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return {"cleanup_successful": False, "error": str(e)}
    
    async def generate_cleanup_report(self) -> Dict:
        """Generate comprehensive cleanup report"""
        report = {
            "cleanup_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_proposals_processed": self.cleanup_stats["total_proposals"],
                "proposals_deleted": self.cleanup_stats["deleted_proposals"],
                "backup_created": self.cleanup_stats["backup_created"],
                "backup_path": self.cleanup_stats["backup_path"],
                "errors_encountered": len(self.cleanup_stats["errors"]),
                "warnings": len(self.cleanup_stats["warnings"])
            },
            "detailed_stats": self.cleanup_stats,
            "recommendations": []
        }
        
        # Add recommendations based on results
        if self.cleanup_stats["errors"]:
            report["recommendations"].append("Review errors and consider manual intervention")
        
        if self.cleanup_stats["deleted_proposals"] == 0:
            report["recommendations"].append("No proposals were deleted - verify cleanup strategy")
        
        if not self.cleanup_stats["backup_created"]:
            report["recommendations"].append("Backup was not created - consider manual backup")
        
        return report
    
    async def run_cleanup(self, strategy: str = "conservative", backup: bool = True, 
                         hours_old: int = 24) -> bool:
        """Run the complete cleanup process"""
        try:
            logger.info("🚀 Starting comprehensive proposal cleanup process")
            logger.info(f"📋 Strategy: {strategy}")
            logger.info(f"💾 Backup: {backup}")
            
            # Initialize database
            if not await self.initialize_database():
                return False
            
            # Get initial statistics
            if SessionLocal is None:
                logger.error("❌ SessionLocal is None, cannot proceed with cleanup")
                return False
                
            async with SessionLocal() as db:
                initial_stats = await self.get_proposal_statistics(db)
                self.cleanup_stats.update(initial_stats)
                
                logger.info("📊 Initial proposal statistics:")
                for key, value in initial_stats.get("status_counts", {}).items():
                    logger.info(f"   {key}: {value}")
                
                # Create backup if requested
                if backup:
                    if not await self.create_backup(db):
                        logger.warning("⚠️ Backup failed, but continuing with cleanup")
                
                # Perform cleanup based on strategy
                cleanup_success = False
                if strategy == "aggressive":
                    cleanup_success = await self.cleanup_aggressive(db)
                elif strategy == "conservative":
                    cleanup_success = await self.cleanup_conservative(db)
                elif strategy == "selective":
                    cleanup_success = await self.cleanup_selective(db, hours_old)
                else:
                    logger.error(f"❌ Unknown strategy: {strategy}")
                    return False
                
                if not cleanup_success:
                    return False
                
                # Verify cleanup
                verification = await self.verify_cleanup(db)
                
                # Generate final report
                report = await self.generate_cleanup_report()
                report["verification"] = verification
                
                # Save report
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_path = f"cleanup_report_{timestamp}.json"
                with open(report_path, 'w') as f:
                    json.dump(report, f, indent=2)
                
                logger.info(f"📄 Cleanup report saved: {report_path}")
                
                # Print summary
                logger.info("🎉 Cleanup process completed!")
                logger.info(f"📊 Proposals deleted: {self.cleanup_stats['deleted_proposals']}")
                logger.info(f"💾 Backup created: {self.cleanup_stats['backup_created']}")
                logger.info(f"❌ Errors: {len(self.cleanup_stats['errors'])}")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Cleanup process failed: {e}")
            self.cleanup_stats["errors"].append(f"Process failed: {e}")
            return False

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Comprehensive Proposal Cleanup Tool")
    parser.add_argument("--strategy", choices=["aggressive", "conservative", "selective"], 
                       default="conservative", help="Cleanup strategy")
    parser.add_argument("--backup-only", action="store_true", 
                       help="Only create backup, don't delete")
    parser.add_argument("--verify-only", action="store_true", 
                       help="Only verify current state, don't delete")
    parser.add_argument("--no-backup", action="store_true", 
                       help="Skip backup creation")
    parser.add_argument("--hours-old", type=int, default=24, 
                       help="For selective strategy: remove proposals older than N hours")
    
    args = parser.parse_args()
    
    cleanup_service = ProposalCleanupService()
    
    if args.backup_only:
        logger.info("📦 Backup-only mode")
        if await cleanup_service.initialize_database():
            if SessionLocal is not None:
                async with SessionLocal() as db:
                    await cleanup_service.create_backup(db)
            else:
                logger.error("❌ SessionLocal is None, cannot create backup")
        return
    
    if args.verify_only:
        logger.info("🔍 Verify-only mode")
        if await cleanup_service.initialize_database():
            if SessionLocal is not None:
                async with SessionLocal() as db:
                    stats = await cleanup_service.get_proposal_statistics(db)
                    verification = await cleanup_service.verify_cleanup(db)
                    logger.info("📊 Current proposal statistics:")
                    for key, value in stats.get("status_counts", {}).items():
                        logger.info(f"   {key}: {value}")
                    logger.info(f"🔍 Verification: {verification}")
            else:
                logger.error("❌ SessionLocal is None, cannot verify")
        return
    
    # Run full cleanup
    success = await cleanup_service.run_cleanup(
        strategy=args.strategy,
        backup=not args.no_backup,
        hours_old=args.hours_old
    )
    
    if success:
        logger.info("✅ Cleanup completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Cleanup failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 