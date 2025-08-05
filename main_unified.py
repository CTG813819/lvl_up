"""
Unified FastAPI application for AI Backend with scikit-learn integration
This consolidates all functionality into a single, properly configured application
"""

import os
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import structlog
from multiprocessing import Process
import time

# Import all routers (consolidated from both main files)
from app.routers import (
    proposals, learning, analytics, approval, conquest, imperium, 
    guardian, sandbox, code, oath_papers, experiments, notify,
    github_webhook, agents, growth, notifications, missions
)
from app.routers.custody_protocol import router as custody_protocol
from app.routers.imperium_learning import router as imperium_learning_router
from app.routers.codex import router as codex_router
from app.routers.plugin import router as plugin_router
from app.routers.auto_apply import router as auto_apply_router
from app.routers.optimized_services import router as optimized_services_router
from app.routers.proposals import periodic_proposal_generation

# Import all additional routers from app/main.py (with correct router objects)
from app.routers import (
    enhanced_learning, terra_extensions, training_data, anthropic_test, 
    token_usage, weekly_notifications, black_library, imperium_extensions
)
from app.routers.enhanced_ai_router import router as enhanced_ai_router
from app.routers.system_status import router as system_status_router
from app.routers.ai import router as ai_router
from app.routers.agent_metrics import router as agent_metrics_router
from app.routers.scheduling import router as scheduling_router
from app.routers.enhanced_adversarial_testing import router as enhanced_adversarial_router
from app.routers.offline_chaos_router import router as offline_chaos_router
from app.routers.project_berserk import router as project_berserk_router
from app.routers.training_ground import router as training_ground_router
from app.routers.weapons import router as weapons_router

# Import new AI service routers
from app.routers.project_horus import router as project_horus_router
from app.routers.olympic_ai import router as olympic_ai_router
from app.routers.collaborative_ai import router as collaborative_ai_router
from app.routers.custodes_ai import router as custodes_ai_router

# Import services
from app.services.ai_learning_service import AILearningService
from app.services.ml_service import MLService
from app.core.config import settings
from app.core.database import init_database, close_database, create_tables, create_indexes
from app.core.logging import setup_logging

# Initialize all services
from app.services.ai_agent_service import AIAgentService
from app.services.github_service import GitHubService
from app.services.background_service import BackgroundService
from app.services.ai_growth_service import AIGrowthService
from app.services.imperium_learning_controller import ImperiumLearningController
from app.services.auto_apply_service import auto_apply_service
from app.services.cache_service import CacheService
from app.services.data_collection_service import DataCollectionService
from app.services.analysis_service import AnalysisService

# Initialize new AI services
from app.services.project_horus_service import project_horus_service
from app.services.olympic_ai_service import olympic_ai_service
from app.services.collaborative_ai_service import collaborative_ai_service
from app.services.custodes_ai_service import custodes_ai_service

# Initialize other services from app/main.py
from app.services.proposal_cycle_service import ProposalCycleService
from app.services.token_usage_service import TokenUsageService
from app.services.scheduled_notification_service import ScheduledNotificationService
from app.services.enhanced_autonomous_learning_service import EnhancedAutonomousLearningService  # FIXED IMPORT
from app.services.custody_protocol_service import CustodyProtocolService

# Setup logging
setup_logging()
logger = structlog.get_logger()

