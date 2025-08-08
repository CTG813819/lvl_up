from fastapi import APIRouter
from app.services.enhanced_ai_coordinator import EnhancedAICoordinator
from app.services.background_service import BackgroundService

router = APIRouter()

scheduler_coordinator = EnhancedAICoordinator()

background_service = BackgroundService()

@router.post("/scheduler/interval")
async def update_scheduler_interval(data: dict):
    """Update the scheduler interval for all backend scheduled tasks (in minutes)."""
    try:
        interval = int(data.get('interval_minutes', 90))
        await scheduler_coordinator.start_cross_ai_schedulers(interval_minutes=interval)
        return {"status": "success", "interval_minutes": interval}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/scheduler/all_intervals")
async def get_all_scheduler_intervals():
    """Get all backend schedule intervals (in minutes)."""
    return {
        "agent_scheduler": background_service.agent_scheduler_interval,
        "github_monitor": background_service.github_monitor_interval,
        "learning_cycle": background_service.learning_cycle_interval,
        "custody_testing": background_service.custody_testing_interval
    }

@router.post("/scheduler/all_intervals")
async def set_all_scheduler_intervals(data: dict):
    """Set all backend schedule intervals (in minutes). Applies within the next schedule."""
    try:
        if "agent_scheduler" in data:
            background_service.agent_scheduler_interval = int(data["agent_scheduler"])
        if "github_monitor" in data:
            background_service.github_monitor_interval = int(data["github_monitor"])
        if "learning_cycle" in data:
            background_service.learning_cycle_interval = int(data["learning_cycle"])
        if "custody_testing" in data:
            background_service.custody_testing_interval = int(data["custody_testing"])
        await background_service.reschedule_all()
        return {"status": "success", "intervals": await get_all_scheduler_intervals()}
    except Exception as e:
        return {"status": "error", "message": str(e)} 