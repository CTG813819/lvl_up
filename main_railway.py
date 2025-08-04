#!/usr/bin/env python3
"""
Railway-Optimized AI Backend - Single Process Mode
Designed to avoid multiprocessing issues in containerized environments
"""

import os
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import structlog

# Core imports
from app.core.database import init_database, create_tables, create_indexes
from app.core.logging import setup_logging

# Service imports
from app.services.ml_service import MLService
from app.services.ai_learning_service import AILearningService
from app.services.ai_agent_service import AIAgentService
from app.services.github_service import GitHubService
from app.services.background_service import BackgroundService
from app.services.ai_growth_service import AIGrowthService
from app.services.cache_service import CacheService
from app.services.data_collection_service import DataCollectionService
from app.services.analysis_service import AnalysisService
from app.services.custody_protocol_service import CustodyProtocolService
from app.services.proposal_cycle_service import ProposalCycleService
from app.services.token_usage_service import TokenUsageService
from app.services.scheduled_notification_service import ScheduledNotificationService
from app.services.auto_apply_service import auto_apply_service
from app.services.imperium_learning_controller import ImperiumLearningController

# Setup logging
setup_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events - Railway optimized for single process"""
    # Startup
    logger.info("🚂 Starting Railway-Optimized AI Backend")
    print("🔧 RAILWAY DEBUG: Entered lifespan function")
    logger.info("🔧 RAILWAY DEBUG: Entered lifespan function")
    
    try:
        # Initialize database
        logger.info("🔧 RAILWAY DEBUG: Starting database initialization...")
        await init_database()
        logger.info("🔧 RAILWAY DEBUG: Database engine created...")
        await create_tables()
        logger.info("🔧 RAILWAY DEBUG: Tables created...")
        await create_indexes()
        logger.info("✅ Database initialized")
        
        # Initialize ML service
        logger.info("🔧 RAILWAY DEBUG: Starting ML Service initialization...")
        await MLService.initialize()
        logger.info("✅ ML Service initialized")
        
        # Initialize AI Learning service
        logger.info("🔧 RAILWAY DEBUG: Starting AI Learning Service initialization...")
        await AILearningService.initialize()
        logger.info("✅ AI Learning Service initialized")
        
        # Initialize core services
        logger.info("🔧 RAILWAY DEBUG: Starting AIAgentService initialization...")
        await AIAgentService.initialize()
        logger.info("🔧 RAILWAY DEBUG: AIAgentService initialized")
        
        logger.info("🔧 RAILWAY DEBUG: Starting GitHubService initialization...")
        await GitHubService.initialize()
        logger.info("🔧 RAILWAY DEBUG: GitHubService initialized")
        
        logger.info("🔧 RAILWAY DEBUG: Starting BackgroundService initialization...")
        await BackgroundService.initialize()
        logger.info("🔧 RAILWAY DEBUG: BackgroundService initialized")
        
        logger.info("🔧 RAILWAY DEBUG: Starting AIGrowthService initialization...")
        await AIGrowthService.initialize()
        logger.info("✅ Core AI services initialized")
        
        # Initialize Imperium Learning Controller
        logger.info("🔧 RAILWAY DEBUG: Starting Imperium Learning Controller initialization...")
        await ImperiumLearningController.initialize()
        logger.info("✅ Imperium Learning Controller initialized")
        
        # Initialize Auto-Apply Service
        logger.info("🔧 RAILWAY DEBUG: Starting Auto-Apply Service initialization...")
        await auto_apply_service.initialize()
        logger.info("✅ Auto-Apply Service initialized")
        
        # Initialize optimization services
        logger.info("🔧 RAILWAY DEBUG: Starting CacheService initialization...")
        await CacheService.initialize()
        logger.info("🔧 RAILWAY DEBUG: CacheService initialized")
        
        logger.info("🔧 RAILWAY DEBUG: Starting DataCollectionService initialization...")
        await DataCollectionService.initialize()
        logger.info("🔧 RAILWAY DEBUG: DataCollectionService initialized")
        
        logger.info("🔧 RAILWAY DEBUG: Starting AnalysisService initialization...")
        await AnalysisService.initialize()
        logger.info("✅ Optimization services initialized")
        
        # Initialize Custody Protocol Service
        logger.info("🔧 RAILWAY DEBUG: Starting Custody Protocol Service initialization...")
        custody_service = await CustodyProtocolService.initialize()
        logger.info("✅ Custody Protocol Service initialized")
        
        # Initialize additional services
        logger.info("🔧 RAILWAY DEBUG: Starting ProposalCycleService initialization...")
        proposal_cycle_service = await ProposalCycleService.initialize()
        logger.info("🔧 RAILWAY DEBUG: ProposalCycleService initialized")
        
        logger.info("🔧 RAILWAY DEBUG: Starting TokenUsageService initialization...")
        token_usage_service = await TokenUsageService.initialize()
        logger.info("🔧 RAILWAY DEBUG: TokenUsageService initialized")
        
        logger.info("🔧 RAILWAY DEBUG: Starting ScheduledNotificationService initialization...")
        scheduled_notification_service = await ScheduledNotificationService.initialize()
        logger.info("✅ Additional services initialized")
        
        # Start background jobs (Railway optimized)
        logger.info("🔧 RAILWAY DEBUG: Checking background jobs environment...")
        if os.getenv("RUN_BACKGROUND_JOBS", "1") != "0":
            logger.info("🔧 RAILWAY DEBUG: Starting background jobs...")
            print("🔧 RAILWAY DEBUG: Starting background jobs...")
            
            # Start autonomous AI cycle in background (non-blocking)
            logger.info("🔧 RAILWAY DEBUG: Creating background service instance...")
            print("🔧 RAILWAY DEBUG: Creating background service instance...")
            background_service = BackgroundService()
            logger.info("🔧 RAILWAY DEBUG: Background service instance created")
            print("🔧 RAILWAY DEBUG: Background service instance created")
            
            logger.info("🔧 RAILWAY DEBUG: Starting autonomous cycle task...")
            print("🔧 RAILWAY DEBUG: Starting autonomous cycle task...")
            asyncio.create_task(background_service.start_autonomous_cycle())
            logger.info("🔧 RAILWAY DEBUG: Autonomous cycle task created")
            print("🔧 RAILWAY DEBUG: Autonomous cycle task created")
            
            # Start proposal cycle service (non-blocking)
            logger.info("🔧 RAILWAY DEBUG: Starting proposal cycle task...")
            print("🔧 RAILWAY DEBUG: Starting proposal cycle task...")
            asyncio.create_task(proposal_cycle_service.start_proposal_cycle())
            logger.info("🔧 RAILWAY DEBUG: Proposal cycle task created")
            print("🔧 RAILWAY DEBUG: Proposal cycle task created")
            
            # Start scheduled notification service (non-blocking)
            logger.info("🔧 RAILWAY DEBUG: Starting notification scheduler task...")
            print("🔧 RAILWAY DEBUG: Starting notification scheduler task...")
            asyncio.create_task(scheduled_notification_service.start_weekly_scheduler())
            logger.info("🔧 RAILWAY DEBUG: Notification scheduler task created")
            print("🔧 RAILWAY DEBUG: Notification scheduler task created")
            
            logger.info("✅ Background services started (Railway optimized)")
            print("✅ Background services started (Railway optimized)")
        else:
            logger.info("🔧 RAILWAY DEBUG: Background jobs disabled via environment variable")
        
        logger.info("🎯 Railway AI Backend fully initialized!")
        print("🎯 Railway AI Backend fully initialized!")
        print("📊 Main Server: Railway deployment running")
        print("⚔️ Enhanced Adversarial Testing: Integrated in main process") 
        print("🏋️ Training Ground: Available via custody protocol")
        
        logger.info("🔧 RAILWAY DEBUG: About to yield - startup complete")
        print("🔧 RAILWAY DEBUG: About to yield - startup complete")
        yield
        logger.info("🔧 RAILWAY DEBUG: After yield - app is running")
        print("🔧 RAILWAY DEBUG: After yield - app is running")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}")
        print(f"❌ Error during startup: {str(e)}")
        raise
    
    # Shutdown
    logger.info("🛑 Shutting down Railway AI Backend")
    try:
        # Stop background services
        if 'background_service' in locals():
            await background_service.stop_autonomous_cycle()
        if 'scheduled_notification_service' in locals():
            await scheduled_notification_service.stop_weekly_scheduler()
        logger.info("✅ Background services stopped")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {str(e)}")

# Create FastAPI application
app = FastAPI(
    title="AI Backend - Railway Deployment",
    description="Complete AI Backend System optimized for Railway deployment",
    version="2.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Include routers from main_unified.py
from app.routers import (
    imperium_learning, notifications, missions, imperium, guardian, 
    conquest, sandbox, learning, growth, proposals, notify, oath_papers, 
    codex, agents, analytics, github_webhook, code, approval, experiments, 
    plugin, enhanced_learning, terra_extensions, training_data, anthropic_test, 
    optimized_services, token_usage, weekly_notifications, custody_protocol, 
    black_library, imperium_extensions, enhanced_ai_router
)

# Import router objects with correct aliases
from app.routers.system_status import router as system_status_router
from app.routers.ai import router as ai_router
from app.routers.agent_metrics import router as agent_metrics_router
from app.routers.scheduling import router as scheduling_router
from app.routers.enhanced_adversarial_testing import router as enhanced_adversarial_router
from app.routers.offline_chaos_router import router as offline_chaos_router
from app.routers.project_berserk import router as project_berserk_router
from app.routers.weapons import router as weapons_router
from app.routers.project_horus import router as project_horus_router
from app.routers.olympic_ai import router as olympic_ai_router
from app.routers.collaborative_ai import router as collaborative_ai_router
from app.routers.custodes_ai import router as custodes_ai_router

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "ok",
        "message": "Railway AI Backend is running",
        "version": "2.0.0",
        "environment": "railway",
        "services": {
            "adversarial_testing": "integrated",
            "training_ground": "custody_protocol",
            "background_jobs": "active"
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Backend - Railway Deployment",
        "status": "operational",
        "total_endpoints": "230+",
        "ai_services": 8,
        "deployment": "railway"
    }

# Include all routers
app.include_router(imperium_learning)
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
app.include_router(codex, prefix="/api/codex", tags=["Codex"])
app.include_router(agents, prefix="/api/agents", tags=["Agents"])
app.include_router(analytics, prefix="/api/analytics", tags=["Analytics"])
app.include_router(github_webhook, prefix="/api/github", tags=["GitHub"])
app.include_router(code, prefix="/api/code", tags=["Code"])
app.include_router(approval, prefix="/api/approval", tags=["Approval"])
app.include_router(experiments, prefix="/api/experiments", tags=["Experiments"])
app.include_router(plugin, prefix="/api/plugin", tags=["Plugin"])

# Enhanced services
app.include_router(enhanced_learning, prefix="/api/enhanced-learning", tags=["Enhanced Learning"])
app.include_router(terra_extensions, prefix="/api/terra-extensions", tags=["Terra Extensions"])
app.include_router(training_data, prefix="/api/training-data", tags=["Training Data"])
app.include_router(anthropic_test, prefix="/api/anthropic-test", tags=["Anthropic Test"])
app.include_router(optimized_services, prefix="/api/optimized-services", tags=["Optimized Services"])
app.include_router(token_usage, prefix="/api/token-usage", tags=["Token Usage"])
app.include_router(weekly_notifications, prefix="/api/weekly-notifications", tags=["Weekly Notifications"])
app.include_router(custody_protocol, prefix="/api/custody", tags=["Custody Protocol"])
app.include_router(black_library, prefix="/api/black-library", tags=["Black Library"])
app.include_router(imperium_extensions, prefix="/api/imperium-extensions", tags=["Imperium Extensions"])

# Router objects with aliases
app.include_router(enhanced_ai_router)
app.include_router(ai_router, prefix="/api/ai", tags=["AI"])
app.include_router(system_status_router, prefix="/api/system", tags=["System"])
app.include_router(weapons_router, prefix="/api/weapons", tags=["Weapons"])
app.include_router(agent_metrics_router, prefix="/api/agent-metrics", tags=["Agent Metrics"])
app.include_router(scheduling_router, prefix="/api/scheduling", tags=["Scheduling"])
app.include_router(enhanced_adversarial_router, prefix="/api/enhanced-adversarial", tags=["Enhanced Adversarial Testing"])
app.include_router(project_berserk_router) # Already has prefix="/api/project-warmaster" in router definition
app.include_router(offline_chaos_router, prefix="/api/offline-chaos", tags=["Offline Chaos"])

# New AI service routers
app.include_router(project_horus_router) # Already has prefix="/api/project-horus" in router definition
app.include_router(olympic_ai_router, prefix="/api/olympic-ai", tags=["Olympic AI"])
app.include_router(collaborative_ai_router, prefix="/api/collaborative-ai", tags=["Collaborative AI"])
app.include_router(custodes_ai_router, prefix="/api/custodes-ai", tags=["Custodes AI"])

# Debug endpoint
@app.get("/debug")
async def debug_info():
    """Debug information for Railway deployment"""
    return {
        "status": "operational",
        "environment": "railway",
        "deployment_mode": "single_process",
        "total_endpoints": "230+",
        "ai_services": {
            "imperium": "active",
            "guardian": "active", 
            "conquest": "active",
            "sandbox": "active",
            "project_horus": "integrated",
            "project_berserk": "integrated",
            "olympic_ai": "active",
            "collaborative_ai": "active"
        },
        "services": {
            "adversarial_testing": "integrated_in_main_process",
            "training_ground": "available_via_custody_protocol",
            "background_jobs": "active",
            "database": "neon_postgresql",
            "ml_models": "sckipit_integrated"
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main_railway:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )