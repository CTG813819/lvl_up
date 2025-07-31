#!/usr/bin/env python3
"""
Enhanced Adversarial Testing Service Startup Script
Runs the enhanced adversarial testing service on port 8001
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.enhanced_adversarial_testing import router as enhanced_adversarial_router
from app.services.enhanced_scenario_service import EnhancedScenarioService
import asyncio
import structlog

logger = structlog.get_logger()

# Create FastAPI app for enhanced adversarial testing service
app = FastAPI(
    title="Enhanced Adversarial Testing Service",
    description="Enhanced adversarial testing system with continuous learning and AI response display",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the enhanced adversarial testing router
app.include_router(enhanced_adversarial_router, prefix="/api/enhanced-adversarial", tags=["Enhanced Adversarial Testing"])

# Add a root endpoint
@app.get("/")
async def root():
    return {
        "service": "Enhanced Adversarial Testing Service",
        "version": "2.0.0",
        "port": 8001,
        "status": "running",
        "features": [
            "continuous_internet_learning",
            "llm_enhanced_scenarios",
            "indefinite_scenario_generation",
            "real_time_ai_response_display",
            "enhanced_warp_integration"
        ]
    }

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Enhanced Adversarial Testing Service",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Initialize enhanced scenario service on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        logger.info("Starting Enhanced Adversarial Testing Service on port 8001")
        logger.info("Initializing Enhanced Scenario Service with continuous learning")
        
        # Initialize the enhanced scenario service
        scenario_service = EnhancedScenarioService()
        await scenario_service.initialize()
        
        logger.info("Enhanced Scenario Service initialized successfully")
        logger.info("Continuous learning loop started")
        logger.info("Enhanced Adversarial Testing Service ready on port 8001")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the service on port 8001
    uvicorn.run(
        "start_enhanced_adversarial_service:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 