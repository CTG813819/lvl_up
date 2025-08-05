from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
import os
import structlog
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.training_data import TrainingData
from app.services.enhanced_subject_learning_service import EnhancedSubjectLearningService
from app.services.enhanced_scenario_service import EnhancedScenarioService

logger = structlog.get_logger()

router = APIRouter(prefix="/api/ai", tags=["training-data"])

class TrainingDataRequest(BaseModel):
    title: str
    subject: Optional[str] = None  # New subject field for AI learning
    description: str
    code: Optional[str] = None
    timestamp: str

class TrainingDataResponse(BaseModel):
    id: int
    title: str
    subject: Optional[str] = None  # New subject field
    description: str
    code: Optional[str] = None
    timestamp: datetime
    status: str

class ScenarioSuggestionRequest(BaseModel):
    user_id: str
    scenario_description: str
    vulnerability_type: str
    difficulty_level: str
    learning_objectives: Optional[str] = None
    requirements: Optional[str] = None
    expected_outcome: Optional[str] = None

class ExpertLearningRequest(BaseModel):
    scenario_name: str
    vulnerability_type: str
    difficulty: str
    success: bool
    techniques_used: List[str]
    learning_insights: Optional[str] = None

@router.post("/upload-training-data")
async def upload_training_data(
    data: TrainingDataRequest,
    db: Session = Depends(get_db)
):
    """
    Upload training data to the AI models with enhanced subject learning.
    This data will be used to improve model performance.
    """
    try:
        # Create new training data record
        training_data = TrainingData(
            title=data.title,
            subject=data.subject,  # Include subject field
            description=data.description,
            code=data.code,
            timestamp=datetime.fromisoformat(data.timestamp.replace('Z', '+00:00')),
            status="pending"
        )
        
        db.add(training_data)
        db.commit()
        db.refresh(training_data)
        
        # Enhanced subject learning if subject is provided
        enhanced_learning_result = None
        if data.subject:
            try:
                enhanced_learning = EnhancedSubjectLearningService()
                knowledge_base = await enhanced_learning.build_subject_knowledge_base(
                    subject=data.subject,
                    context=data.description
                )
                
                # Update training data with enhanced insights
                training_data.processing_notes = json.dumps({
                    "enhanced_learning": knowledge_base,
                    "learning_value": knowledge_base.get("learning_value", 0.0),
                    "status": "enhanced_learning_completed"
                })
                training_data.status = "processed"
                training_data.processed_at = datetime.utcnow()
                
                db.commit()
                db.refresh(training_data)
                
                enhanced_learning_result = knowledge_base
                logger.info(f"Enhanced subject learning completed for {data.subject}")
                
            except Exception as learning_error:
                logger.error(f"Enhanced learning failed", subject=data.subject, error=str(learning_error))
                print(f"[ERROR] Enhanced learning failed for subject {data.subject}: {learning_error}")
                # Continue with basic processing even if enhanced learning fails
        
        # Log the upload for monitoring
        print(f"[TRAINING_DATA] New upload: {data.title} - {len(data.description)} chars")
        if data.subject:
            print(f"[TRAINING_DATA] Subject: {data.subject}")
        if data.code:
            print(f"[TRAINING_DATA] Code included: {len(data.code)} chars")
        
        return {
            "message": "Training data uploaded successfully",
            "id": training_data.id,
            "status": training_data.status,
            "enhanced_learning": enhanced_learning_result,
            "subject_researched": bool(data.subject)
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
    subject: Optional[str] = None,  # Filter by subject
    db: Session = Depends(get_db)
):
    """
    Get uploaded training data (for admin review).
    Can filter by subject if provided.
    """
    try:
        query = db.query(TrainingData)
        
        # Filter by subject if provided
        if subject:
            query = query.filter(TrainingData.subject == subject)
        
        training_data = query\
            .order_by(TrainingData.timestamp.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        return {
            "data": [
                {
                    "id": item.id,
                    "title": item.title,
                    "subject": item.subject,
                    "description": item.description,
                    "code": item.code,
                    "timestamp": item.timestamp.isoformat(),
                    "status": item.status,
                    "processing_notes": item.processing_notes
                }
                for item in training_data
            ],
            "total": len(training_data),
            "filtered_by_subject": subject
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to get training data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get training data: {str(e)}"
        )

@router.get("/training-data/subjects")
async def get_training_data_subjects(db: Session = Depends(get_db)):
    """
    Get all unique subjects from training data.
    """
    try:
        subjects = db.query(TrainingData.subject)\
            .filter(TrainingData.subject.isnot(None))\
            .distinct()\
            .all()
        
        return {
            "subjects": [subject[0] for subject in subjects if subject[0]],
            "total_subjects": len([s for s in subjects if s[0]])
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to get training data subjects: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get training data subjects: {str(e)}"
        )

@router.post("/research-subject")
async def research_subject(subject: str, context: str = ""):
    """
    Research a subject using enhanced AI learning for Book of Lorgar.
    """
    try:
        enhanced_learning = EnhancedSubjectLearningService()
        knowledge_base = await enhanced_learning.build_subject_knowledge_base(subject, context)
        
        return {
            "subject": subject,
            "knowledge_base": knowledge_base,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to research subject: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to research subject: {str(e)}"
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

@router.post("/scenario-suggestion")
async def add_scenario_suggestion(request: ScenarioSuggestionRequest):
    """
    Add a new scenario suggestion from user for AI to build and deploy.
    The system will learn from this suggestion and provide feedback.
    """
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        result = await enhanced_scenario_service.add_scenario_suggestion(
            user_id=request.user_id,
            scenario_description=request.scenario_description,
            vulnerability_type=request.vulnerability_type,
            difficulty_level=request.difficulty_level,
            learning_objectives=request.learning_objectives,
            requirements=request.requirements,
            expected_outcome=request.expected_outcome
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "message": "Scenario suggestion added successfully",
            "suggestion_id": result["suggestion_id"],
            "ai_feedback": result["ai_feedback"],
            "status": result["status"]
        }
        
    except Exception as e:
        logger.error(f"Failed to add scenario suggestion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add scenario suggestion: {str(e)}"
        )

@router.get("/scenario-suggestions")
async def get_scenario_suggestions(
    user_id: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Get scenario suggestions with optional filtering by user_id and status.
    """
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        suggestions = await enhanced_scenario_service.get_scenario_suggestions(
            user_id=user_id,
            status=status
        )
        
        return {
            "suggestions": suggestions,
            "total": len(suggestions),
            "filtered_by_user": user_id is not None,
            "filtered_by_status": status is not None
        }
        
    except Exception as e:
        logger.error(f"Failed to get scenario suggestions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scenario suggestions: {str(e)}"
        )

@router.post("/expert-learning")
async def learn_from_expert_example(request: ExpertLearningRequest):
    """
    Learn from expert example and update AI knowledge base.
    This helps the AI improve its scenario generation and difficulty assessment.
    """
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        result = await enhanced_scenario_service.learn_from_expert_example(
            scenario_name=request.scenario_name,
            vulnerability_type=request.vulnerability_type,
            difficulty=request.difficulty,
            success=request.success,
            techniques_used=request.techniques_used,
            learning_insights=request.learning_insights
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "message": "Expert example learned successfully",
            "example_id": result["example_id"],
            "learning_value": result["learning_value"]
        }
        
    except Exception as e:
        logger.error(f"Failed to learn from expert example: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to learn from expert example: {str(e)}"
        )

@router.get("/expert-examples")
async def get_expert_examples(
    vulnerability_type: Optional[str] = None,
    difficulty: Optional[str] = None
):
    """
    Get expert examples for learning and reference.
    Can filter by vulnerability type and difficulty level.
    """
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        examples = await enhanced_scenario_service.get_expert_examples(
            vulnerability_type=vulnerability_type,
            difficulty=difficulty
        )
        
        return {
            "examples": examples,
            "total": len(examples),
            "filtered_by_vulnerability": vulnerability_type is not None,
            "filtered_by_difficulty": difficulty is not None
        }
        
    except Exception as e:
        logger.error(f"Failed to get expert examples: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get expert examples: {str(e)}"
        )

@router.post("/build-suggested-scenario/{suggestion_id}")
async def build_suggested_scenario(suggestion_id: int, user_id: str = "default"):
    """
    Build and deploy a scenario based on a user suggestion.
    This creates a live environment for the AI to attack.
    """
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        scenario = await enhanced_scenario_service.build_scenario_from_suggestion(suggestion_id, user_id)
        
        if "error" in scenario:
            raise HTTPException(status_code=404, detail=scenario["error"])
        
        return {
            "message": "Suggested scenario built successfully",
            "scenario": scenario,
            "suggestion_id": suggestion_id
        }
        
    except Exception as e:
        logger.error(f"Failed to build suggested scenario: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to build suggested scenario: {str(e)}"
        )

@router.post("/build-expert-scenario/{example_id}")
async def build_expert_scenario(example_id: int, user_id: str = "default"):
    """
    Build and deploy a scenario based on an expert example.
    This creates a live environment for the AI to attack using expert techniques.
    """
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        scenario = await enhanced_scenario_service.build_scenario_from_expert_example(example_id, user_id)
        
        if "error" in scenario:
            raise HTTPException(status_code=404, detail=scenario["error"])
        
        return {
            "message": "Expert scenario built successfully",
            "scenario": scenario,
            "example_id": example_id
        }
        
    except Exception as e:
        logger.error(f"Failed to build expert scenario: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to build expert scenario: {str(e)}"
        ) 