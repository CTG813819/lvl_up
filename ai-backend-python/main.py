"""
Main FastAPI application for AI Backend with scikit-learn integration
"""

import os
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import structlog

# Import routers
from app.routers import (
    proposals, learning, analytics, approval, conquest, imperium, 
    guardian, sandbox, code, oath_papers, experiments, notify,
    github_webhook, agents, growth, notifications
)
from app.routers.codex import router as codex_router

# Import services
from app.services.ai_learning_service import AILearningService
from app.services.ml_service import MLService
from app.core.config import settings
from app.core.database import init_database, close_database, create_tables, create_indexes
from app.core.logging import setup_logging

# Initialize new services
from app.services.ai_agent_service import AIAgentService
from app.services.github_service import GitHubService
from app.services.background_service import BackgroundService
from app.services.ai_growth_service import AIGrowthService

# Setup logging
setup_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AI Backend with scikit-learn integration")
    
    # Initialize database
    await init_database()
    
    # Initialize ML service
    await MLService.initialize()
    
    # Initialize AI Learning service
    await AILearningService.initialize()
    
    # Initialize new services
    await AIAgentService.initialize()
    await GitHubService.initialize()
    await BackgroundService.initialize()
    await AIGrowthService.initialize()
    
    # Start autonomous AI cycle in background
    background_service = BackgroundService()
    asyncio.create_task(background_service.start_autonomous_cycle())
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Backend")
    await close_database()

# Create FastAPI app
app = FastAPI(
    title="AI Backend with scikit-learn",
    description="Advanced AI backend with machine learning capabilities using scikit-learn",
    version="2.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "AI Backend with scikit-learn is running",
        "version": "2.0.0"
    }

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "AI Learning Backend with scikit-learn is running"
    }

# Debug endpoint
@app.get("/debug")
async def debug_info():
    """Debug endpoint to show system statistics"""
    try:
        from app.models.sql_models import Proposal
        from app.core.database import get_session
        from sqlalchemy import select, func
        
        session = get_session()
        try:
            # Get proposal statistics
            total_result = await session.execute(select(func.count(Proposal.id)))
            total = total_result.scalar()
            
            pending_result = await session.execute(select(func.count(Proposal.id)).where(Proposal.status == "pending"))
            pending = pending_result.scalar()
            
            approved_result = await session.execute(select(func.count(Proposal.id)).where(Proposal.status == "approved"))
            approved = approved_result.scalar()
            
            rejected_result = await session.execute(select(func.count(Proposal.id)).where(Proposal.status == "rejected"))
            rejected = rejected_result.scalar()
            
            applied_result = await session.execute(select(func.count(Proposal.id)).where(Proposal.status == "applied"))
            applied = applied_result.scalar()
            
            test_passed_result = await session.execute(select(func.count(Proposal.id)).where(Proposal.status == "test-passed"))
            test_passed = test_passed_result.scalar()
            
            test_failed_result = await session.execute(select(func.count(Proposal.id)).where(Proposal.status == "test-failed"))
            test_failed = test_failed_result.scalar()
            
            # Get recent proposals
            recent_proposals_result = await session.execute(
                select(Proposal).order_by(Proposal.created_at.desc()).limit(5)
            )
            recent_proposals = recent_proposals_result.scalars().all()
            
            return {
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat(),
                "stats": {
                    "total": total,
                    "pending": pending,
                    "approved": approved,
                    "rejected": rejected,
                    "applied": applied,
                    "test_passed": test_passed,
                    "test_failed": test_failed
                },
                "recent_proposals": [
                    {
                        "id": str(p.id),
                        "ai_type": p.ai_type,
                        "file_path": p.file_path,
                        "status": p.status,
                        "created_at": p.created_at.isoformat() if getattr(p, "created_at", None) is not None else None
                    }
                    for p in recent_proposals
                ]
            }
        finally:
            await session.close()
    except Exception as e:
        logger.error("Error in debug endpoint", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# App functionality endpoints
@app.get("/api/app/status")
async def app_status():
    """App functionality status endpoint"""
    return {
        "status": "running",
        "message": "App is running and functional with scikit-learn",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "features": [
            "scikit-learn-ml",
            "proposals",
            "notifications", 
            "github-integration",
            "ai-learning",
            "nlp-processing"
        ]
    }

# GitHub integration status endpoint
@app.get("/api/github/status")
async def github_status():
    """GitHub integration status endpoint"""
    has_token = bool(os.getenv("GITHUB_TOKEN"))
    has_repo = bool(os.getenv("GITHUB_REPO"))
    has_repo_url = bool(os.getenv("GITHUB_REPO_URL"))
    has_username = bool(os.getenv("GITHUB_USERNAME"))
    
    # Check if we have either repo or repo_url + username
    repo_configured = has_repo or (has_repo_url and has_username)
    
    return {
        "status": "configured" if (has_token and repo_configured) else "not-configured",
        "message": "GitHub integration is configured" if (has_token and repo_configured) else "GitHub integration needs configuration",
        "timestamp": datetime.utcnow().isoformat(),
        "has_token": has_token,
        "has_repo": has_repo,
        "has_repo_url": has_repo_url,
        "has_username": has_username,
        "repo": os.getenv("GITHUB_REPO", os.getenv("GITHUB_REPO_URL", "not-set"))
    }

# Include routers
app.include_router(proposals.router, prefix="/api/proposals", tags=["proposals"])
app.include_router(code.router, prefix="/api/code", tags=["code"])
app.include_router(experiments.router, prefix="/api/experiments", tags=["experiments"])
app.include_router(guardian.router, prefix="/api/guardian", tags=["guardian"])
app.include_router(imperium.router, prefix="/api/imperium", tags=["imperium"])
app.include_router(sandbox.router, prefix="/api/sandbox", tags=["sandbox"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(notify.router, prefix="/api/notify", tags=["notify"])
app.include_router(learning.router, prefix="/api/learning", tags=["learning"])
app.include_router(approval.router, prefix="/api/approval", tags=["approval"])
app.include_router(oath_papers.router, prefix="/api/oath-papers", tags=["oath-papers"])
app.include_router(conquest.router, prefix="/api/conquest", tags=["conquest"])
app.include_router(github_webhook.router, prefix="/api/github", tags=["github"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(growth.router, prefix="/api/growth", tags=["growth"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(codex_router, prefix="/api/codex", tags=["Codex"])

# Add extra mounts for /api/ai/* compatibility
app.include_router(imperium.router, prefix="/api/ai/imperium", tags=["ai-imperium"])
app.include_router(guardian.router, prefix="/api/ai/guardian", tags=["ai-guardian"])
app.include_router(sandbox.router, prefix="/api/ai/sandbox", tags=["ai-sandbox"])
app.include_router(conquest.router, prefix="/api/ai/conquest", tags=["ai-conquest"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 4000)),
        reload=True,
        log_level="info"
    ) 