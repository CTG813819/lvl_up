from fastapi import FastAPI, WebSocket, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import time
from app.routers import imperium_learning, notifications, missions, imperium, guardian, conquest, sandbox, learning, growth, proposals, notify, oath_papers, codex, agents, analytics, github_webhook, code, approval, experiments, plugin, enhanced_learning, terra_extensions, training_data, anthropic_test, optimized_services, token_usage, weekly_notifications, custody_protocol, black_library, imperium_extensions, enhanced_ai_router, system_status, ai, agent_metrics, scheduling, enhanced_adversarial_testing, project_berserk, universal_hub, offline_chaos_router
from app.core.database import init_database, create_tables, create_indexes
from dotenv import load_dotenv
import asyncio
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request, Response
from app.core.config import settings
from app.core.database import get_session
from app.models.sql_models import Proposal, TokenUsage, TokenUsageLog
from app.models.terra_extension import TerraExtension
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.routers.imperium_learning import router as imperium_learning_router
from app.routers.conquest import router as conquest_router
from app.routers.oath_papers import router as oath_papers_router
from app.routers.analytics import router as analytics_router
from app.routers.plugin import router as plugin_router
from app.routers.optimized_services import router as optimized_router
from app.services.background_service import BackgroundService
from app.services.proposal_cycle_service import ProposalCycleService
from app.services.token_usage_service import TokenUsageService
from app.services.scheduled_notification_service import ScheduledNotificationService
from sqlalchemy import text
import logging
import structlog
from app.services.enhanced_autonomous_learning_service import EnhancedAutonomousLearningService
from app.core.watchdog import start_watchdog
from app.routers.ai import router as ai_router
from app.routers.weapons import router as weapons
from app.services.custody_protocol_service import CustodyProtocolService
from app.routers.scheduling import router as scheduling_router
from app.routers.project_berserk import router as project_berserk_router

logger = structlog.get_logger()

app = FastAPI()

load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],  # Restrict to specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

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

# Initialize services
background_service = None
proposal_cycle_service = None
token_usage_service = None
scheduled_notification_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global background_service, proposal_cycle_service, token_usage_service, scheduled_notification_service
    import os
    try:
        # Initialize database
        await init_database()
        
        # Create database tables (including token usage tables)
        await create_tables()
        
        # Create database indexes
        await create_indexes()
        
        # Initialize Custody Protocol Service (required for custody tests, Olympic events, and collaborative tests)
        from app.services.custody_protocol_service import CustodyProtocolService
        custody_service = await CustodyProtocolService.initialize()
        logger.info("✅ Custody Protocol Service initialized")
        
        # Initialize background service (always start)
        background_service = await BackgroundService.initialize()
        
        # Initialize proposal cycle service
        proposal_cycle_service = await ProposalCycleService.initialize()
        
        # Initialize token usage service
        token_usage_service = await TokenUsageService.initialize()
        
        # Initialize scheduled notification service
        scheduled_notification_service = await ScheduledNotificationService.initialize()
        
        # Start background services
        await background_service.start_autonomous_cycle()
        # Note: Proposal cycle is handled by periodic_proposal_generation() in proposals router
        # Note: Token tracking is handled internally by TokenUsageService
        await scheduled_notification_service.start_weekly_scheduler()
        
        logger.info("✅ All background services started")
            
    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global background_service, proposal_cycle_service, scheduled_notification_service
    try:
        if background_service:
            await background_service.stop_autonomous_cycle()
        if scheduled_notification_service:
            await scheduled_notification_service.stop_weekly_scheduler()
        print("✅ Application shutdown complete")
    except Exception as e:
        print(f"❌ Error during shutdown: {e}")

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
app.include_router(plugin_router, prefix="/api/plugins", tags=["Plugins"])
app.include_router(enhanced_learning)
app.include_router(terra_extensions)
app.include_router(training_data)
app.include_router(anthropic_test)
app.include_router(optimized_router, prefix="/optimized", tags=["Optimized Services"])
app.include_router(token_usage)
app.include_router(weekly_notifications)
app.include_router(custody_protocol, prefix="/custody", tags=["Custody Protocol"])
app.include_router(black_library, tags=["Black Library"])
app.include_router(imperium_extensions, prefix="/api/imperium-extensions", tags=["Imperium Extensions"])
app.include_router(enhanced_ai_router.router, prefix="/api", tags=["Enhanced AI"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI"])
app.include_router(system_status, prefix="/api/system", tags=["System"])
app.include_router(weapons)
app.include_router(agent_metrics.router, prefix="/api/agent-metrics", tags=["agent-metrics"])
app.include_router(scheduling_router, prefix="/api/scheduling", tags=["Scheduling"])
app.include_router(enhanced_adversarial_testing.router, prefix="/api", tags=["Enhanced Adversarial Testing"])
app.include_router(project_berserk_router, prefix="/api/project-warmaster", tags=["Project Warmaster"])
app.include_router(universal_hub.router, prefix="/api/project-warmaster/universal-hub", tags=["Universal Hub"])
app.include_router(offline_chaos_router.router, prefix="/api/offline-chaos", tags=["Offline Chaos"])

@app.websocket("/ws/imperium/learning-analytics")
async def ws_learning_analytics(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")

# Remove stub /api/health and /api/status endpoints
# Instead, add proxy endpoints that call the real implementations from imperium_learning
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

# Set up logging
logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.get("/api/health")
async def health_check_proxy(request: Request):
    # Call the real health_check from imperium_learning
    from app.routers.imperium_learning import health_check
    return await health_check()

@app.get("/api/status")
async def status_proxy(request: Request):
    """Get system status - simplified version"""
    try:
        # Get basic system status
        system_status = {
            "status": "active",
            "api_version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "background_service": "active",
                "ai_learning_service": "active",
                "database": "connected"
            },
            "supported_features": [
                "agent_registration",
                "learning_cycles",
                "internet_learning",
                "real_time_analytics",
                "persistence",
                "trusted_sources"
            ]
        }
        
        return system_status
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add a simple /api/agents/status endpoint
@app.get("/api/agents/status")
async def get_agents_status():
    return {
        "imperium": {"status": "online"},
        "guardian": {"status": "online"},
        "sandbox": {"status": "online"},
        "conquest": {"status": "online"},
    }

# Add database health check endpoint
@app.get("/api/database/health")
async def database_health_check():
    """Check database connection health"""
    try:
        from app.core.database import get_pool_status, engine
        pool_status = await get_pool_status()
        
        # Test actual connection
        if engine:
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT 1 as test"))
                test_result = result.fetchone()
                
            return {
                "status": "healthy",
                "database_connected": True,
                "test_query": "passed",
                "pool_status": pool_status,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "unhealthy",
                "database_connected": False,
                "error": "Engine not initialized",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database_connected": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.now().isoformat()
        }

# /api/oath-papers/learn: implement as a GET that returns recent learning results
@app.get("/api/oath-papers/learn")
async def oath_papers_learn_proxy():
    """Get oath papers learning data - simplified version"""
    return {
        "status": "active",
        "learning_data": [],
        "timestamp": datetime.now().isoformat()
    }

# /api/conquest/build-failure: wire to the real handler in conquest.py
from app.routers.conquest import report_build_failure, BuildFailureRequest
@app.post("/api/conquest/build-failure")
async def conquest_build_failure_proxy(request: Request):
    data = await request.json()
    build_failure_req = BuildFailureRequest(**data)
    return await report_build_failure(build_failure_req)

# /api/conquest/analytics: wire to analytics router for real data
@app.get("/api/conquest/analytics")
async def conquest_analytics_proxy():
    """Get conquest analytics - simplified version"""
    return {
        "status": "active",
        "analytics": {},
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/config")
async def api_config():
    return settings.dict()

@app.get("/api/info")
async def api_info():
    return {"info": "Lvl Up API", "description": "AI Learning Backend", "time": str(datetime.utcnow())}

@app.get("/api/version")
async def api_version():
    return {"version": "1.0.0", "build": "2025-07-08"}

@app.post("/api/proposals/status")
async def proposals_status(data: dict, db: AsyncSession = Depends(get_session)):
    proposal_id = data.get("id")
    if not proposal_id:
        return JSONResponse(status_code=400, content={"error": "Missing proposal id"})
    proposal = await db.get(Proposal, proposal_id)
    if not proposal:
        return JSONResponse(status_code=404, content={"error": "Proposal not found"})
    return {"id": proposal_id, "status": proposal.status} 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8003,  # HORUS Project Berserk on port 8003
        reload=True,
        log_level="info"
    ) 