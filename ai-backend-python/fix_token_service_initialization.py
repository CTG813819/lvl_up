#!/usr/bin/env python3
"""
Fix Token Service Initialization
================================

This script ensures the token usage service is properly initialized after database setup.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database
from app.services.token_usage_service import token_usage_service

async def fix_token_service():
    """Fix token service initialization"""
    
    try:
        print("🔧 Fixing token service initialization...")
        
        # Initialize database
        print("📊 Initializing database...")
        await init_database()
        
        # Initialize token usage service
        print("🔑 Initializing token usage service...")
        await token_usage_service.initialize()
        
        # Test the service
        print("🧪 Testing token usage service...")
        
        # Test getting usage for an AI
        test_ai = "imperium"
        usage = await token_usage_service.get_monthly_usage(test_ai)
        print(f"✅ Token usage service working for {test_ai}: {usage}")
        
        # Test recording usage
        await token_usage_service.record_token_usage(
            ai_type=test_ai,
            tokens_in=100,
            tokens_out=50,
            model_used="test-model",
            request_type="TEST"
        )
        print("✅ Token usage recording working")
        
        # Test getting usage again
        usage_after = await token_usage_service.get_monthly_usage(test_ai)
        print(f"✅ Usage after recording: {usage_after}")
        
        print("🎉 Token service initialization fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing token service: {str(e)}")
        return False

async def main():
    """Main function"""
    success = await fix_token_service()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 