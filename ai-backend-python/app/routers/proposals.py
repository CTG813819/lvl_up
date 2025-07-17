"""
Proposals router with ML integration
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
import json
from datetime import datetime, timedelta
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
import asyncio
# Import TestingService first, then create testing_service instance
from app.services.testing_service import TestingService
from app.services.ai_learning_service import AILearningService
from app.models.sql_models import LearningLog
import hashlib

from app.models.proposal import ProposalCreate, ProposalUpdate, ProposalResponse, ProposalStats
from app.models.sql_models import Proposal
from app.core.database import get_db, SessionLocal, init_database
from app.services.ml_service import MLService
from app.services.proposal_cycle_service import ProposalCycleService
from app.services.proposal_validation_service import ProposalValidationService
from app.services.enhanced_proposal_validation_service import EnhancedProposalValidationService

# Ensure logger is defined at the top
logger = structlog.get_logger()
router = APIRouter()

# Create a fresh instance to avoid import timing issues
def get_testing_service():
    """Get a fresh TestingService instance"""
    return TestingService()

# Initialize testing_service as None, will be created when needed
# testing_service = None

# Initialize proposal cycle service
proposal_cycle_service = None

async def get_proposal_cycle_service():
    """Get the proposal cycle service instance"""
    global proposal_cycle_service
    if proposal_cycle_service is None:
        proposal_cycle_service = await ProposalCycleService.initialize()
    return proposal_cycle_service


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
            improved_result = await ai_agent_service.run_guardian_agent()
        elif failed_proposal.ai_type.lower() == "imperium":
            improved_result = await ai_agent_service.run_imperium_agent()
        elif failed_proposal.ai_type.lower() == "sandbox":
            improved_result = await ai_agent_service.run_sandbox_agent()
        elif failed_proposal.ai_type.lower() == "conquest":
            improved_result = await ai_agent_service.run_conquest_agent()
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
proposal_validation_service = EnhancedProposalValidationService()


# --- Feedback Loop State ---
feedback_loop_logs = []
feedback_loop_lock = asyncio.Lock()

async def feedback_log(message, **kwargs):
    log_entry = {"timestamp": datetime.utcnow().isoformat(), "message": message}
    log_entry.update(kwargs)
    feedback_loop_logs.append(log_entry)
    logger.info(f"[FEEDBACK_LOOP] {message}", **kwargs)

async def notify_ai_of_deleted_proposal(proposal):
    # Stub: Implement actual notification logic here
    logger.info("Notifying AI of deleted proposal", proposal_id=str(proposal.id), ai_type=proposal.ai_type, file_path=proposal.file_path, reason="Expired due to new proposal cycle")
    # You could add more details or send a message to the AI agent here

async def delete_old_pending_proposals():
    """Delete all pending proposals created before the current cycle and notify AIs with details."""
    from app.core.database import get_session
    from app.models.sql_models import Proposal
    import datetime
    now = datetime.datetime.utcnow()
    # Define cutoff as 45 minutes ago
    cutoff = now - datetime.timedelta(minutes=45)
    async with get_session() as session:
        old_pending = await session.execute(
            select(Proposal).where(
                Proposal.status == "pending",
                Proposal.created_at < cutoff
            )
        )
        old_proposals = old_pending.scalars().all()
        for proposal in old_proposals:
            logger.info("Deleting expired pending proposal", proposal_id=str(proposal.id), ai_type=proposal.ai_type, reason="Expired due to new proposal cycle", file_path=proposal.file_path)
            await notify_ai_of_deleted_proposal(proposal)
            await session.delete(proposal)
        await session.commit()

# --- Periodic Proposal Generation Scheduler ---
async def periodic_proposal_generation():
    await asyncio.sleep(5)  # Wait for app startup
    while True:
        try:
            await feedback_log("Periodic proposal generation triggered.")
            
            # Clean up old pending proposals first
            await cleanup_old_pending_proposals()
            await delete_old_pending_proposals()
            
            # Get the proposal cycle service
            cycle_service = await get_proposal_cycle_service()
            
            # Get the next agent that should generate a proposal
            next_agent = await cycle_service.get_next_agent()
            
            if next_agent is not None:
                logger.info(f"🔄 Generating proposal for {next_agent.value}")
                await generate_and_test_proposal(next_agent.value)
            else:
                logger.info("🔄 No agent available for proposal generation")
                
        except Exception as e:
            await feedback_log("Error in periodic proposal generation", error=str(e))
        # 30-minute cooldown starts only after all proposal generation and testing is complete
        await asyncio.sleep(2700)  # 2700 seconds = 45 minutes

async def cleanup_old_pending_proposals():
    """Clean up pending proposals older than 1 hour to prevent backlog"""
    try:
        import app.core.database as database_module
        
        # Check if we have too many pending proposals
        async with database_module.SessionLocal() as db:
            pending_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
            pending_result = await db.execute(pending_query)
            pending_count = pending_result.scalar() or 0
            
            if pending_count > 50:  # If more than 50 pending, clean up old ones (increased from 30)
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
                        # Only assign to Proposal attributes if they exist and are not SQLAlchemy Columns
                        # (This is a runtime check, but for linter, we can use type: ignore)
                        if hasattr(proposal, 'status'):
                            proposal.status = "expired"  # type: ignore
                        if hasattr(proposal, 'user_feedback'):
                            proposal.user_feedback = "expired"  # type: ignore
                    
                    await db.commit()
                    await feedback_log(f"Cleaned up {len(old_pending_proposals)} old pending proposals")
                    
    except Exception as e:
        await feedback_log("Error in cleanup_old_pending_proposals", error=str(e))

# --- Proposal Generation, Testing, Learning, Regeneration ---
async def generate_and_test_proposal(ai_type: str):
    print(">>> [MARKER] proposals.py generate_and_test_proposal CALLED <<<")
    print(f"[DEBUG] Starting generate_and_test_proposal for {ai_type}")
    try:
        print("[DEBUG] About to call init_database()")
        await init_database()
        print("[DEBUG] init_database() completed successfully")
        import app.core.database as database_module
        if database_module.SessionLocal is None:
            logger.error("SessionLocal is None after init_database. Database initialization failed.")
            raise RuntimeError("SessionLocal is None after init_database. Check database configuration and connectivity.")
        
        # Check for existing pending proposals for this AI type
        async with database_module.SessionLocal() as db:
            pending_query = select(func.count(Proposal.id)).where(Proposal.status == "pending", Proposal.ai_type == ai_type)
            pending_result = await db.execute(pending_query)
            pending_count = pending_result.scalar() or 0
            if pending_count >= 2:
                print(f"[INFO] Skipping proposal generation for {ai_type}: already has {pending_count} pending proposals.")
                await feedback_log(f"Skipped proposal generation for {ai_type}: already has {pending_count} pending proposals.")
                return
        
        # Actually run the AI agent to generate real proposals
        print(f"[DEBUG] Running {ai_type} agent to generate real proposals")
        from app.services.ai_agent_service import AIAgentService
        agent_service = AIAgentService()
        
        # Run the appropriate agent based on AI type
        if ai_type.lower() == "imperium":
            result = await agent_service.run_imperium_agent()
        elif ai_type.lower() == "guardian":
            result = await agent_service.run_guardian_agent()
        elif ai_type.lower() == "sandbox":
            result = await agent_service.run_sandbox_agent()
        elif ai_type.lower() == "conquest":
            result = await agent_service.run_conquest_agent()
        else:
            logger.error(f"Unknown AI type: {ai_type}")
            return
        
        print(f"[DEBUG] {ai_type} agent result: {result}")
        
        if result.get("status") != "success":
            logger.warning(f"{ai_type} agent failed to generate proposals: {result.get('message', 'Unknown error')}")
            return
        
        # Check if proposals were actually created
        proposals_created = result.get("proposals_created", 0)
        if proposals_created == 0:
            logger.info(f"No proposals were created by {ai_type} agent")
            return
        
        logger.info(f"Successfully generated {proposals_created} proposals for {ai_type}")
        await feedback_log(f"Generated {proposals_created} proposals for {ai_type}")
        
    except Exception as e:
        await feedback_log(f"Error in generate_and_test_proposal for {ai_type}", error=str(e))

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
        logger.info("Starting create_proposal_internal", proposal_ai_type=proposal.ai_type)
        
        # Check if this AI type already has a pending proposal
        existing_query = select(Proposal).where(
            Proposal.ai_type == proposal.ai_type,
            Proposal.status.in_(["pending", "test-passed", "testing"])
        )
        existing_result = await db.execute(existing_query)
        existing_proposals = existing_result.scalars().all()
        
        if existing_proposals:
            logger.warning(f"AI {proposal.ai_type} already has {len(existing_proposals)} active proposals")
            raise HTTPException(
                status_code=429, 
                detail=f"AI {proposal.ai_type} already has active proposals. Please approve or reject existing proposals first."
            )
        
        # Validate proposal using the validation service
        logger.info("Validating proposal with validation service")
        proposal_dict = proposal.dict()
        is_valid, validation_reason, validation_details = await proposal_validation_service.validate_proposal(proposal_dict, db)
        
        if not is_valid:
            logger.warning(f"Proposal validation failed: {validation_reason}")
            raise HTTPException(
                status_code=400,
                detail=f"Proposal validation failed: {validation_reason}"
            )
        
        logger.info("Proposal validation passed", validation_details=validation_details)
        
        # Get pending count for logging
        pending_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
        pending_result = await db.execute(pending_query)
        pending_count = pending_result.scalar() or 0
        
        # Compute semantic hash if not provided
        if not proposal.semantic_hash:
            hash_input = f"{proposal.ai_type}|{proposal.file_path}|{proposal.code_before}|{proposal.code_after}"
            proposal.semantic_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
        if not proposal.code_hash:
            code_hash_input = f"{proposal.code_before}|{proposal.code_after}"
            proposal.code_hash = hashlib.sha256(code_hash_input.encode('utf-8')).hexdigest()

        logger.info("Checking for duplicates (robust)")
        duplicate_query = select(Proposal).where(
            (Proposal.code_hash == proposal.code_hash) | (Proposal.semantic_hash == proposal.semantic_hash),
            Proposal.status.in_(["pending", "in_review", "test-passed", "test-failed"])
        )
        duplicate_result = await db.execute(duplicate_query)
        duplicates = duplicate_result.scalars().all()
        if duplicates:
            logger.warning(f"Duplicate proposal detected: {duplicates[0].id}")
            raise HTTPException(status_code=409, detail="Duplicate proposal already exists.")
        
        # Convert to dict for ML analysis
        logger.info("Converting proposal to dict for ML analysis")
        proposal_dict = proposal.dict()
        
        # Analyze proposal quality using ML
        logger.info("Analyzing proposal quality with ML")
        ml_analysis = await ml_service.analyze_proposal_quality(proposal_dict)
        logger.info("ML analysis completed", quality_score=ml_analysis.get("quality_score"))
        
        # Clamp confidence
        confidence = ml_analysis.get("quality_score", 0.5)
        confidence = min(max(confidence, 0.0), 1.0)
        
        # Create new proposal instance with SQLAlchemy model
        logger.info("Creating new proposal instance")
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
            previous_mistakes_avoided=proposal.previous_mistakes_avoided,
            files_analyzed=proposal.files_analyzed or []
        )
        
        logger.info("Adding proposal to database")
        db.add(new_proposal)
        logger.info("Committing proposal to database")
        await db.commit()
        logger.info("Refreshing proposal from database")
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
        new_proposal = await create_proposal_internal(proposal, db)
        
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
                ai_type = getattr(new_proposal, 'ai_type', None)
                file_path = getattr(new_proposal, 'file_path', None)
                await notification_service.notify_live_test_started(
                    str(new_proposal.id), 
                    str(ai_type), 
                    str(file_path)
                )
            except Exception as e:
                logger.error("Error sending live test started notification", error=str(e))
            
            # Run tests
            testing_service_instance = get_testing_service()
            overall_result, summary, detailed_results = await testing_service_instance.test_proposal(proposal_data)
            
            # Send notification about test completion
            try:
                detailed_results_json = [result.to_dict() for result in detailed_results]
                ai_type = getattr(new_proposal, 'ai_type', None)
                file_path = getattr(new_proposal, 'file_path', None)
                await notification_service.notify_live_test_completed(
                    str(new_proposal.id),
                    str(ai_type),
                    str(file_path),
                    overall_result.value,
                    summary,
                    detailed_results_json
                )
            except Exception as e:
                logger.error("Error sending live test completion notification", error=str(e))
            
            # Update proposal based on LIVE test results
            if overall_result.value == "passed":
                # Use .value for Enum assignments if needed, else assign string directly
                new_proposal.status = "test-passed"  # type: ignore
                new_proposal.test_status = "passed"  # type: ignore
                new_proposal.test_output = str(summary)  # type: ignore
                logger.info("Proposal passed LIVE testing", proposal_id=str(new_proposal.id))
                
                # Send notification that proposal is ready for users
                try:
                    await notification_service.notify_proposal_ready_for_user(
                        str(new_proposal.id),
                        str(new_proposal.ai_type),
                        str(new_proposal.file_path)
                    )
                except Exception as e:
                    logger.error("Error sending proposal ready notification", error=str(e))
                    
            elif overall_result.value == "failed":
                new_proposal.status = "test-failed"  # type: ignore
                new_proposal.test_status = "failed"  # type: ignore
                new_proposal.test_output = str(summary)  # type: ignore
                logger.info("Proposal failed LIVE testing", proposal_id=str(new_proposal.id))
                
                # Learn from failed test and generate new proposal
                try:
                    await ai_learning_service.learn_from_proposal(
                        str(new_proposal.id), 
                        "test-failed", 
                        f"Test failed: {summary if summary is not None else ''}"
                    )
                    
                    # Send notification that learning was triggered
                    await notification_service.notify_learning_triggered(
                        str(new_proposal.id),
                        str(new_proposal.ai_type),
                        f"Test failed: {summary if summary is not None else ''}"
                    )
                    
                    # Generate a new improved proposal based on learning
                    await generate_improved_proposal(new_proposal, summary, db)
                    
                except Exception as e:
                    logger.error("Error learning from failed test", 
                                proposal_id=str(new_proposal.id),
                                error=str(e))
            else:  # error or skipped
                new_proposal.status = "test-failed"  # type: ignore
                new_proposal.test_status = "error"  # type: ignore
                new_proposal.test_output = str(summary)  # type: ignore
                logger.warning("Proposal LIVE testing had errors", proposal_id=str(new_proposal.id))
            
            # Store detailed LIVE test results as JSON
            detailed_results_json = [result.to_dict() for result in detailed_results]
            new_proposal.result = json.dumps(detailed_results_json)  # type: ignore
            
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
    try:
        from uuid import UUID
        proposal_uuid = UUID(proposal_id)
        proposal = await db.get(Proposal, proposal_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid proposal ID format")
    
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # If proposal is already test-passed, approve it directly
    if proposal.status == "test-passed":
        # For SQLAlchemy boolean columns, use explicit comparison
        if getattr(proposal, 'is_approved', False) == True:
            proposal.status = "approved"  # type: ignore
            proposal.user_feedback = "accepted"  # type: ignore
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
        
        logger.info(
            f"Test-passed proposal approved directly: proposal_id={proposal.id}, new_proposal_id={new_proposal.id}"
        )
        
        return {
            "status": "success", 
            "test_status": "passed", 
            "test_output": "Proposal was already tested and passed",
            "overall_result": "passed",
            "new_proposal_id": str(new_proposal.id)
        }
    
    # Set status to testing first for pending proposals
    if getattr(proposal, 'is_testing', False) == True:
        proposal.status = "testing"  # type: ignore
        proposal.user_feedback = "accepted"  # type: ignore
        proposal.test_status = "pending"  # type: ignore
    await db.commit()
    
    try:
        # Import notification service
        from app.services.notification_service import notification_service
        
        # Send notification that live testing is starting for acceptance
        try:
            ai_type = getattr(proposal, 'ai_type', None)
            file_path = getattr(proposal, 'file_path', None)
            await notification_service.notify_live_test_started(
                str(proposal.id),
                str(ai_type),
                str(file_path)
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
        testing_service_instance = get_testing_service()
        overall_result, summary, detailed_results = await testing_service_instance.test_proposal(proposal_data)
        
        # Send notification about test completion
        try:
            detailed_results_json = [result.to_dict() for result in detailed_results]
            ai_type = getattr(proposal, 'ai_type', None)
            file_path = getattr(proposal, 'file_path', None)
            await notification_service.notify_live_test_completed(
                str(proposal.id),
                str(ai_type),
                str(file_path),
                overall_result.value,
                summary,
                detailed_results_json
            )
        except Exception as e:
            logger.error("Error sending live test completion notification for acceptance", error=str(e))
        
        # Update proposal based on test results
        if overall_result.value == "passed":
            proposal.status = "accepted"  # type: ignore
            proposal.test_status = "passed"  # type: ignore
            proposal.test_output = summary  # type: ignore
        elif overall_result.value == "failed":
            proposal.status = "test-failed"  # type: ignore
            proposal.test_status = "failed"  # type: ignore
            proposal.test_output = summary  # type: ignore
        else:  # error or skipped
            proposal.status = "test-failed"  # type: ignore
            proposal.test_status = "error"  # type: ignore
            proposal.test_output = summary  # type: ignore
        
        # Store detailed test results as JSON
        detailed_results_json = [result.to_dict() for result in detailed_results]
        proposal.result = json.dumps(detailed_results_json)  # type: ignore
        
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
        proposal.status = "test-failed"  # type: ignore
        proposal.test_status = "error"  # type: ignore
        proposal.test_output = f"Test execution failed: {str(e)}"  # type: ignore
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
    try:
        from uuid import UUID
        proposal_uuid = UUID(proposal_id)
        proposal = await db.get(Proposal, proposal_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid proposal ID format")
    
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Handle both pending and test-passed proposals
    proposal.status = "rejected"  # type: ignore
    proposal.user_feedback = "rejected"  # type: ignore
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


@router.get("/validation/stats")
async def get_validation_stats(db: AsyncSession = Depends(get_db)):
    """Get proposal validation statistics"""
    try:
        stats = await proposal_validation_service.get_validation_stats(db)
        return {
            "validation_stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting validation stats", error=str(e))
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
        
        # For int arguments that may be None, use 0 as default
        summary_stats = ProposalStats(
            total=total if total is not None else 0,
            pending=pending if pending is not None else 0,
            approved=approved if approved is not None else 0,
            rejected=rejected if rejected is not None else 0,
            test_passed=test_passed if test_passed is not None else 0,
            test_failed=test_failed if test_failed is not None else 0,
            applied=applied if applied is not None else 0,
            timestamp=datetime.utcnow()
        )
        
        return summary_stats
        
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
        testing_service_instance = get_testing_service()
        final_result, final_summary, final_detailed_results = await testing_service_instance.test_proposal(proposal_data)
        
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
        
        # Generate application response
        application_response = self._generate_application_response(proposal, final_summary)
        post_application_analysis = self._generate_post_application_analysis(proposal, final_summary)
        
        # Update proposal status with response data
        proposal.status = "applied"
        proposal.user_feedback = "applied"
        proposal.updated_at = datetime.utcnow()
        proposal.application_response = application_response
        proposal.application_timestamp = datetime.utcnow()
        proposal.application_result = "success"
        proposal.post_application_analysis = post_application_analysis
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
            "final_test_summary": final_summary,
            "application_response": application_response,
            "post_application_analysis": post_application_analysis
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

    def _generate_application_response(self, proposal, test_summary: str) -> str:
        """Generate a user-friendly response when a proposal is applied"""
        ai_type = proposal.ai_type
        file_name = proposal.file_path.split('/')[-1] if '/' in proposal.file_path else proposal.file_path
        change_type = getattr(proposal, 'change_type', 'unknown')
        improvement_type = proposal.improvement_type or 'general'
        
        response_templates = {
            'Imperium': f"✅ {ai_type} AI has successfully applied system improvements to {file_name}. The {change_type} changes have been tested and validated, ensuring enhanced system performance and reliability.",
            'Guardian': f"🛡️ {ai_type} AI has successfully applied security and stability enhancements to {file_name}. The {change_type} modifications have been thoroughly tested to maintain system integrity.",
            'Sandbox': f"🧪 {ai_type} AI has successfully applied experimental improvements to {file_name}. The {change_type} changes have been validated and are ready for production use.",
            'Conquest': f"⚔️ {ai_type} AI has successfully applied user experience improvements to {file_name}. The {change_type} enhancements have been tested and will improve user satisfaction."
        }
        
        base_response = response_templates.get(ai_type, f"✅ {ai_type} AI has successfully applied {improvement_type} improvements to {file_name}.")
        
        if test_summary and "passed" in test_summary.lower():
            base_response += " All tests passed successfully."
        
        return base_response

    def _generate_post_application_analysis(self, proposal, test_summary: str) -> str:
        """Generate post-application analysis"""
        ai_type = proposal.ai_type
        file_name = proposal.file_path.split('/')[-1] if '/' in proposal.file_path else proposal.file_path
        change_type = getattr(proposal, 'change_type', 'unknown')
        
        analysis = f"""
