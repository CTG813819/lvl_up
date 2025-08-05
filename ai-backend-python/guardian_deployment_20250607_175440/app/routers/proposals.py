"""
Proposals router with ML integration
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
import json
from datetime import datetime, timedelta
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
import asyncio
from app.services.testing_service import TestingService
from app.services.ai_learning_service import AILearningService
from app.models.sql_models import LearningLog

from app.models.proposal import ProposalCreate, ProposalUpdate, ProposalResponse, ProposalStats
from app.models.sql_models import Proposal
from app.core.database import get_db, SessionLocal, init_database
from app.services.ml_service import MLService

logger = structlog.get_logger()
router = APIRouter()

# Create a fresh instance to avoid import timing issues
def get_testing_service():
    """Get a fresh TestingService instance"""
    return TestingService()

# Initialize testing_service as None, will be created when needed
testing_service = None


async def generate_improved_proposal(failed_proposal: Proposal, test_summary: str, db: AsyncSession):
    """Generate an improved proposal based on failed test results"""
    try:
        from app.services.ai_agent_service import AIAgentService
        
        # Analyze the failure and generate improvements
        ai_agent_service = AIAgentService()
        
        # Create improvement context
        improvement_context = f"""
Original proposal failed testing:
- AI Type: {failed_proposal.ai_type}
- File: {failed_proposal.file_path}
- Test Summary: {test_summary}
- Original Code: {failed_proposal.code_after}

