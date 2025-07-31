#!/usr/bin/env python3
"""
Database Initialization Script
"""

import asyncio
import sys
import os

# Add the backend path
sys.path.append('ai-backend-python')

async def init_database():
    """Initialize the database"""
    try:
        from app.core.database import init_database
        from app.services.token_usage_service import TokenUsageService
        
        print("🔧 Initializing database...")
        await init_database()
        print("✅ Database initialized successfully")
        
        print("\n🔧 Initializing token usage service...")
        token_service = await TokenUsageService.initialize()
        print("✅ Token usage service initialized")
        
        print("\n📊 Testing token system...")
        usage = await token_service.get_all_monthly_usage()
        print(f"✅ Token system working: {usage}")
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(init_database()) 