#!/usr/bin/env python3
"""
Initialize database and token usage tables
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database
from app.services.token_usage_service import token_usage_service

async def main():
    """Initialize database and token usage tables"""
    print("🔧 Initializing database and token usage tables...")
    
    try:
        # Initialize database
        await init_database()
        print("✅ Database initialized successfully")
        
        # Setup token usage tracking
        await token_usage_service._setup_monthly_tracking()
        print("✅ Token usage tracking initialized successfully")
        
        print("🎉 All initialization complete!")
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 