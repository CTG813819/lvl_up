from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/")
async def get_issues_status():
    return {
        "status": "success",
        "message": "Issues service is active.",
        "timestamp": datetime.now().isoformat()
    } 