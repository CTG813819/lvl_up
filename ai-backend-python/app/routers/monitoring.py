from fastapi import APIRouter
from datetime import datetime
from app.models.sql_models import Proposal, Experiment, GuardianSuggestion
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy import select
from app.database import get_session

router = APIRouter()

@router.get("/")
async def get_monitoring_status(session: AsyncSession = Depends(get_db)):
    try:
        proposal_count = (await session.execute(select(Proposal))).scalars().count()
        experiment_count = (await session.execute(select(Experiment))).scalars().count()
        suggestion_count = (await session.execute(select(GuardianSuggestion))).scalars().count()
        return {
            "status": "success",
            "message": "Monitoring service is active.",
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "proposals": proposal_count,
                "experiments": experiment_count,
                "guardian_suggestions": suggestion_count
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)} 