"""
Oath Papers Router with AI Learning Integration
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from datetime import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.models.sql_models import OathPaper, Proposal
from app.services.ai_learning_service import AILearningService
from app.services.ai_agent_service import AIAgentService
from app.services.enhanced_subject_learning_service import EnhancedSubjectLearningService
from app.models.oath_paper import OathPaperResponse
from sqlalchemy import select

logger = structlog.get_logger()
router = APIRouter()


class EnhancedOathPaperRequest(BaseModel):
    subject: str
    tags: List[str]
    description: Optional[str] = None
    code: Optional[str] = None
    targetAI: Optional[str] = None
    aiWeights: Optional[Dict[str, float]] = None
    learningMode: Optional[str] = "enhanced"
    extractKeywords: Optional[bool] = True
    internetSearch: Optional[bool] = True
    gitIntegration: Optional[bool] = True
    learningInstructions: Optional[Dict[str, bool]] = None
    timestamp: Optional[str] = None


class OathPaperCreateRequest(BaseModel):
    title: str
    subject: Optional[str] = None  # New subject field
    content: str
    category: str = "general"


@router.get("/", response_model=List[OathPaperResponse])
async def list_oath_papers(session: AsyncSession = Depends(get_db)):
    """List all oath papers"""
    try:
        result = await session.execute(select(OathPaper).order_by(OathPaper.created_at.desc()))
        papers = result.scalars().all()
        return [OathPaperResponse(
            id=str(p.id),
            title=p.title,
            subject=p.subject,
            content=p.content,
            category=p.category,
            ai_insights=p.ai_insights,
            learning_value=p.learning_value,
            status=p.status,
            ai_responses=p.ai_responses or {},
            created_at=p.created_at,
            updated_at=p.updated_at
        ) for p in papers]
    except Exception as e:
        logger.error("Error getting oath papers", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_oath_paper(
    request: OathPaperCreateRequest,
    session: AsyncSession = Depends(get_db)
):
    """Create a new oath paper with AI analysis and subject learning"""
    try:
        # Create oath paper
        oath_paper = OathPaper(
            title=request.title,
            subject=request.subject,  # Include subject field
            content=request.content,
            category=request.category,
            created_at=datetime.utcnow()
        )
        session.add(oath_paper)
        await session.commit()
        await session.refresh(oath_paper)
        
        # Enhanced subject learning if subject is provided
        if request.subject:
            try:
                enhanced_learning = EnhancedSubjectLearningService()
                knowledge_base = await enhanced_learning.build_subject_knowledge_base(
                    subject=request.subject,
                    context=request.content
                )
                
                # Update oath paper with enhanced insights
                oath_paper.ai_insights = knowledge_base
                oath_paper.learning_value = knowledge_base.get("learning_value", 0.0)
                oath_paper.status = "learned"
                
                await session.commit()
                await session.refresh(oath_paper)
                
                logger.info(f"Enhanced subject learning completed for {request.subject}")
                
            except Exception as learning_error:
                logger.error(f"Enhanced learning failed", subject=request.subject, error=str(learning_error))
                # Continue with basic analysis even if enhanced learning fails
        
        # Basic AI analysis
        ai_learning = AILearningService()
        analysis = await ai_learning.analyze_oath_paper(oath_paper)
        
        # Create AI proposal for improvements
        if analysis.get("needs_improvement"):
            proposal = Proposal(
                ai_type="imperium",
                file_path=f"oath_papers/{oath_paper.id}",
                code_before=oath_paper.content,
                code_after=analysis.get("improvement_suggestions", ""),
                status="pending",
                created_at=datetime.utcnow()
            )
            session.add(proposal)
            await session.commit()
        
        return {
            "oath_paper": {
                "id": str(oath_paper.id),
                "title": oath_paper.title,
                "subject": oath_paper.subject,
                "content": oath_paper.content,
                "category": oath_paper.category,
                "created_at": oath_paper.created_at.isoformat()
            },
            "ai_analysis": analysis,
            "enhanced_learning": oath_paper.ai_insights if request.subject else None,
            "proposal_created": analysis.get("needs_improvement", False),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error creating oath paper", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhanced")
async def create_enhanced_oath_paper(
    request: EnhancedOathPaperRequest,
    session: AsyncSession = Depends(get_db)
):
    """Create an enhanced oath paper with advanced AI learning"""
    try:
        # Create oath paper with subject
        oath_paper = OathPaper(
            title=request.subject,  # Use subject as title
            subject=request.subject,
            content=request.description or f"Learning about {request.subject}",
            category="enhanced_learning",
            created_at=datetime.utcnow()
        )
        session.add(oath_paper)
        await session.commit()
        await session.refresh(oath_paper)
        
        # Enhanced subject learning
        enhanced_learning = EnhancedSubjectLearningService()
        knowledge_base = await enhanced_learning.build_subject_knowledge_base(
            subject=request.subject,
            context=request.description or ""
        )
        
        # Update oath paper with comprehensive insights
        oath_paper.ai_insights = knowledge_base
        oath_paper.learning_value = knowledge_base.get("learning_value", 0.0)
        oath_paper.status = "learned"
        
        # Process with AI learning service
        ai_learning = AILearningService()
        processing_result = await ai_learning.process_enhanced_oath_paper(
            oath_paper_id=str(oath_paper.id),
            subject=request.subject,
            tags=request.tags,
            description=request.description,
            code=request.code,
            target_ai=request.targetAI,
            ai_weights=request.aiWeights,
            extract_keywords=request.extractKeywords,
            internet_search=request.internetSearch,
            git_integration=request.gitIntegration,
            learning_instructions=request.learningInstructions
        )
        
        # Update with processing results
        oath_paper.ai_responses = processing_result.get("ai_responses", {})
        oath_paper.learning_value = processing_result.get("learning_value", 0.0)
        
        await session.commit()
        await session.refresh(oath_paper)
        
        return {
            "oath_paper": {
                "id": str(oath_paper.id),
                "title": oath_paper.title,
                "subject": oath_paper.subject,
                "content": oath_paper.content,
                "category": oath_paper.category,
                "created_at": oath_paper.created_at.isoformat()
            },
            "enhanced_learning": knowledge_base,
            "ai_processing": processing_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error creating enhanced oath paper", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subject/{subject}")
async def get_oath_papers_by_subject(
    subject: str,
    session: AsyncSession = Depends(get_db)
):
    """Get oath papers by subject"""
    try:
        result = await session.execute(
            select(OathPaper).where(OathPaper.subject == subject).order_by(OathPaper.created_at.desc())
        )
        papers = result.scalars().all()
        
        return [OathPaperResponse(
            id=str(p.id),
            title=p.title,
            subject=p.subject,
            content=p.content,
            category=p.category,
            ai_insights=p.ai_insights,
            learning_value=p.learning_value,
            status=p.status,
            ai_responses=p.ai_responses,
            created_at=p.created_at,
            updated_at=p.updated_at
        ) for p in papers]
        
    except Exception as e:
        logger.error("Error getting oath papers by subject", subject=subject, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research-subject")
async def research_subject(subject: str, context: str = ""):
    """Research a subject using enhanced AI learning"""
    try:
        enhanced_learning = EnhancedSubjectLearningService()
        knowledge_base = await enhanced_learning.build_subject_knowledge_base(subject, context)
        
        return {
            "subject": subject,
            "knowledge_base": knowledge_base,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error researching subject", subject=subject, error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 