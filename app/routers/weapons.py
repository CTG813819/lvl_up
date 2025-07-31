from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.sql_models import Weapon
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

router = APIRouter()

class WeaponCreateRequest(BaseModel):
    user_id: str
    name: str
    code: str
    description: str = ""

class WeaponUseRequest(BaseModel):
    user_id: str
    weapon_id: str
    target: str

@router.post("/weapons/save")
async def save_weapon(request: WeaponCreateRequest, db: AsyncSession = Depends(get_db)):
    weapon = Weapon(
        id=uuid.uuid4(),
        user_id=request.user_id,
        name=request.name,
        code=request.code,
        description=request.description,
        created_at=datetime.utcnow()
    )
    db.add(weapon)
    await db.commit()
    await db.refresh(weapon)
    return {"status": "success", "weapon_id": str(weapon.id)}

@router.get("/weapons/list")
async def list_weapons(user_id: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(Weapon).where(Weapon.user_id == user_id).order_by(Weapon.created_at.desc()))
    weapons = result.scalars().all()
    return {
        "status": "success",
        "weapons": [
            {
                "id": str(w.id),
                "name": w.name,
                "code": w.code,
                "description": w.description,
                "created_at": w.created_at.isoformat()
            } for w in weapons
        ]
    }

@router.post("/weapons/use")
async def use_weapon(request: WeaponUseRequest, db: AsyncSession = Depends(get_db)):
    # For now, just return a stub response
    # In a real system, you would execute the code against the target
    return {"status": "success", "message": f"Weapon {request.weapon_id} would be used on {request.target}"} 