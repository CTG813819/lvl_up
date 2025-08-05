#!/usr/bin/env python3
"""
Test the background service directly
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_background_service():
    """Test the background service directly"""
    try:
        from app.core.database import init_database
        from app.services.background_service import BackgroundService
        
        print("🧪 Testing Background Service...")
        
        # Initialize database first
        await init_database()
        print("✅ Database initialized")
        
        # Initialize background service
        background_service = await BackgroundService.initialize()
        print("✅ Background Service initialized")
        
        # Test starting the autonomous cycle
        print("🤖 Starting autonomous cycle...")
        await background_service.start_autonomous_cycle()
        
        # Wait a bit to see if it starts
        await asyncio.sleep(5)
        
        print("✅ Background service test completed")
        
    except Exception as e:
        print(f"❌ Error testing background service: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_background_service()) 