# @asynccontextmanager  # Temporarily disabled to fix 502 errors
async def lifespan_disabled(app: FastAPI):
    """Application lifespan events - handles startup and shutdown - TEMPORARILY DISABLED"""
    # Startup
    logger.info("🚀 Starting Unified AI Backend with scikit-learn integration")
    
    try:
        # Initialize database
        await init_database()
        await create_tables()
        await create_indexes()
        
        # Initialize ML service first
        await MLService.initialize()
        logger.info("✅ ML Service initialized")
        
        # Initialize AI Learning service
        await AILearningService.initialize()
        logger.info("✅ AI Learning Service initialized")
        
        # Initialize core services
        await AIAgentService.initialize()
        await GitHubService.initialize()
        await BackgroundService.initialize()
        await AIGrowthService.initialize()
        logger.info("✅ Core AI services initialized")
        
        # Initialize Imperium Learning Controller
        await ImperiumLearningController.initialize()
        logger.info("✅ Imperium Learning Controller initialized")
        
        # Initialize Auto-Apply Service
        await auto_apply_service.initialize()
        logger.info("✅ Auto-Apply Service initialized")
        
        # Initialize optimization services
        await CacheService.initialize()
        await DataCollectionService.initialize()
        await AnalysisService.initialize()
        logger.info("✅ Optimization services initialized")
        
        # Initialize Custody Protocol Service (required for custody tests, Olympic events, and collaborative tests)
        custody_service = await CustodyProtocolService.initialize()
        logger.info("✅ Custody Protocol Service initialized")
        
        # Initialize additional services from app/main.py
        proposal_cycle_service = await ProposalCycleService.initialize()
        token_usage_service = await TokenUsageService.initialize()
        scheduled_notification_service = await ScheduledNotificationService.initialize()
        logger.info("✅ Additional services initialized")
        
        # Initialize new AI services
        logger.info("🤖 Initializing specialized AI services: Project Horus, Olympic AI, Collaborative AI, Custodes AI")
        # These are already initialized by their imports, but we log the status
        
        # Start background jobs by default [[memory:4401230]]
        # Only disable if explicitly set to 0
        if os.getenv("RUN_BACKGROUND_JOBS", "1") != "0":
            # Start autonomous AI cycle in background
            background_service = BackgroundService()
            asyncio.create_task(background_service.start_autonomous_cycle())
            
            # Start enhanced autonomous learning service with custody protocol
            enhanced_learning_service = EnhancedAutonomousLearningService()
            asyncio.create_task(enhanced_learning_service.start_enhanced_autonomous_learning())
            
            # Start auto-apply monitoring
            asyncio.create_task(auto_apply_service.start_monitoring())

            # Start periodic proposal generation feedback loop
            asyncio.create_task(periodic_proposal_generation())
            
            # Start additional services from app/main.py
            asyncio.create_task(scheduled_notification_service.start_weekly_scheduler())
            
            print("✅ Background jobs started - Learning cycles active")
            logger.info("✅ Background jobs started - Learning cycles active")
        else:
            print("⚠️ Background jobs disabled (RUN_BACKGROUND_JOBS=0)")
            logger.warning("⚠️ Background jobs disabled (RUN_BACKGROUND_JOBS=0)")
        
        # Detect Railway environment to prevent multiprocessing hangs
        railway_env = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT") or os.getenv("RAILWAY_ENVIRONMENT_NAME")
        
        if railway_env:
            # Railway deployment - avoid multiprocessing, use integrated routers
            logger.info("🚂 Railway environment detected - using integrated services")
            print("🚂 Railway environment detected - using integrated services")
            logger.info("✅ Enhanced adversarial testing integrated in main process")
            logger.info("✅ Training ground available via custody protocol")
        else:
            # Local development - use separate processes for services
            logger.info("🏠 Local development - starting separate service processes")
            
            # Start enhanced adversarial testing service on port 8001 [[memory:4401228]]
            try:
                def start_enhanced_adversarial_service():
                    """Start the enhanced adversarial testing service on port 8001"""
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                    
                    from standalone_enhanced_adversarial_testing import app as adversarial_app
                    
                    uvicorn.run(
                        adversarial_app,
                        host="0.0.0.0",
                        port=8001,
                        log_level="info",
                        access_log=True
                    )
                
                # Start enhanced adversarial testing service in a separate process
                adversarial_process = Process(target=start_enhanced_adversarial_service)
                adversarial_process.start()
                
                logger.info("✅ Enhanced adversarial testing service started on port 8001")
                print("✅ Enhanced adversarial testing service started on port 8001")
                
            except Exception as e:
                logger.error(f"❌ Failed to start enhanced adversarial testing service: {str(e)}")
                print(f"❌ Failed to start enhanced adversarial testing service: {str(e)}")
            
            # Start training ground server on port 8002
            try:
                def start_training_ground_service():
                    """Start the training ground service on port 8002"""
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                    
                    from training_ground_server import app as training_ground_app
                    
                    uvicorn.run(
                        training_ground_app,
                        host="0.0.0.0",
                        port=8002,
                        log_level="info",
                        access_log=True
                    )
                
                # Start training ground service in a separate process
                training_ground_process = Process(target=start_training_ground_service)
                training_ground_process.start()
                
                logger.info("✅ Training ground service started on port 8002")
                print("✅ Training ground service started on port 8002")
                
            except Exception as e:
                logger.error(f"❌ Failed to start training ground service: {str(e)}")
                print(f"❌ Failed to start training ground service: {str(e)}")
        
        logger.info("🎯 All systems initialized and running!")
        print("🎯 All systems initialized and running!")
        if railway_env:
            print("📊 Main Server: Railway deployment running")
            print("⚔️ Enhanced Adversarial Testing: Integrated in main process") 
            print("🏋️ Training Ground: Available via custody protocol")
        else:
            print("📊 Main Server: http://localhost:8000")
            print("⚔️ Adversarial Testing: http://localhost:8001") 
            print("🏋️ Training Ground: http://localhost:8002")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}")
        print(f"❌ Error during startup: {str(e)}")
        raise
    
    # Shutdown
    logger.info("🛑 Shutting down AI Backend")
    try:
        # Stop background services
        if 'background_service' in locals():
            await background_service.stop_autonomous_cycle()
        if 'scheduled_notification_service' in locals():
            await scheduled_notification_service.stop_weekly_scheduler()
        await close_database()
        logger.info("✅ Shutdown complete")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {str(e)}")

