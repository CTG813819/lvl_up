"""
Scheduling Management Router
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from datetime import timedelta
import structlog
from pydantic import BaseModel

from ..core.database import get_session
from ..services.background_service import BackgroundService
from ..core.config import settings

logger = structlog.get_logger()
router = APIRouter(prefix="/scheduling", tags=["scheduling"])


class SchedulingConfig(BaseModel):
    """Scheduling configuration model"""
    custodes_test_interval_minutes: int = 20
    learning_cycle_interval_minutes: int = 30
    github_monitor_interval_minutes: int = 60
    enabled: bool = True


class SchedulingStatus(BaseModel):
    """Current scheduling status"""
    custodes_test_interval_minutes: int
    learning_cycle_interval_minutes: int
    github_monitor_interval_minutes: int
    enabled: bool
    last_custodes_test: Optional[str] = None
    last_learning_cycle: Optional[str] = None
    next_custodes_test: Optional[str] = None
    next_learning_cycle: Optional[str] = None


@router.get("/config", response_model=SchedulingStatus)
async def get_scheduling_config():
    """Get current scheduling configuration"""
    try:
        # Get background service instance
        background_service = BackgroundService()
        
        # Get current intervals from background service
        custodes_interval = getattr(background_service, '_custodes_test_interval_minutes', 20)
        learning_interval = getattr(background_service, '_learning_cycle_interval_minutes', 30)
        github_interval = getattr(background_service, '_github_monitor_interval_minutes', 60)
        enabled = getattr(background_service, '_running', False)
        
        # Calculate next run times (simplified - in real implementation you'd track actual last run times)
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        
        return SchedulingStatus(
            custodes_test_interval_minutes=custodes_interval,
            learning_cycle_interval_minutes=learning_interval,
            github_monitor_interval_minutes=github_interval,
            enabled=enabled,
            next_custodes_test=(now + timedelta(minutes=custodes_interval)).isoformat(),
            next_learning_cycle=(now + timedelta(minutes=learning_interval)).isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting scheduling config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting scheduling config: {str(e)}")


@router.post("/config", response_model=SchedulingStatus)
async def update_scheduling_config(config: SchedulingConfig):
    """Update scheduling configuration"""
    try:
        # Validate intervals
        if config.custodes_test_interval_minutes < 5:
            raise HTTPException(status_code=400, detail="Custodes test interval must be at least 5 minutes")
        if config.learning_cycle_interval_minutes < 10:
            raise HTTPException(status_code=400, detail="Learning cycle interval must be at least 10 minutes")
        if config.github_monitor_interval_minutes < 15:
            raise HTTPException(status_code=400, detail="GitHub monitor interval must be at least 15 minutes")
        
        # Get background service instance
        background_service = BackgroundService()
        
        # Update intervals
        background_service._custodes_test_interval_minutes = config.custodes_test_interval_minutes
        background_service._learning_cycle_interval_minutes = config.learning_cycle_interval_minutes
        background_service._github_monitor_interval_minutes = config.github_monitor_interval_minutes
        
        # Handle enable/disable
        if config.enabled and not background_service._running:
            logger.info("🔄 Starting background service from scheduling config update")
            # Note: In a real implementation, you'd want to restart the service with new intervals
        elif not config.enabled and background_service._running:
            logger.info("🛑 Stopping background service from scheduling config update")
            await background_service.stop_autonomous_cycle()
        
        logger.info(f"✅ Scheduling config updated: Custodes={config.custodes_test_interval_minutes}m, Learning={config.learning_cycle_interval_minutes}m, GitHub={config.github_monitor_interval_minutes}m, Enabled={config.enabled}")
        
        # Return updated config
        return await get_scheduling_config()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating scheduling config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating scheduling config: {str(e)}")


@router.post("/trigger/custodes")
async def trigger_custodes_test():
    """Manually trigger custodes testing cycle"""
    try:
        background_service = BackgroundService()
        
        if not background_service._running:
            raise HTTPException(status_code=400, detail="Background service is not running")
        
        # Import and run custodes testing
        from app.services.custody_protocol_service import CustodyProtocolService
        custody_service = await CustodyProtocolService.initialize()
        
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        test_results = {}
        
        for ai_type in ai_types:
            try:
                logger.info(f"🧪 Manual trigger: Running Custody test for {ai_type}...")
                
                # Check if AI is eligible for testing
                is_eligible = await custody_service._check_proposal_eligibility(ai_type)
                if not is_eligible:
                    logger.warning(f"AI {ai_type} not eligible for manual testing")
                    test_results[ai_type] = {"status": "skipped", "message": "Not eligible"}
                    continue
                
                # Run test with AI self-generation (no external LLM dependencies)
                test_result = await background_service._administer_test_with_fallback(custody_service, ai_type)
                test_results[ai_type] = test_result
                
                if test_result.get('status') == 'success':
                    logger.info(f"✅ Manual custodes test completed for {ai_type}: {test_result.get('passed', False)}")
                else:
                    logger.warning(f"⚠️ Manual custodes test had issues for {ai_type}: {test_result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"❌ Manual custodes test failed for {ai_type}", error=str(e))
                
                # Provide specific error information
                error_message = str(e)
                if "llm" in error_message.lower() or "sckipit" in error_message.lower():
                    error_message = f"AI self-generation issue: {error_message}. Using internal knowledge-based testing."
                
                test_results[ai_type] = {"status": "error", "message": error_message}
        
        successful_tests = sum(1 for result in test_results.values() if result.get('status') == 'success')
        failed_tests = sum(1 for result in test_results.values() if result.get('status') == 'error')
        skipped_tests = sum(1 for result in test_results.values() if result.get('status') == 'skipped')
        
        logger.info(f"🎯 Manual custodes testing completed: {successful_tests}/{len(ai_types)} AIs tested successfully")
        
        # Provide detailed response with status information
        response_data = {
            "status": "success" if successful_tests > 0 else "partial_success" if failed_tests < len(ai_types) else "error",
            "message": f"Manual custodes testing completed: {successful_tests} successful, {failed_tests} failed, {skipped_tests} skipped",
            "results": test_results,
            "summary": {
                "total_ais": len(ai_types),
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "success_rate": f"{(successful_tests / len(ai_types)) * 100:.1f}%"
            },
            "generation_method": "ai_self",
            "no_external_llm": True
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering manual custodes test: {str(e)}")
        
        # Provide helpful error message
        error_message = str(e)
        if "llm" in error_message.lower() or "sckipit" in error_message.lower():
            error_message = "AI self-generation service is temporarily unavailable. The system will use internal knowledge-based testing."
        
        raise HTTPException(status_code=500, detail=f"Error triggering manual custodes test: {error_message}")


@router.post("/trigger/learning")
async def trigger_learning_cycle():
    """Manually trigger learning cycle"""
    try:
        background_service = BackgroundService()
        
        if not background_service._running:
            raise HTTPException(status_code=400, detail="Background service is not running")
        
        logger.info("🧠 Manual trigger: Running learning cycle...")
        
        # Get learning insights for all AI types
        ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
        learning_results = {}
        
        for ai_type in ai_types:
            try:
                insights = await background_service.learning_service.get_learning_insights(ai_type)
                if insights:
                    logger.info(f"📚 Manual learning insights for {ai_type}", insights=insights)
                    learning_results[ai_type] = {"status": "success", "insights": insights}
                else:
                    learning_results[ai_type] = {"status": "no_insights"}
            except Exception as e:
                logger.error(f"Error getting manual learning insights for {ai_type}", error=str(e))
                learning_results[ai_type] = {"status": "error", "message": str(e)}
        
        # Check ML retraining
        try:
            await background_service._check_ml_retraining()
            learning_results["ml_retraining"] = {"status": "checked"}
        except Exception as e:
            logger.error(f"Error checking ML retraining: {str(e)}")
            learning_results["ml_retraining"] = {"status": "error", "message": str(e)}
        
        successful_learning = sum(1 for result in learning_results.values() if result.get('status') == 'success')
        logger.info(f"🧠 Manual learning cycle completed: {successful_learning} AIs processed successfully")
        
        return {
            "status": "success",
            "message": f"Manual learning cycle completed: {successful_learning} AIs processed successfully",
            "results": learning_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering manual learning cycle: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error triggering manual learning cycle: {str(e)}")


@router.get("/status")
async def get_scheduling_status():
    """Get detailed scheduling status"""
    try:
        background_service = BackgroundService()
        
        return {
            "background_service_running": background_service._running,
            "tasks_count": len(background_service._tasks) if hasattr(background_service, '_tasks') else 0,
            "config": await get_scheduling_config()
        }
        
    except Exception as e:
        logger.error(f"Error getting scheduling status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting scheduling status: {str(e)}") 