Please generate an improved version that addresses the test failures.
"""
        
        # Generate improved proposal based on AI type
        if failed_proposal.ai_type.lower() == "guardian":
            improved_result = await ai_agent_service.run_guardian_agent(
                context=improvement_context,
                focus="fix_test_failures"
            )
        elif failed_proposal.ai_type.lower() == "imperium":
            improved_result = await ai_agent_service.run_imperium_agent(
                context=improvement_context,
                focus="fix_test_failures"
            )
        elif failed_proposal.ai_type.lower() == "sandbox":
            improved_result = await ai_agent_service.run_sandbox_agent(
                context=improvement_context,
                focus="fix_test_failures"
            )
        elif failed_proposal.ai_type.lower() == "conquest":
            improved_result = await ai_agent_service.run_conquest_agent(
                context=improvement_context,
                focus="fix_test_failures"
            )
        else:
            logger.warning(f"Unknown AI type for improvement: {failed_proposal.ai_type}")
            return
        
        # Create new improved proposal
        if improved_result and improved_result.get("code_after"):
            new_proposal = Proposal(
                ai_type=failed_proposal.ai_type,
                file_path=failed_proposal.file_path,
                code_before=failed_proposal.code_before,
                code_after=improved_result["code_after"],
                status="pending",
                result=None,
                user_feedback=None,
                test_status=None,
                test_output=None,
                code_hash=improved_result.get("code_hash", ""),
                semantic_hash=improved_result.get("semantic_hash", ""),
                diff_score=improved_result.get("diff_score", 0.0),
                duplicate_of=None,
                ai_reasoning=f"Improved version based on test failure: {test_summary}",
                learning_context=f"Generated from failed test: {str(failed_proposal.id)}",
                mistake_pattern="test_failure",
                improvement_type="test_fix",
                confidence=improved_result.get("confidence", 0.7),
                user_feedback_reason=None,
                ai_learning_applied=True,
                previous_mistakes_avoided=True
            )
            
            db.add(new_proposal)
            await db.commit()
            await db.refresh(new_proposal)
            
            logger.info("Generated improved proposal from failed test", 
                       original_id=str(failed_proposal.id),
                       new_id=str(new_proposal.id))
        
    except Exception as e:
        logger.error("Error generating improved proposal", 
                    original_id=str(failed_proposal.id),
                    error=str(e))

ml_service = MLService()
ai_learning_service = AILearningService()


# --- Feedback Loop State ---
feedback_loop_logs = []
feedback_loop_lock = asyncio.Lock()

async def feedback_log(message, **kwargs):
    log_entry = {"timestamp": datetime.utcnow().isoformat(), "message": message}
    log_entry.update(kwargs)
    feedback_loop_logs.append(log_entry)
    logger.info(f"[FEEDBACK_LOOP] {message}", **kwargs)

# --- Periodic Proposal Generation Scheduler ---
async def periodic_proposal_generation():
    await asyncio.sleep(5)  # Wait for app startup
    while True:
        try:
            await feedback_log("Periodic proposal generation triggered.")
            # Example: Generate a proposal for each AI type (customize as needed)
            for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:
                await generate_and_test_proposal(ai_type)
        except Exception as e:
            await feedback_log("Error in periodic proposal generation", error=str(e))
        await asyncio.sleep(60)  # 1 minute interval for testing

# --- Proposal Generation, Testing, Learning, Regeneration ---
async def generate_and_test_proposal(ai_type: str):
    print(">>> [MARKER] proposals.py generate_and_test_proposal CALLED <<<")
    print(f"[DEBUG] Starting generate_and_test_proposal for {ai_type}")
    try:
        print("[DEBUG] About to call init_database()")
        await init_database()
        # Access SessionLocal directly through the module to avoid import scope issues
        import app.core.database as database_module
        # Defensive check for SessionLocal
        if database_module.SessionLocal is None:
            logger.error("SessionLocal is None after init_database. Database initialization failed.")
            raise RuntimeError("SessionLocal is None after init_database. Check database configuration and connectivity.")
        print("[DEBUG] init_database() completed successfully")
        # 1. Generate proposal (simulate or use real logic)
        proposal_data = ProposalCreate(
            ai_type=ai_type,
            file_path=f"/path/to/{ai_type}_file.py",
            code_before="# before code",
            code_after="# after code",
            status="pending"
        )
        async with database_module.SessionLocal() as db:
            print("[DEBUG] About to call create_proposal_internal")
            new_proposal = await create_proposal_internal(proposal_data, db)
            print(f"[DEBUG] create_proposal_internal completed: {new_proposal}")
            await feedback_log(f"Proposal generated for {ai_type}", proposal_id=str(new_proposal.id))
            print("[DEBUG] About to create proposal_dict")
            # 2. Test proposal
            proposal_dict = {
                "id": str(new_proposal.id),
                "ai_type": new_proposal.ai_type,
                "file_path": new_proposal.file_path,
                "code_before": new_proposal.code_before,
                "code_after": new_proposal.code_after,
                "improvement_type": getattr(new_proposal, 'improvement_type', None),
                "confidence": getattr(new_proposal, 'confidence', None),
            }
            # Create fresh testing service instance
            print("[DEBUG] Creating fresh TestingService instance")
            testing_service = get_testing_service()
            print(f"[DEBUG] Fresh testing_service created: {testing_service}, type: {type(testing_service)}")
            print(f"[DEBUG] testing_service.test_proposal exists: {hasattr(testing_service, 'test_proposal')}")
            print(f"[DEBUG] testing_service.test_proposal is callable: {callable(getattr(testing_service, 'test_proposal', None))}")
            print("[DEBUG] About to call test_proposal...")
            test_result = await testing_service.test_proposal(proposal_dict)
            print("[DEBUG] test_proposal call completed successfully")
            await feedback_log(f"Proposal tested for {ai_type}", proposal_id=str(new_proposal.id), test_result=test_result)
            # 3. On failure, trigger learning and regeneration
            if test_result and len(test_result) >= 1 and hasattr(test_result[0], 'value') and test_result[0].value == "failed":
                await feedback_log(f"Proposal failed test for {ai_type}", proposal_id=str(new_proposal.id), error=test_result[1] if len(test_result) > 1 else "Unknown error")
                # Trigger learning event
                learning_event = await trigger_learning_from_failure(new_proposal, test_result, db)
                await feedback_log(f"Learning event triggered for failed proposal", proposal_id=str(new_proposal.id), learning_event=learning_event)
                # Regenerate proposal from learning
                await generate_improved_proposal_from_learning(new_proposal, learning_event, db)
    except Exception as e:
        await feedback_log(f"Error in generate_and_test_proposal for {ai_type}", error=str(e))

async def cleanup_old_pending_proposals():
    """Clean up old pending proposals to prevent backlog"""
    try:
        import app.core.database as database_module
        await init_database()
        
        async with database_module.SessionLocal() as db:
            # Check current pending count
            pending_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
            pending_result = await db.execute(pending_query)
            pending_count = pending_result.scalar()
            
            if pending_count > 50:  # If more than 50 pending, clean up old ones
                cutoff_time = datetime.utcnow() - timedelta(minutes=30)  # More aggressive: 30 minutes instead of 1 hour
                
                # Find old pending proposals
                old_pending_query = select(Proposal).where(
                    Proposal.status == "pending",
                    Proposal.created_at < cutoff_time
                )
                old_pending_result = await db.execute(old_pending_query)
                old_pending_proposals = old_pending_result.scalars().all()
                
                if old_pending_proposals:
                    logger.info(f"Cleaning up {len(old_pending_proposals)} old pending proposals")
                    
                    for proposal in old_pending_proposals:
                        proposal.status = "expired"
                        proposal.user_feedback = "expired"
                    
                    await db.commit()
                    await feedback_log(f"Cleaned up {len(old_pending_proposals)} old pending proposals")
                    
    except Exception as e:
        await feedback_log("Error in cleanup_old_pending_proposals", error=str(e))

async def trigger_learning_from_failure(proposal, test_result, db):
    try:
        learning_service = AILearningService()
        learning_event = await learning_service.log_learning_event(
            event_type="proposal_test_failure",
            agent_id=proposal.ai_type,
            agent_type=proposal.ai_type,
            topic=proposal.file_path,
            results_count=1,
            results_sample=[test_result],
            insights=[f"Test failed: {test_result}"] if test_result else [],
            error_message=test_result.get('error') if isinstance(test_result, dict) else None,
            processing_time=None,
            impact_score=0.0,
            event_data={"proposal_id": str(proposal.id), "test_result": test_result}
        )
        return learning_event
    except Exception as e:
        await feedback_log(f"Error triggering learning from failure", error=str(e))
        return None

async def generate_improved_proposal_from_learning(failed_proposal, learning_event, db):
    try:
        # Use the existing generate_improved_proposal logic, but pass learning_event context
        test_summary = learning_event.get("error_message") if learning_event else "Unknown failure"
        await generate_improved_proposal(failed_proposal, test_summary, db)
        await feedback_log(f"Generated improved proposal from learning event", original_id=str(failed_proposal.id))
    except Exception as e:
        await feedback_log(f"Error generating improved proposal from learning", error=str(e))

# --- Startup Hook ---
@router.on_event("startup")
async def start_feedback_loop_scheduler():
    asyncio.create_task(periodic_proposal_generation())
    await feedback_log("Feedback loop scheduler started.")

# --- Feedback Loop Status Endpoint ---
@router.get("/feedback-loop/logs")
async def get_feedback_loop_logs():
    return feedback_loop_logs[-100:]  # Return last 100 log entries


async def create_proposal_internal(proposal: ProposalCreate, db: AsyncSession) -> Proposal:
    """Internal function to create a proposal with a provided database session"""
    try:
        # Check current pending proposal count
        pending_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
        pending_result = await db.execute(pending_query)
        pending_count = pending_result.scalar()
        
        # Limit to 100 pending proposals (increased from 40)
        if pending_count >= 100:
            raise HTTPException(
                status_code=429, 
                detail="Maximum pending proposals reached (100). Please review existing proposals before creating new ones."
            )
        
        # Deduplication: check for existing proposal with same code_hash or semantic_hash
        # Only check for duplicates if we have actual hash values
        if proposal.code_hash is not None or proposal.semantic_hash is not None:
            duplicate_query = select(Proposal).where(
                (Proposal.code_hash == proposal.code_hash) | (Proposal.semantic_hash == proposal.semantic_hash),
                Proposal.status != "rejected"
            )
            duplicate_result = await db.execute(duplicate_query)
            duplicates = duplicate_result.scalars().all()
            if duplicates:
                # If there are multiple duplicates, just use the first one
                duplicate = duplicates[0]
                raise HTTPException(status_code=409, detail="Duplicate proposal already exists.")
        else:
            logger.info("Skipping duplicate check - no hash values provided")
        
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
        
        return new_proposal
        
    except Exception as e:
        logger.error("Error creating proposal", error=str(e), exc_info=True)
        raise


@router.post("/", response_model=ProposalResponse)
async def create_proposal(proposal: ProposalCreate, db: AsyncSession = Depends(get_db)):
    """Create a new proposal with ML analysis and workflow limiting, with deduplication and confidence clamping
    STRICT REQUIREMENT: All proposals must go through LIVE testing before reaching users
    NO STUBS OR SIMULATIONS - ALL TESTS MUST BE REAL"""
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
        # Only check for duplicates if we have actual hash values
        if proposal.code_hash is not None or proposal.semantic_hash is not None:
            duplicate_query = select(Proposal).where(
                (Proposal.code_hash == proposal.code_hash) | (Proposal.semantic_hash == proposal.semantic_hash),
                Proposal.status != "rejected"
            )
            duplicate_result = await db.execute(duplicate_query)
            duplicates = duplicate_result.scalars().all()
            if duplicates:
                # If there are multiple duplicates, just use the first one
                duplicate = duplicates[0]
                raise HTTPException(status_code=409, detail="Duplicate proposal already exists.")
        else:
            logger.info("Skipping duplicate check - no hash values provided")
        
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
        
        # Run LIVE testing on the proposal - NO STUBS OR SIMULATIONS
        try:
            
            # Prepare proposal data for LIVE testing
            proposal_data = {
                "id": str(new_proposal.id),
                "ai_type": new_proposal.ai_type,
                "file_path": new_proposal.file_path,
                "code_before": new_proposal.code_before,
                "code_after": new_proposal.code_after,
                "improvement_type": new_proposal.improvement_type,
                "confidence": new_proposal.confidence,
            }
            
            logger.info("Running LIVE testing on proposal - NO STUBS", proposal_id=str(new_proposal.id))
            
            # Send notification that live testing is starting
            try:
                from app.services.notification_service import notification_service
                await notification_service.notify_live_test_started(
                    str(new_proposal.id), 
                    new_proposal.ai_type, 
                    new_proposal.file_path
                )
            except Exception as e:
                logger.error("Error sending live test started notification", error=str(e))
            
            # Run tests
            overall_result, summary, detailed_results = await testing_service.test_proposal(proposal_data)
            
            # Send notification about test completion
            try:
                detailed_results_json = [result.to_dict() for result in detailed_results]
                await notification_service.notify_live_test_completed(
                    str(new_proposal.id),
                    new_proposal.ai_type,
                    new_proposal.file_path,
                    overall_result.value,
                    summary,
                    detailed_results_json
                )
            except Exception as e:
                logger.error("Error sending live test completion notification", error=str(e))
            
            # Update proposal based on LIVE test results
            if overall_result.value == "passed":
                new_proposal.status = "test-passed"
                new_proposal.test_status = "passed"
                new_proposal.test_output = summary
                logger.info("Proposal passed LIVE testing", proposal_id=str(new_proposal.id))
                
                # Send notification that proposal is ready for users
                try:
                    await notification_service.notify_proposal_ready_for_user(
                        str(new_proposal.id),
                        new_proposal.ai_type,
                        new_proposal.file_path
                    )
                except Exception as e:
                    logger.error("Error sending proposal ready notification", error=str(e))
                    
            elif overall_result.value == "failed":
                new_proposal.status = "test-failed"
                new_proposal.test_status = "failed"
                new_proposal.test_output = summary
                logger.info("Proposal failed LIVE testing", proposal_id=str(new_proposal.id))
                
                # Learn from failed test and generate new proposal
                try:
                    await ai_learning_service.learn_from_proposal(
                        str(new_proposal.id), 
                        "test-failed", 
                        f"Test failed: {summary}"
                    )
                    
                    # Send notification that learning was triggered
                    await notification_service.notify_learning_triggered(
                        str(new_proposal.id),
                        new_proposal.ai_type,
                        f"Test failed: {summary}"
                    )
                    
                    # Generate a new improved proposal based on learning
                    await generate_improved_proposal(new_proposal, summary, db)
                    
                except Exception as e:
                    logger.error("Error learning from failed test", 
                                proposal_id=str(new_proposal.id),
                                error=str(e))
                
                # Learn from failed test and generate new proposal
                try:
                    await ai_learning_service.learn_from_proposal(
                        str(new_proposal.id), 
                        "test-failed", 
                        f"Test failed: {summary}"
                    )
                    
                    # Generate a new improved proposal based on learning
                    await generate_improved_proposal(new_proposal, summary, db)
                    
                except Exception as e:
                    logger.error("Error learning from failed test", 
                                proposal_id=str(new_proposal.id),
                                error=str(e))
            else:  # error or skipped
                new_proposal.status = "test-failed"
                new_proposal.test_status = "error"
                new_proposal.test_output = summary
                logger.warning("Proposal LIVE testing had errors", proposal_id=str(new_proposal.id))
            
            # Store detailed LIVE test results as JSON
            detailed_results_json = [result.to_dict() for result in detailed_results]
            new_proposal.result = json.dumps(detailed_results_json)
            
            await db.commit()
            logger.info("Proposal LIVE testing completed", 
                       proposal_id=str(new_proposal.id),
                       test_result=overall_result.value)
            
        except Exception as e:
            logger.error("Error during LIVE testing", 
                        proposal_id=str(new_proposal.id),
                        error=str(e))
            # Don't fail the proposal creation if testing fails
            # Just log the error and continue
        
        return ProposalResponse.from_orm(new_proposal)
        
    except HTTPException:
        raise
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
    db: AsyncSession = Depends(get_db)
):
    """Get proposals with optional filtering - USERS ONLY SEE TEST-PASSED PROPOSALS"""
    try:
        # Build query - USERS ONLY SEE TEST-PASSED PROPOSALS
        query = select(Proposal)
        
        # CRITICAL: Only show test-passed proposals to users
        # This ensures users only see proposals that have passed rigorous testing
        query = query.where(
            Proposal.status == "test-passed",
            Proposal.test_status == "passed"
        )
        
        if ai_type:
            query = query.where(Proposal.ai_type == ai_type)
        
        # Add ordering and pagination
        query = query.order_by(Proposal.created_at.desc()).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        proposals = result.scalars().all()
        
        # Debug log to verify filtering
        logger.info("Fetched user-ready proposals", 
                   count=len(proposals),
                   statuses=[p.status for p in proposals],
                   test_statuses=[p.test_status for p in proposals],
                   note="Only test-passed proposals shown to users")
        
        return [ProposalResponse.from_orm(proposal) for proposal in proposals]
        
    except Exception as e:
        logger.error("Error getting proposals", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=List[ProposalResponse])
async def list_all_proposals(
    status: Optional[str] = None, 
    ai_type: Optional[str] = None, 
    db: AsyncSession = Depends(get_db)
):
    """Get all proposals including failed ones (ADMIN ONLY endpoint)"""
    try:
        query = select(Proposal).order_by(Proposal.created_at.desc())
        
        if status:
            query = query.where(Proposal.status == status)
        if ai_type:
            query = query.where(Proposal.ai_type == ai_type)
            
        result = await db.execute(query)
        proposals = result.scalars().all()
        
        logger.info("Fetched all proposals (admin)", 
                   count=len(proposals),
                   statuses=[p.status for p in proposals],
                   note="Admin endpoint - shows all proposals including failed ones")
        
        return [ProposalResponse.from_orm(proposal) for proposal in proposals]
        
    except Exception as e:
        logger.error("Error getting all proposals", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{proposal_id}/accept")
async def accept_proposal(proposal_id: str, db: AsyncSession = Depends(get_db)):
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
    proposal = await db.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Set status to testing first
    proposal.status = "testing"
    proposal.user_feedback = "accepted"
    proposal.test_status = "pending"
    await db.commit()
    
    try:
        # Import notification service
        from app.services.notification_service import notification_service
        
        # Send notification that live testing is starting for acceptance
        try:
            await notification_service.notify_live_test_started(
                str(proposal.id),
                proposal.ai_type,
                proposal.file_path
            )
        except Exception as e:
            logger.error("Error sending live test started notification for acceptance", error=str(e))
        
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
        
        # Send notification about test completion
        try:
            detailed_results_json = [result.to_dict() for result in detailed_results]
            await notification_service.notify_live_test_completed(
                str(proposal.id),
                proposal.ai_type,
                proposal.file_path,
                overall_result.value,
                summary,
                detailed_results_json
            )
        except Exception as e:
            logger.error("Error sending live test completion notification for acceptance", error=str(e))
        
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
        
        await db.commit()
        
        # Generate a new pending proposal after approval
        new_proposal = Proposal(
            ai_type=proposal.ai_type,
            file_path=proposal.file_path,
            code_before=proposal.code_before,
            code_after=proposal.code_after,
            status="pending",
            user_feedback=None,
            test_status=None,
            test_output=None,
            code_hash=proposal.code_hash,
            semantic_hash=proposal.semantic_hash,
            diff_score=proposal.diff_score,
            duplicate_of=proposal.duplicate_of,
            ai_reasoning=proposal.ai_reasoning,
            learning_context=proposal.learning_context,
            mistake_pattern=proposal.mistake_pattern,
            improvement_type=proposal.improvement_type,
            confidence=proposal.confidence,
            user_feedback_reason=None,
            ai_learning_applied=proposal.ai_learning_applied,
            previous_mistakes_avoided=proposal.previous_mistakes_avoided
        )
        db.add(new_proposal)
        await db.commit()
        await db.refresh(new_proposal)
        # Debug log
        logger = structlog.get_logger()
        logger.info("Proposal approved and new pending proposal created", old_id=str(proposal.id), old_status=proposal.status, new_id=str(new_proposal.id), new_status=new_proposal.status)
        return {
            "status": "success", 
            "test_status": proposal.test_status, 
            "test_output": proposal.test_output,
            "overall_result": overall_result.value,
            "detailed_results": detailed_results_json,
            "new_proposal_id": str(new_proposal.id)
        }
        
    except Exception as e:
        # If testing fails, mark as test error
        proposal.status = "test-failed"
        proposal.test_status = "error"
        proposal.test_output = f"Test execution failed: {str(e)}"
        await db.commit()
        
        logger.error(f"Error testing proposal {proposal_id}: {str(e)}")
        return {
            "status": "error",
            "test_status": "error",
            "test_output": f"Test execution failed: {str(e)}"
        }

@router.post("/{proposal_id}/reject")
async def reject_proposal(proposal_id: str, db: AsyncSession = Depends(get_db)):
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
    proposal = await db.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    proposal.status = "rejected"
    proposal.user_feedback = "rejected"
    await db.commit()
    # Generate a new pending proposal after rejection
    new_proposal = Proposal(
        ai_type=proposal.ai_type,
        file_path=proposal.file_path,
        code_before=proposal.code_before,
        code_after=proposal.code_after,
        status="pending",
        user_feedback=None,
        test_status=None,
        test_output=None,
        code_hash=proposal.code_hash,
        semantic_hash=proposal.semantic_hash,
        diff_score=proposal.diff_score,
        duplicate_of=proposal.duplicate_of,
        ai_reasoning=proposal.ai_reasoning,
        learning_context=proposal.learning_context,
        mistake_pattern=proposal.mistake_pattern,
        improvement_type=proposal.improvement_type,
        confidence=proposal.confidence,
        user_feedback_reason=None,
        ai_learning_applied=proposal.ai_learning_applied,
        previous_mistakes_avoided=proposal.previous_mistakes_avoided
    )
    db.add(new_proposal)
    await db.commit()
    await db.refresh(new_proposal)
    # Debug log
    logger = structlog.get_logger()
    logger.info("Proposal rejected and new pending proposal created", old_id=str(proposal.id), old_status=proposal.status, new_id=str(new_proposal.id), new_status=new_proposal.status)
    return {
        "status": "success", 
        "message": f"Proposal {proposal_id} rejected and new pending proposal created.",
        "new_proposal_id": str(new_proposal.id)
    }


@router.get("/ai-status")
async def get_ai_status(db: AsyncSession = Depends(get_db)):
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
async def get_proposal(proposal_id: str, db: AsyncSession = Depends(get_db)):
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
async def update_proposal(proposal_id: str, proposal_update: ProposalUpdate, db: AsyncSession = Depends(get_db)):
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
async def delete_proposal(proposal_id: str, db: AsyncSession = Depends(get_db)):
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
async def get_proposal_stats(db: AsyncSession = Depends(get_db)):
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
async def analyze_proposal(proposal_id: str, db: AsyncSession = Depends(get_db)):
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
async def apply_proposal(proposal_id: str, db: AsyncSession = Depends(get_db)):
    """Apply a proposal to the app with additional safety testing"""
    proposal = await db.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # ENHANCED REQUIREMENTS: Only apply proposals that have passed rigorous testing
    if proposal.status != "accepted" or proposal.test_status != "passed":
        raise HTTPException(
            status_code=400, 
            detail="Proposal must be accepted AND have passed rigorous testing before applying"
        )
    
    try:
        # ADDITIONAL SAFETY CHECK: Run one final test before applying
        from app.services.notification_service import notification_service
        
        logger.info(f"Running final safety test before applying proposal {proposal_id}")
        
        # Prepare proposal data for final testing
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
        final_result, final_summary, final_detailed_results = await testing_service.test_proposal(proposal_data)
        
        if final_result.value != "passed":
            logger.error(f"Final safety test failed for proposal {proposal_id}: {final_summary}")
            proposal.status = "apply-failed"
            proposal.user_feedback = f"Final safety test failed: {final_summary}"
            proposal.updated_at = datetime.utcnow()
            await db.commit()
            
            # Notify about failed final test
            try:
                await notification_service.notify_apply_failed(
                    str(proposal.id),
                    proposal.ai_type,
                    proposal.file_path,
                    final_summary
                )
            except Exception as e:
                logger.error("Error sending apply failed notification", error=str(e))
            
            raise HTTPException(
                status_code=400, 
                detail=f"Final safety test failed: {final_summary}"
            )
        
        # FINAL SAFETY TEST PASSED - Apply the proposal
        logger.info(f"Final safety test passed, applying proposal {proposal_id}")
        
        # Write code_after to file_path
        file_path = proposal.file_path
        code_after = proposal.code_after
        if not file_path or not code_after:
            raise Exception("Proposal missing file_path or code_after")
        
        # Create backup of original file
        import shutil
        import os
        backup_path = f"{file_path}.backup.{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Apply the code change
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code_after)
        
        # Update proposal status
        proposal.status = "applied"
        proposal.user_feedback = "applied"
        proposal.updated_at = datetime.utcnow()
        await db.commit()
        
        # Notify about successful application
        try:
            await notification_service.notify_apply_success(
                str(proposal.id),
                proposal.ai_type,
                proposal.file_path,
                final_summary
            )
        except Exception as e:
            logger.error("Error sending apply success notification", error=str(e))
        
        # Call learning service for successful application
        try:
            from app.services.ai_learning_service import AILearningService
            ai_learning_service = AILearningService()
            await ai_learning_service.learn_from_proposal(proposal_id, "applied")
        except Exception as le:
            logger.warning(f"Learning event not recorded: {le}")
        
        logger.info(f"Successfully applied proposal {proposal_id} to {file_path}")
        
        return {
            "status": "success", 
            "message": "Proposal applied successfully after rigorous testing",
            "file_path": file_path,
            "backup_path": backup_path,
            "final_test_summary": final_summary
        }
        
    except Exception as e:
        proposal.status = "apply-failed"
        proposal.user_feedback = f"apply-failed: {str(e)}"
        proposal.updated_at = datetime.utcnow()
        await db.commit()
        
        # Call learning service for failure
        try:
            from app.services.ai_learning_service import AILearningService
            ai_learning_service = AILearningService()
            await ai_learning_service.learn_from_proposal(proposal_id, "apply-failed", feedback_reason=str(e))
        except Exception as le:
            logger.warning(f"Learning event not recorded: {le}")
        
        logger.error(f"Error applying proposal {proposal_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Apply failed: {e}")


@router.post("/{proposal_id}/auto-apply")
async def auto_apply_proposal(proposal_id: str, db: AsyncSession = Depends(get_db)):
    """Automatically apply a proposal after user approval (real-time update system)"""
    proposal = await db.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # STRICT REQUIREMENTS: Only auto-apply proposals that have passed rigorous testing
    if proposal.status != "accepted" or proposal.test_status != "passed":
        raise HTTPException(
            status_code=400, 
            detail="Proposal must be accepted AND have passed rigorous testing for auto-application"
        )
    
    try:
        # Run final safety test
        from app.services.notification_service import notification_service
        
        logger.info(f"Auto-applying proposal {proposal_id} after user approval")
        
        # Prepare proposal data for final testing
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
        final_result, final_summary, final_detailed_results = await testing_service.test_proposal(proposal_data)
        
        if final_result.value != "passed":
            logger.error(f"Auto-apply final test failed for proposal {proposal_id}: {final_summary}")
            proposal.status = "auto-apply-failed"
            proposal.user_feedback = f"Auto-apply final test failed: {final_summary}"
            proposal.updated_at = datetime.utcnow()
            await db.commit()
            
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
            
            raise HTTPException(
                status_code=400, 
                detail=f"Auto-apply final test failed: {final_summary}"
            )
        
        # FINAL TEST PASSED - Auto-apply the proposal
        logger.info(f"Auto-applying proposal {proposal_id} after final test passed")
        
        # Write code_after to file_path
        file_path = proposal.file_path
        code_after = proposal.code_after
        if not file_path or not code_after:
            raise Exception("Proposal missing file_path or code_after")
        
        # Create backup of original file
        import shutil
        import os
        backup_path = f"{file_path}.backup.{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup for auto-apply: {backup_path}")
        
        # Apply the code change
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code_after)
        
        # Update proposal status
        proposal.status = "auto-applied"
        proposal.user_feedback = "auto-applied"
        proposal.updated_at = datetime.utcnow()
        await db.commit()
        
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
            from app.services.ai_learning_service import AILearningService
            ai_learning_service = AILearningService()
            await ai_learning_service.learn_from_proposal(proposal_id, "auto-applied")
        except Exception as le:
            logger.warning(f"Learning event not recorded: {le}")
        
        logger.info(f"Successfully auto-applied proposal {proposal_id} to {file_path}")
        
        return {
            "status": "success", 
            "message": "Proposal auto-applied successfully after rigorous testing",
            "file_path": file_path,
            "backup_path": backup_path,
            "final_test_summary": final_summary,
            "auto_applied": True
        }
        
    except Exception as e:
        proposal.status = "auto-apply-failed"
        proposal.user_feedback = f"auto-apply-failed: {str(e)}"
        proposal.updated_at = datetime.utcnow()
        await db.commit()
        
        # Call learning service for failure
        try:
            from app.services.ai_learning_service import AILearningService
            ai_learning_service = AILearningService()
            await ai_learning_service.learn_from_proposal(proposal_id, "auto-apply-failed", feedback_reason=str(e))
        except Exception as le:
            logger.warning(f"Learning event not recorded: {le}")
        
        logger.error(f"Error auto-applying proposal {proposal_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Auto-apply failed: {e}")
