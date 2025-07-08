from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/")
async def get_monitoring_status():
    return {
        "status": "success",
        "message": "Monitoring service is active.",
        "timestamp": datetime.now().isoformat()
    } 