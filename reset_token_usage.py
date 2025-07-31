#!/usr/bin/env python3
"""
Reset Token Usage for Testing
============================

This script resets token usage for all AIs. Use with caution in production.
"""

import asyncio
import sys
import os
from datetime import datetime

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def reset_token_usage():
    """Reset token usage for all AIs"""
    
    print("🔄 Resetting token usage for all AIs...")
    
    try:
        # Check if DATABASE_URL is set
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            print("Please check your .env file")
            return
        
        print(f"📊 Using database: {database_url[:50]}...")
        
        # Import database modules
        from app.core.database import init_database, get_session
        from app.models.sql_models import TokenUsage
        from sqlalchemy import text
        
        # Initialize database first
        print("📊 Initializing database...")
        await init_database()
        print("✅ Database initialized successfully")
        
        async with get_session() as session:
            # Delete all token usage records using text() function
            print("🗑️ Deleting token usage records...")
            await session.execute(text("DELETE FROM token_usage"))
            await session.commit()
            
            print("✅ Token usage reset successfully")
            print("📊 All AIs now have 0 token usage")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the ai-backend-python directory")
    except Exception as e:
        print(f"❌ Error resetting token usage: {str(e)}")
        print("Try running: python init_database.py first")

if __name__ == "__main__":
    asyncio.run(reset_token_usage())
