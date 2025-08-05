#!/usr/bin/env python3
"""
AI Backend Server Startup Script
Starts the unified AI backend system with all components
"""

import os
import sys
import uvicorn
import structlog
from pathlib import Path

# Setup logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def main():
    """Start the unified AI backend server"""
    
    # Set environment variables if not set
    if not os.getenv("RUN_BACKGROUND_JOBS"):
        os.environ["RUN_BACKGROUND_JOBS"] = "1"
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    print("🚀 Starting AI Backend - Unified System")
    print("=" * 60)
    print("📊 Main Server: http://localhost:8000")
    print("⚔️ Adversarial Testing: http://localhost:8001") 
    print("🏋️ Training Ground: http://localhost:8002")
    print("=" * 60)
    print("🧠 Learning Cycles: ACTIVE")
    print("🛡️ Custody Testing: ACTIVE")
    print("🏆 Olympic Events: ACTIVE")
    print("🤝 Collaborative Testing: ACTIVE")
    print("🔬 ML Training: ACTIVE")
    print("=" * 60)
    
    try:
        # Run the unified application on port 8000
        uvicorn.run(
            "main_unified:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload for production stability
            log_level="info",
            access_log=True,
            workers=1  # Single worker to avoid conflicts with background tasks
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        logger.info("Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()