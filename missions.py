"""
Mission router for mission management and Guardian AI health checks
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
import json

from app.core.database import get_db
from app.models.sql_models import Mission, MissionSubtask, GuardianSuggestion
from app.services.guardian_ai_service import GuardianAIService

logger = structlog.get_logger()
router = APIRouter()


@router.post("/sync")
async def sync_missions(
    missions_data: List[Dict[str, Any]],
    session: AsyncSession = Depends(get_db)
):
    """Sync missions from frontend to backend for Guardian AI health checks"""
    try:
        logger.info(f"Syncing {len(missions_data)} missions from frontend")
        
        synced_count = 0
        updated_count = 0
        
        for mission_data in missions_data:
            # Check if mission already exists
            if mission_data.get('id'):
                result = await session.execute(
                    select(Mission).where(Mission.id == mission_data['id'])
                )
                existing_mission = result.scalar_one_or_none()
                
                if existing_mission:
                    # Update existing mission
                    for key, value in mission_data.items():
                        if hasattr(existing_mission, key) and key != 'id':
                            setattr(existing_mission, key, value)
                    existing_mission.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new mission
                    mission = Mission(**mission_data)
                    session.add(mission)
                    synced_count += 1
            else:
                # Create new mission without ID
                mission = Mission(**mission_data)
                session.add(mission)
                synced_count += 1
            
            # Handle subtasks if present
            if 'subtasks' in mission_data and mission_data['subtasks']:
                mission_id = mission_data.get('id') or mission.id
                
                # Delete existing subtasks for this mission
                await session.execute(
                    select(MissionSubtask).where(MissionSubtask.mission_id == mission_id)
                )
                
                # Create new subtasks
                for subtask_data in mission_data['subtasks']:
                    subtask_data['mission_id'] = mission_id
                    subtask = MissionSubtask(**subtask_data)
                    session.add(subtask)
        
        await session.commit()
        
        logger.info(f"Mission sync completed: {synced_count} new, {updated_count} updated")
        
        return {
            "status": "success",
            "data": {
                "synced_count": synced_count,
                "updated_count": updated_count,
                "total_processed": len(missions_data)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error syncing missions", error=str(e))
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_missions(
    session: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
    completed: Optional[bool] = None
):
    """Get missions with optional filtering"""
    try:
        query = select(Mission)
        
        if completed is not None:
            query = query.where(Mission.is_completed == completed)
        
        query = query.order_by(Mission.created_at.desc()).offset(offset).limit(limit)
        
        result = await session.execute(query)
        missions = result.scalars().all()
        
        return {
            "status": "success",
            "data": {
                "missions": [
                    {
                        "id": str(m.id),
                        "mission_id": m.mission_id,
                        "title": m.title,
                        "description": m.description,
                        "mission_type": m.mission_type,
                        "is_completed": m.is_completed,
                        "has_failed": m.has_failed,
                        "mastery_id": m.mastery_id,
                        "value": m.value,
                        "is_counter_based": m.is_counter_based,
                        "current_count": m.current_count,
                        "target_count": m.target_count,
                        "mastery_value": m.mastery_value,
                        "linked_mastery_id": m.linked_mastery_id,
                        "notification_id": m.notification_id,
                        "scheduled_notification_id": m.scheduled_notification_id,
                        "image_url": m.image_url,
                        "created_at": m.created_at.isoformat() if m.created_at else None,
                        "last_completed": m.last_completed.isoformat() if m.last_completed else None,
                        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
                        "subtasks_data": m.subtasks_data,
                        "subtask_mastery_values": m.subtask_mastery_values,
                        "bolt_color": m.bolt_color,
                        "timelapse_color": m.timelapse_color,
                        "health_status": m.health_status,
                        "data_integrity_score": m.data_integrity_score
                    }
                    for m in missions
                ],
                "total": len(missions),
                "limit": limit,
                "offset": offset
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting missions", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_mission_statistics(session: AsyncSession = Depends(get_db)):
    """Get mission statistics"""
    try:
        # Count total missions
        total_result = await session.execute(select(func.count(Mission.id)))
        total_missions = total_result.scalar()
        
        # Count completed missions
        completed_result = await session.execute(
            select(func.count(Mission.id)).where(Mission.is_completed == True)
        )
        completed_missions = completed_result.scalar()
        
        # Count failed missions
        failed_result = await session.execute(
            select(func.count(Mission.id)).where(Mission.has_failed == True)
        )
        failed_missions = failed_result.scalar()
        
        # Count counter-based missions
        counter_result = await session.execute(
            select(func.count(Mission.id)).where(Mission.is_counter_based == True)
        )
        counter_missions = counter_result.scalar()
        
        # Count missions by type
        type_result = await session.execute(
            select(Mission.mission_type, func.count(Mission.id))
            .group_by(Mission.mission_type)
        )
        missions_by_type = dict(type_result.all())
        
        # Count subtasks
        subtasks_result = await session.execute(select(func.count(MissionSubtask.id)))
        total_subtasks = subtasks_result.scalar()
        
        return {
            "status": "success",
            "data": {
                "total_missions": total_missions,
                "completed_missions": completed_missions,
                "failed_missions": failed_missions,
                "counter_missions": counter_missions,
                "missions_by_type": missions_by_type,
                "total_subtasks": total_subtasks,
                "completion_rate": (completed_missions / total_missions * 100) if total_missions > 0 else 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting mission statistics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health-check")
async def run_mission_health_check(session: AsyncSession = Depends(get_db)):
    """Run health check specifically on missions"""
    try:
        guardian_service = GuardianAIService()
        results = await guardian_service._check_mission_health(session)
        
        return {
            "status": "success",
            "data": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error running mission health check", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{mission_id}")
async def get_mission(
    mission_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get a specific mission by ID"""
    try:
        result = await session.execute(
            select(Mission).where(Mission.id == mission_id)
        )
        mission = result.scalar_one_or_none()
        
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        # Get subtasks for this mission
        subtasks_result = await session.execute(
            select(MissionSubtask).where(MissionSubtask.mission_id == mission_id)
        )
        subtasks = subtasks_result.scalars().all()
        
        return {
            "status": "success",
            "data": {
                "mission": {
                    "id": str(mission.id),
                    "mission_id": mission.mission_id,
                    "title": mission.title,
                    "description": mission.description,
                    "mission_type": mission.mission_type,
                    "is_completed": mission.is_completed,
                    "has_failed": mission.has_failed,
                    "mastery_id": mission.mastery_id,
                    "value": mission.value,
                    "is_counter_based": mission.is_counter_based,
                    "current_count": mission.current_count,
                    "target_count": mission.target_count,
                    "mastery_value": mission.mastery_value,
                    "linked_mastery_id": mission.linked_mastery_id,
                    "notification_id": mission.notification_id,
                    "scheduled_notification_id": mission.scheduled_notification_id,
                    "image_url": mission.image_url,
                    "created_at": mission.created_at.isoformat() if mission.created_at else None,
                    "last_completed": mission.last_completed.isoformat() if mission.last_completed else None,
                    "updated_at": mission.updated_at.isoformat() if mission.updated_at else None,
                    "subtasks_data": mission.subtasks_data,
                    "subtask_mastery_values": mission.subtask_mastery_values,
                    "bolt_color": mission.bolt_color,
                    "timelapse_color": mission.timelapse_color,
                    "health_status": mission.health_status,
                    "data_integrity_score": mission.data_integrity_score
                },
                "subtasks": [
                    {
                        "id": str(s.id),
                        "name": s.name,
                        "required_completions": s.required_completions,
                        "current_completions": s.current_completions,
                        "linked_mastery_id": s.linked_mastery_id,
                        "mastery_value": s.mastery_value,
                        "is_counter_based": s.is_counter_based,
                        "current_count": s.current_count,
                        "bolt_color": s.bolt_color,
                        "created_at": s.created_at.isoformat() if s.created_at else None,
                        "updated_at": s.updated_at.isoformat() if s.updated_at else None
                    }
                    for s in subtasks
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting mission", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 