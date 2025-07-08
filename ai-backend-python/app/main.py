from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import imperium_learning, notifications, missions, imperium, guardian, conquest, sandbox, learning, growth, proposals, notify, oath_papers, codex, agents, analytics, github_webhook
from app.core.database import init_database, create_tables, create_indexes
from dotenv import load_dotenv
import asyncio
from datetime import datetime
from fastapi import APIRouter

app = FastAPI()

load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        await init_database()
        await create_tables()
        await create_indexes()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

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

@app.get("/health")
async def health_check():
    """Root-level health check endpoint"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "service": "imperium_backend",
            "endpoints": {
                "imperium": "/api/imperium",
                "health": "/health",
                "docs": "/docs"
            }
        }
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

# Add a simple /api/agents/status endpoint
@app.get("/api/agents/status")
async def get_agents_status():
    return {
        "imperium": {"status": "online"},
        "guardian": {"status": "online"},
        "sandbox": {"status": "online"},
        "conquest": {"status": "online"},
    } 