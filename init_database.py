#!/usr/bin/env python3
"""
<<<<<<< HEAD
Initialize database and token usage tables
=======
Database Initialization Script
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
"""

import asyncio
import sys
import os

<<<<<<< HEAD
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
=======
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
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
