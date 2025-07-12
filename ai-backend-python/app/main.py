from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.routers import imperium_learning, notifications, missions, imperium, guardian, conquest, sandbox, learning, growth, proposals, notify, oath_papers, codex, agents, analytics, github_webhook, code, approval, experiments, plugin, enhanced_learning, terra_extensions, training_data, anthropic_test, optimized_services
from app.core.database import init_database, create_tables, create_indexes
from dotenv import load_dotenv
import asyncio
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request, Response
from app.core.config import settings
from app.core.database import get_session
from app.models.sql_models import Proposal
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

app = FastAPI()

load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
background_service = None
proposal_cycle_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global background_service, proposal_cycle_service
    
    try:
        # Initialize database
        await init_database()
        
        # Initialize background service
        background_service = await BackgroundService.initialize()
        
        # Initialize proposal cycle service
        proposal_cycle_service = await ProposalCycleService.initialize()
        
        # Start background services
        asyncio.create_task(background_service.start_autonomous_cycle())
        asyncio.create_task(proposal_cycle_service.start_cycle_service())
        
        print("✅ Application startup complete")
        
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global background_service, proposal_cycle_service
    
    try:
        if background_service:
            await background_service.stop_autonomous_cycle()
        
        if proposal_cycle_service:
            await proposal_cycle_service.stop_cycle_service()
        
        print("✅ Application shutdown complete")
        
    except Exception as e:
        print(f"❌ Error during shutdown: {e}")

app.include_router(imperium_learning.router)
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(missions.router, prefix="/api/missions", tags=["Missions"])
app.include_router(imperium.router, prefix="/api/imperium", tags=["Imperium"])
app.include_router(guardian.router, prefix="/api/guardian", tags=["Guardian"])
app.include_router(conquest.router, prefix="/api/conquest", tags=["Conquest"])
app.include_router(sandbox.router, prefix="/api/sandbox", tags=["Sandbox"])
app.include_router(learning.router, prefix="/api/learning", tags=["Learning"])
app.include_router(growth.router, prefix="/api/growth", tags=["Growth"])
app.include_router(proposals.router, prefix="/api/proposals", tags=["Proposals"])
app.include_router(notify.router, prefix="/api/notify", tags=["Notify"])
app.include_router(oath_papers.router, prefix="/api/oath-papers", tags=["Oath Papers"])
app.include_router(codex.router, prefix="/api/codex", tags=["Codex"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(github_webhook.router, prefix="/api/github", tags=["GitHub"])
app.include_router(code.router, prefix="/api/code", tags=["Code"])
app.include_router(approval.router, prefix="/api/approval", tags=["Approval"])
app.include_router(experiments.router, prefix="/api/experiments", tags=["Experiments"])
app.include_router(plugin_router, prefix="/api/plugins", tags=["Plugins"])
app.include_router(enhanced_learning.router)
app.include_router(terra_extensions.router)
app.include_router(training_data.router)
app.include_router(anthropic_test.router)
app.include_router(optimized_router, prefix="/optimized", tags=["Optimized Services"])

@app.websocket("/ws/imperium/learning-analytics")
async def ws_learning_analytics(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")

# Remove stub /api/health and /api/status endpoints
# Instead, add proxy endpoints that call the real implementations from imperium_learning
from fastapi import Request
from fastapi.responses import JSONResponse

@app.get("/api/health")
async def health_check_proxy(request: Request):
    # Call the real health_check from imperium_learning
    from app.routers.imperium_learning import health_check
    return await health_check()

@app.get("/api/status")
async def status_proxy(request: Request):
    from app.routers.imperium_learning import get_system_status
    return await get_system_status()

# Add a simple /api/agents/status endpoint
@app.get("/api/agents/status")
async def get_agents_status():
    return {
        "imperium": {"status": "online"},
        "guardian": {"status": "online"},
        "sandbox": {"status": "online"},
        "conquest": {"status": "online"},
    }

# /api/oath-papers/learn: implement as a GET that returns recent learning results
@app.get("/api/oath-papers/learn")
async def oath_papers_learn_proxy():
    # Use the AI insights endpoint for real learning data
    from app.routers.oath_papers import get_oath_papers_ai_insights
    return await get_oath_papers_ai_insights()

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
    # Use system performance as a proxy for conquest analytics
    from app.routers.analytics import get_system_performance
    return await get_system_performance()

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