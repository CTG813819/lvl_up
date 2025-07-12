from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.sql_models import Proposal
from app.services.ai_learning_service import AILearningService
import structlog
import os

CODEX_LOG_PATH = os.path.join(os.path.dirname(__file__), '../../codex_log.json')

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
async def get_codex(db: AsyncSession = Depends(get_db)):
    """
    Returns a chronological list of AI learning cycles, proposals, and feedback, grouped by day (chapter),
    with Roman numerals, timestamps, and summaries. Suitable for Codex UI.
    Now also includes custom logs from codex_log.json.
    """
    import json
    try:
        # Get all proposals, ordered by creation date
        proposals = (await db.execute(select(Proposal).order_by(Proposal.created_at.asc()))).scalars().all()
        # Group proposals by day
        chapters = {}
        for p in proposals:
            day = p.created_at.date().isoformat()
            if day not in chapters:
                chapters[day] = []
            chapters[day].append({
                "type": "proposal",
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
            })
        # Load custom logs from codex_log.json
        log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../codex_log.json'))
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        # Group logs by day
        for log in logs:
            ts = log.get('timestamp')
            if not ts:
                continue
            try:
                day = ts[:10]  # YYYY-MM-DD
            except Exception:
                continue
            if day not in chapters:
                chapters[day] = []
            log_entry = dict(log)
            log_entry['type'] = log.get('type', 'log')
            chapters[day].append(log_entry)
        # Format chapters, sorted by day
        codex = []
        for idx, (day, events) in enumerate(sorted(chapters.items()), 1):
            # Sort events by timestamp
            events_sorted = sorted(events, key=lambda e: e.get('created_at', e.get('timestamp', '')))
            # Count proposals
            n_proposals = sum(1 for e in events_sorted if e.get('type') == 'proposal')
            n_accepted = sum(1 for e in events_sorted if e.get('type') == 'proposal' and e.get('status') == 'accepted')
            n_rejected = sum(1 for e in events_sorted if e.get('type') == 'proposal' and e.get('status') == 'rejected')
            codex.append({
                "chapter": int_to_roman(idx),
                "date": day,
                "timestamp": events_sorted[0].get('created_at', events_sorted[0].get('timestamp', '')),
                "proposals": events_sorted,
                "summary": f"{n_proposals} proposals, {n_accepted} accepted, {n_rejected} rejected, {len(events_sorted) - n_proposals} logs"
            })
        return {"chapters": codex}
    except Exception as e:
        logger.error("Error generating codex", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate codex")

@router.post("/log", summary="Log a new Codex event", tags=["Codex"])
async def log_codex_event(event: dict):
    """
    Log a new Codex event (e.g., Imperium audit, feedback) to the Codex log file.
    """
    import json
    try:
        # Load existing log
        if os.path.exists(CODEX_LOG_PATH):
            with open(CODEX_LOG_PATH, 'r', encoding='utf-8') as f:
                log = json.load(f)
        else:
            log = []
        # Append new event
        event['timestamp'] = datetime.utcnow().isoformat()
        log.append(event)
        # Save log
        with open(CODEX_LOG_PATH, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2)
        return {"status": "success", "message": "Event logged"}
    except Exception as e:
        logger.error("Error logging Codex event", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to log Codex event") 