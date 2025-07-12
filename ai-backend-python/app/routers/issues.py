from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.sql_models import ErrorLearning, GuardianSuggestion

router = APIRouter()

@router.get("/")
async def get_issues_status(session: AsyncSession = Depends(get_db)):
    """Get issues service status from live data"""
    try:
        # Get total error learnings
        error_learnings_result = await session.execute(select(ErrorLearning))
        total_errors = len(error_learnings_result.scalars().all())
        
        # Get total guardian suggestions (potential issues)
        suggestions_result = await session.execute(select(GuardianSuggestion))
        total_suggestions = len(suggestions_result.scalars().all())
        
        # Get critical issues
        critical_errors_result = await session.execute(
            select(ErrorLearning).where(ErrorLearning.severity == "critical")
        )
        critical_errors = len(critical_errors_result.scalars().all())
        
        return {
            "status": "success",
            "message": "Issues service is active.",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "total_errors": total_errors,
                "total_suggestions": total_suggestions,
                "critical_issues": critical_errors,
                "system_health": "healthy" if critical_errors == 0 else "warning"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting issues status: {str(e)}",
            "timestamp": datetime.now().isoformat()
        } 