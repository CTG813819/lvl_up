"""
Oath Papers Router with AI Learning Integration
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from datetime import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_session
from app.models.sql_models import OathPaper, Proposal
from app.services.ai_learning_service import AILearningService
from app.services.ai_agent_service import AIAgentService
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


@router.get("/", response_model=List[OathPaperResponse])
async def list_oath_papers():
    """List all oath papers"""
    try:
        session = get_session()
        async with session as s:
            result = await s.execute(select(OathPaper).order_by(OathPaper.created_at.desc()))
            papers = result.scalars().all()
            return [OathPaperResponse(
                id=str(p.id),
                title=p.title,
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
        logger.error("Error getting oath papers", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_oath_paper(
    title: str,
    content: str,
    category: str = "general",
    session: AsyncSession = Depends(get_session)
):
    """Create a new oath paper with AI analysis"""
    try:
        # Create oath paper
        oath_paper = OathPaper(
            title=title,
            content=content,
            category=category,
            created_at=datetime.utcnow()
        )
        session.add(oath_paper)
        await session.commit()
        await session.refresh(oath_paper)
        
        # Analyze with AI learning
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
                "content": oath_paper.content,
                "category": oath_paper.category,
                "created_at": oath_paper.created_at.isoformat()
            },
            "ai_analysis": analysis,
            "proposal_created": analysis.get("needs_improvement", False),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error creating oath paper", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhanced-learning")
async def enhanced_oath_paper_learning(request: EnhancedOathPaperRequest):
    """Enhanced oath paper learning with keyword extraction, internet search, and git integration"""
    try:
        logger.info("Processing enhanced oath paper", subject=request.subject, target_ai=request.targetAI)
        
        # Create oath paper record
        session = get_session()
        async with session as s:
            oath_paper = OathPaper(
                title=request.subject,
                content=request.description or "",
                category="enhanced",
                created_at=datetime.utcnow(),
                status="processing"
            )
            s.add(oath_paper)
            await s.commit()
            await s.refresh(oath_paper)
            
            # Initialize AI learning service
            ai_learning = AILearningService()
            
            # Process with enhanced learning
            learning_result = await ai_learning.process_enhanced_oath_paper(
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
            
            # Update oath paper status
            oath_paper.status = "completed"
            oath_paper.ai_insights = learning_result.get("ai_insights", {})
            oath_paper.learning_value = learning_result.get("learning_value", 0.0)
            oath_paper.ai_responses = learning_result.get("ai_responses", {})
            await s.commit()
            
            # Create proposals for each AI if specified
            proposals_created = []
            if request.targetAI and request.targetAI != "All AIs":
                # Create proposal for specific AI
                proposal = Proposal(
                    ai_type=request.targetAI.lower(),
                    file_path=f"oath_papers/{oath_paper.id}",
                    code_before=request.description or "",
                    code_after=learning_result.get("improvement_suggestions", ""),
                    status="pending",
                    created_at=datetime.utcnow()
                )
                s.add(proposal)
                proposals_created.append(str(proposal.id))
            else:
                # Create proposals for all AIs
                ai_types = ["imperium", "guardian", "sandbox", "conquest"]
                for ai_type in ai_types:
                    proposal = Proposal(
                        ai_type=ai_type,
                        file_path=f"oath_papers/{oath_paper.id}",
                        code_before=request.description or "",
                        code_after=learning_result.get("improvement_suggestions", ""),
                        status="pending",
                        created_at=datetime.utcnow()
                    )
                    s.add(proposal)
                    proposals_created.append(str(proposal.id))
            
            await s.commit()
            
            return {
                "status": "success",
                "oath_paper_id": str(oath_paper.id),
                "learning_result": learning_result,
                "proposals_created": proposals_created,
                "processing_time": learning_result.get("processing_time", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error("Error processing enhanced oath paper", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-insights")
async def get_oath_papers_ai_insights(session: AsyncSession = Depends(get_session)):
    """Get AI insights for all oath papers"""
    try:
        ai_learning = AILearningService()
        insights = await ai_learning.get_oath_papers_insights()
        
        return {
            "insights": insights,
            "learning_progress": await ai_learning.get_learning_progress(),
            "recommendations": await ai_learning.get_oath_papers_recommendations(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting AI insights", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learn/{paper_id}")
async def trigger_learning(paper_id: str):
    session = get_session()
    async with session as s:
        paper = await s.get(OathPaper, paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Oath Paper not found")
        # Simulate learning for all AIs
        ai_names = ["Imperium", "Guardian", "Sandbox", "Conquest"]
        ai_responses = {}
        for ai in ai_names:
            # Simulate learning result
            ai_responses[ai] = "learned"
        paper.status = "learned"
        paper.ai_responses = ai_responses
        await s.commit()
        return {"status": "success", "ai_responses": ai_responses}


@router.get("/categories")
async def get_oath_paper_categories(session: AsyncSession = Depends(get_session)):
    """Get oath paper categories with AI analysis"""
    try:
        from sqlalchemy import select, func
        result = await session.execute(
            select(OathPaper.category, func.count(OathPaper.id))
            .group_by(OathPaper.category)
        )
        categories = result.all()
        
        ai_learning = AILearningService()
        category_insights = await ai_learning.analyze_oath_paper_categories()
        
        return {
            "categories": [
                {
                    "category": cat,
                    "count": count,
                    "ai_insights": category_insights.get(cat, {})
                }
                for cat, count in categories
            ],
            "total_categories": len(categories),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting categories", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 