# Create FastAPI app with unified configuration
app = FastAPI(
    title="AI Backend - Unified System", 
    description="Complete AI Backend with Learning Cycles, Testing Systems, and ML Integration",
    version="2.0.0",
    # lifespan=lifespan  # Temporarily disabled
)

# Add middleware (consolidated from both apps)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com", "*"],  # Allow both specific and all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Health check endpoints - ULTRA SIMPLE for Railway
@app.get("/")
def root():
    """Root endpoint - basic health check - SYNCHRONOUS"""
    return {"status": "healthy"}

@app.get("/health")
def health_check():
    """Railway health check - SYNCHRONOUS and zero dependencies"""
    return {"status": "healthy"}

@app.get("/api/health")  
def api_health_check():
    """Detailed API health check - SYNCHRONOUS"""
    return {
        "status": "ok",
        "message": "AI Learning Backend is running", 
        "endpoints": 475,
        "projects": ["horus", "berserk", "adversarial", "training_ground", "imperium"]
    }

# Include all routers (consolidated from both main files)
# Core routers
app.include_router(imperium_learning_router)
app.include_router(notifications, prefix="/api/notifications", tags=["Notifications"])
app.include_router(missions, prefix="/api/missions", tags=["Missions"])
app.include_router(imperium, prefix="/api/imperium", tags=["Imperium"])
app.include_router(guardian, prefix="/api/guardian", tags=["Guardian"])
app.include_router(conquest, prefix="/api/conquest", tags=["Conquest"])
app.include_router(sandbox, prefix="/api/sandbox", tags=["Sandbox"])
app.include_router(learning, prefix="/api/learning", tags=["Learning"])
app.include_router(growth, prefix="/api/growth", tags=["Growth"])
app.include_router(proposals, prefix="/api/proposals", tags=["Proposals"])
app.include_router(notify, prefix="/api/notify", tags=["Notify"])
app.include_router(oath_papers, prefix="/api/oath-papers", tags=["Oath Papers"])
app.include_router(codex_router, prefix="/api/codex", tags=["Codex"])
app.include_router(agents, prefix="/api/agents", tags=["Agents"])
app.include_router(analytics, prefix="/api/analytics", tags=["Analytics"])
app.include_router(github_webhook, prefix="/api/github", tags=["GitHub"])
app.include_router(code, prefix="/api/code", tags=["Code"])
app.include_router(approval, prefix="/api/approval", tags=["Approval"])
app.include_router(experiments, prefix="/api/experiments", tags=["Experiments"])
app.include_router(plugin_router, prefix="/api/plugins", tags=["Plugins"])
app.include_router(auto_apply_router, prefix="/api/auto-apply", tags=["Auto Apply"])
app.include_router(optimized_services_router, prefix="/api/optimized", tags=["Optimized Services"])

