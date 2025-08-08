"""
Test Enhanced Router - Simple test to isolate router inclusion issue
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import structlog
from datetime import datetime

logger = structlog.get_logger()
router = APIRouter(prefix="/api/test-enhanced", tags=["Test Enhanced"])

class TestRequest(BaseModel):
    message: str

@router.get("/status")
async def get_test_status():
    """Get test status"""
    return {
        "status": "success",
        "message": "Test enhanced router is working",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/test")
async def test_endpoint(request: TestRequest):
    """Test endpoint"""
    return {
        "status": "success",
        "message": f"Received: {request.message}",
        "timestamp": datetime.now().isoformat()
    } 