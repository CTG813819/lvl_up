from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.jarvis_service import jarvis_service

router = APIRouter(prefix="/api/jarvis", tags=["Jarvis"])


class JarvisSignals(BaseModel):
    horus: Optional[Dict[str, Any]] = None
    berserk: Optional[Dict[str, Any]] = None
    chaos: Optional[Dict[str, Any]] = None
    adversarial: Optional[Dict[str, Any]] = None
    internet_digest: Optional[str] = None


@router.get("/status")
async def get_jarvis_status() -> Dict[str, Any]:
    try:
        return {"status": "success", "jarvis": jarvis_service.get_status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learn")
async def trigger_jarvis_learning() -> Dict[str, Any]:
    try:
        result = jarvis_service.trigger_learning_cycle()
        return {"status": "success", "jarvis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/integrate")
async def integrate_jarvis(signals: JarvisSignals) -> Dict[str, Any]:
    try:
        result = jarvis_service.integrate_signals(signals.model_dump())
        return {"status": "success", "jarvis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
