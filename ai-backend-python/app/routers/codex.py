from fastapi import APIRouter, HTTPException
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_session
from app.models.sql_models import Proposal
from app.services.ai_learning_service import AILearningService
import structlog

router = APIRouter()
logger = structlog.get_logger()

# Helper to convert day index to Roman numerals
def int_to_roman(input):
    if not isinstance(input, int):
        raise TypeError("expected integer, got %s" % type(input))
    if not 0 < input < 4000:
        raise ValueError("Argument must be between 1 and 3999")
    ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    nums = ("M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I")
    result = []
    for i in range(len(ints)):
        count = int(input / ints[i])
        result.append(nums[i] * count)
        input -= ints[i] * count
    return ''.join(result)

@router.get("/", summary="Codex: AI Learning Chapters", tags=["Codex"])
async def get_codex(db: AsyncSession = None):
    """
    Returns a chronological list of AI learning cycles, proposals, and feedback, grouped by day (chapter),
    with Roman numerals, timestamps, and summaries. Suitable for Codex UI.
    """
    if db is None:
        db = await get_session().__aenter__()
    try:
        # Get all proposals, ordered by creation date
        proposals = (await db.execute(select(Proposal).order_by(Proposal.created_at.asc()))).scalars().all()
        if not proposals:
            return {"chapters": []}
        # Group by day
        chapters = {}
        for p in proposals:
            day = p.created_at.date().isoformat()
            if day not in chapters:
                chapters[day] = []
            chapters[day].append(p)
        # Format chapters
        codex = []
        for idx, (day, props) in enumerate(sorted(chapters.items()), 1):
            codex.append({
                "chapter": int_to_roman(idx),
                "date": day,
                "timestamp": props[0].created_at.isoformat(),
                "proposals": [
                    {
                        "id": str(p.id),
                        "ai_type": p.ai_type,
                        "file_path": p.file_path,
                        "status": p.status,
                        "improvement_type": getattr(p, 'improvement_type', None),
                        "confidence": getattr(p, 'confidence', 0.5),
                        "user_feedback": p.user_feedback,
                        "test_status": p.test_status,
                        "created_at": p.created_at.isoformat(),
                        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                        "ai_reasoning": getattr(p, 'ai_reasoning', None),
                        "user_feedback_reason": getattr(p, 'user_feedback_reason', None)
                    } for p in props
                ],
                "summary": f"{len(props)} proposals, {sum(1 for p in props if p.status == 'accepted')} accepted, {sum(1 for p in props if p.status == 'rejected')} rejected"
            })
        return {"chapters": codex}
    except Exception as e:
        logger.error("Error generating codex", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate codex") 