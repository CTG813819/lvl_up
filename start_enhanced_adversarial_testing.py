#!/usr/bin/env python3
"""
Start Enhanced Adversarial Testing Service
This script starts the enhanced adversarial testing service on port 8001
"""

import uvicorn
import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import init_database
from app.services.agent_metrics_service import AgentMetricsService

async def initialize_services():
    """Initialize database and services"""
    try:
        print("🔧 Initializing database...")
        await init_database()
        print("✅ Database initialized successfully")
        
        print("🔧 Initializing agent metrics service...")
        agent_metrics_service = AgentMetricsService()
        await agent_metrics_service.initialize()
        print("✅ Agent metrics service initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Failed to initialize services: {str(e)}")
        return False

def main():
    """Main function to start the enhanced adversarial testing service"""
    print("🚀 Starting Enhanced Adversarial Testing Service on port 8001...")
    
    # Initialize services
    if not asyncio.run(initialize_services()):
        print("❌ Failed to initialize services. Exiting.")
        sys.exit(1)
    
    # Start the service
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8001,
            reload=False,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Failed to start enhanced adversarial testing service: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 