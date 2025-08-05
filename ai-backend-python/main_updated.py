from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings
from app.core.database import engine
from app.models.sql_models import Base
from app.routers.ai_agents_updated import router as ai_agents_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LVL UP AI Backend - Updated Frequencies",
    description="AI Backend with optimized agent frequencies and staggered execution",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai_agents_router)

@app.get("/")
async def root():
    return {
        "message": "LVL UP AI Backend - Updated Frequencies",
        "version": "2.0.0",
        "status": "running",
        "ai_agents": {
            "imperium": "Every 1.5 hours",
            "sandbox": "Every 2 hours (starts 30min after Imperium)",
            "guardian": "Every 5 hours (starts 1hr after Imperium)",
            "custodes": "Every 1.5 hours (starts 1.5hr after Imperium, tests others)"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-15T12:00:00Z"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