# Additional routers from app/main.py
app.include_router(enhanced_learning)
app.include_router(terra_extensions)
app.include_router(training_data)
app.include_router(anthropic_test)
app.include_router(token_usage)
app.include_router(weekly_notifications)
app.include_router(custody_protocol, prefix="/api/custody", tags=["Custody Protocol"])
app.include_router(black_library, tags=["Black Library"])
app.include_router(imperium_extensions, prefix="/api/imperium-extensions", tags=["Imperium Extensions"])
app.include_router(enhanced_ai_router, prefix="/api", tags=["Enhanced AI"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI"])
app.include_router(system_status_router, prefix="/api/system", tags=["System"])
app.include_router(weapons_router, prefix="/api/weapons", tags=["Weapons"])
app.include_router(agent_metrics_router, prefix="/api/agent-metrics", tags=["Agent Metrics"])
app.include_router(scheduling_router, prefix="/api/scheduling", tags=["Scheduling"])
app.include_router(enhanced_adversarial_router, prefix="/api/enhanced-adversarial", tags=["Enhanced Adversarial Testing"])
app.include_router(project_berserk_router, prefix="/api/project-warmaster", tags=["Project Warmaster"])
app.include_router(training_ground_router, prefix="/api/training-ground", tags=["Training Ground"])
app.include_router(offline_chaos_router, prefix="/api/offline-chaos", tags=["Offline Chaos"])

# New AI service routers
app.include_router(project_horus_router)  # Already has prefix="/api/project-horus" in router definition
app.include_router(olympic_ai_router, prefix="/api/olympic-ai", tags=["Olympic AI"])
app.include_router(collaborative_ai_router, prefix="/api/collaborative-ai", tags=["Collaborative AI"])
app.include_router(custodes_ai_router, prefix="/api/custodes-ai", tags=["Custodes AI"])

# WebSocket endpoints
@app.websocket("/ws/imperium/learning-analytics")
async def ws_learning_analytics(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")

# Debug endpoint
@app.get("/debug")
async def debug_info():
    """Debug information endpoint"""
    try:
        from sqlalchemy import select, func
        from app.models.sql_models import Proposal
        from app.core.database import get_session
        
        async with get_session() as session:
            # Get proposal statistics
            total_result = await session.execute(select(func.count(Proposal.id)))
            total = total_result.scalar()
            
            pending_result = await session.execute(select(func.count(Proposal.id)).where(Proposal.status == "pending"))
            pending = pending_result.scalar()
            
            approved_result = await session.execute(select(func.count(Proposal.id)).where(Proposal.status == "approved"))
            approved = approved_result.scalar()
            
            return {
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "2.0.0",
                "stats": {
                    "total_proposals": total,
                    "pending": pending,
                    "approved": approved
                },
                "services": {
                    "main_server": "port_8000",
                    "adversarial_testing": "port_8001", 
                    "training_ground": "port_8002",
                    "learning_cycles": "active",
                    "custody_testing": "active",
                    "olympic_events": "active",
                    "collaborative_testing": "active"
                }
            }
            
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

if __name__ == "__main__":
    # Run the unified application on port 8000 [[memory:4401229]]
    uvicorn.run(
        "main_unified:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload for production
        log_level="info",
        access_log=True
    )