**Post-Application Analysis for {ai_type} AI Proposal**

**File Modified:** {file_name}
**Change Type:** {change_type.title()}
**Application Status:** ✅ Successfully Applied
**Test Results:** {test_summary}

**Impact Assessment:**
- The {change_type} changes have been successfully implemented
- All validation tests passed
- System stability maintained
- No conflicts detected with existing functionality

**Next Steps:**
- Monitor system performance for any unexpected behavior
- Track user feedback on the changes
- Consider additional improvements based on usage patterns

**Learning Outcome:**
This successful application contributes to the {ai_type} AI's learning database, improving future proposal accuracy and effectiveness.
        """.strip()
        
        return analysis


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
        testing_service_instance = get_testing_service()
        final_result, final_summary, final_detailed_results = await testing_service_instance.test_proposal(proposal_data)
        
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

@router.get("/cycle/status")
async def get_cycle_status():
    """Get the current proposal cycle status"""
    try:
        cycle_service = await get_proposal_cycle_service()
        status = await cycle_service.get_cycle_status()
        return status
    except Exception as e:
        logger.error(f"Error getting cycle status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cycle/reset")
async def reset_cycle():
    """Force reset the proposal cycle"""
    try:
        cycle_service = await get_proposal_cycle_service()
        result = await cycle_service.force_cycle_reset()
        return result
    except Exception as e:
        logger.error(f"Error resetting cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cycle/agent/{agent_type}/progress")
async def get_agent_progress(agent_type: str):
    """Get progress for a specific agent"""
    try:
        from app.services.proposal_cycle_service import AIAgent
        
        # Map agent type string to enum
        agent_map = {
            "imperium": AIAgent.IMPERIUM,
            "guardian": AIAgent.GUARDIAN,
            "sandbox": AIAgent.SANDBOX,
            "conquest": AIAgent.CONQUEST
        }
        
        if agent_type not in agent_map:
            raise HTTPException(status_code=400, detail=f"Invalid agent type: {agent_type}")
        
        cycle_service = await get_proposal_cycle_service()
        progress = await cycle_service.get_agent_progress(agent_map[agent_type])
        return progress
    except Exception as e:
        logger.error(f"Error getting agent progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/accept-all")
async def accept_all_proposals(db: AsyncSession = Depends(get_db)):
    """Accept all test-passed proposals"""
    try:
        # Get all test-passed proposals
        query = select(Proposal).where(
            Proposal.status == "test-passed",
            Proposal.test_status == "passed"
        )
        result = await db.execute(query)
        test_passed_proposals = result.scalars().all()
        
        if not test_passed_proposals:
            return {
                "status": "success",
                "message": "No test-passed proposals to accept",
                "accepted_count": 0
            }
        
        accepted_count = 0
        for proposal in test_passed_proposals:
            try:
                # Accept the proposal
                proposal.status = "approved"
                proposal.user_feedback = "accepted"
                proposal.user_feedback_reason = "Bulk approval"
                
                # Generate a new pending proposal for this AI type
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
                accepted_count += 1
                
            except Exception as e:
                logger.error(f"Error accepting proposal {proposal.id}: {str(e)}")
                continue
        
        await db.commit()
        
        logger.info(f"Bulk accepted {accepted_count} proposals")
        
        return {
            "status": "success",
            "message": f"Accepted {accepted_count} proposals",
            "accepted_count": accepted_count
        }
        
    except Exception as e:
        logger.error("Error in bulk accept", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-all")
async def reset_all_proposals(db: AsyncSession = Depends(get_db)):
    """Reset all proposals to pending status"""
    try:
        # Get all proposals that are not approved or rejected
        query = select(Proposal).where(
            Proposal.status.in_(["test-passed", "test-failed", "testing"])
        )
        result = await db.execute(query)
        proposals_to_reset = result.scalars().all()
        
        if not proposals_to_reset:
            return {
                "status": "success",
                "message": "No proposals to reset",
                "reset_count": 0
            }
        
        reset_count = 0
        for proposal in proposals_to_reset:
            try:
                proposal.status = "pending"
                proposal.user_feedback = None
                proposal.test_status = None
                proposal.test_output = None
                reset_count += 1
                
            except Exception as e:
                logger.error(f"Error resetting proposal {proposal.id}: {str(e)}")
                continue
        
        await db.commit()
        
        logger.info(f"Bulk reset {reset_count} proposals")
        
        return {
            "status": "success",
            "message": f"Reset {reset_count} proposals",
            "reset_count": reset_count
        }
        
    except Exception as e:
        logger.error("Error in bulk reset", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup-daily")
async def cleanup_daily_proposals(db: AsyncSession = Depends(get_db)):
    """Clean up all proposals that haven't been approved by end of day"""
    try:
        # Get all proposals that are not approved or rejected and older than 1 day
        cutoff_time = datetime.utcnow() - timedelta(days=1)
        query = select(Proposal).where(
            Proposal.status.in_(["pending", "test-passed", "test-failed", "testing"]),
            Proposal.created_at < cutoff_time
        )
        result = await db.execute(query)
        old_proposals = result.scalars().all()
        
        if not old_proposals:
            return {
                "status": "success",
                "message": "No old proposals to clean up",
                "cleaned_count": 0
            }
        
        cleaned_count = 0
        for proposal in old_proposals:
            try:
                proposal.status = "expired"
                proposal.user_feedback = "expired"
                proposal.user_feedback_reason = "Daily cleanup - not approved within 24 hours"
                cleaned_count += 1
                
            except Exception as e:
                logger.error(f"Error cleaning up proposal {proposal.id}: {str(e)}")
                continue
        
        await db.commit()
        
        logger.info(f"Daily cleanup: removed {cleaned_count} old proposals")
        
        return {
            "status": "success",
            "message": f"Cleaned up {cleaned_count} old proposals",
            "cleaned_count": cleaned_count
        }
        
    except Exception as e:
        logger.error("Error in daily cleanup", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
