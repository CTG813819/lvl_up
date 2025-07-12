from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json
import os
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.training_data import TrainingData

router = APIRouter(prefix="/api/ai", tags=["training-data"])

class TrainingDataRequest(BaseModel):
    title: str
    description: str
    code: Optional[str] = None
    timestamp: str

class TrainingDataResponse(BaseModel):
    id: int
    title: str
    description: str
    code: Optional[str] = None
    timestamp: datetime
    status: str

@router.post("/upload-training-data")
async def upload_training_data(
    data: TrainingDataRequest,
    db: Session = Depends(get_db)
):
    """
    Upload training data to the AI models.
    This data will be used to improve model performance.
    """
    try:
        # Create new training data record
        training_data = TrainingData(
            title=data.title,
            description=data.description,
            code=data.code,
            timestamp=datetime.fromisoformat(data.timestamp.replace('Z', '+00:00')),
            status="pending"
        )
        
        db.add(training_data)
        db.commit()
        db.refresh(training_data)
        
        # Log the upload for monitoring
        print(f"[TRAINING_DATA] New upload: {data.title} - {len(data.description)} chars")
        if data.code:
            print(f"[TRAINING_DATA] Code included: {len(data.code)} chars")
        
        # TODO: Trigger model retraining process
        # This could be a background task that:
        # 1. Exports all training data
        # 2. Retrains the models
        # 3. Updates the model artifacts
        
        return {
            "message": "Training data uploaded successfully",
            "id": training_data.id,
            "status": "pending_processing"
        }
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to upload training data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload training data: {str(e)}"
        )

@router.get("/training-data")
async def get_training_data(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get uploaded training data (for admin review).
    """
    try:
        training_data = db.query(TrainingData)\
            .order_by(TrainingData.timestamp.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        return {
            "data": [
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "code": item.code,
                    "timestamp": item.timestamp.isoformat(),
                    "status": item.status
                }
                for item in training_data
            ],
            "total": len(training_data)
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to get training data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get training data: {str(e)}"
        )

@router.delete("/training-data/{data_id}")
async def delete_training_data(
    data_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete training data (admin only).
    """
    try:
        training_data = db.query(TrainingData).filter(TrainingData.id == data_id).first()
        
        if not training_data:
            raise HTTPException(status_code=404, detail="Training data not found")
        
        db.delete(training_data)
        db.commit()
        
        return {"message": "Training data deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to delete training data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete training data: {str(e)}"
        )

@router.post("/retrain-models")
async def trigger_model_retraining():
    """
    Trigger model retraining with all available training data.
    This is a manual trigger for admin use.
    """
    try:
        # TODO: Implement model retraining logic
        # This should:
        # 1. Export all training data from database
        # 2. Combine with existing training data
        # 3. Retrain the ML models
        # 4. Save new model artifacts
        # 5. Update model status
        
        print("[TRAINING] Manual retraining triggered")
        
        return {
            "message": "Model retraining triggered",
            "status": "processing",
            "estimated_time": "5-10 minutes"
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to trigger model retraining: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger model retraining: {str(e)}"
        ) 