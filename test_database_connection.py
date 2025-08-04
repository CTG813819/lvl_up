#!/usr/bin/env python3
"""
Test database connection for Railway deployment
"""

import os
import asyncio
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Set the database URL
DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

async def test_database_connection():
    """Test the database connection"""
    print("🔍 Testing database connection...")
    
    try:
        # Test with asyncpg directly
        print("📦 Testing asyncpg connection...")
        conn = await asyncpg.connect(
            "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
        )
        
        # Test a simple query
        result = await conn.fetchval("SELECT version()")
        print(f"✅ Database connection successful!")
        print(f"📄 PostgreSQL version: {result}")
        
        await conn.close()
        
        # Test with SQLAlchemy
        print("\n📦 Testing SQLAlchemy connection...")
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            print("✅ SQLAlchemy connection successful!")
        
        await engine.dispose()
        
        print("\n🎯 Database connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_app_startup():
    """Test if the app can start with the database"""
    print("\n🔍 Testing app startup...")
    
    try:
        # Set environment variable
        os.environ["DATABASE_URL"] = DATABASE_URL
        
        # Try to import and start the app
        from app.main import app
        print("✅ App import successful!")
        
        # Test a simple endpoint
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.get("/health")
        print(f"✅ Health endpoint: {response.status_code}")
        
        if response.status_code == 200:
            print("🎯 App startup test passed!")
            return True
        else:
            print(f"⚠️ Health endpoint returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        return False

async def main():
    print("🚀 Railway Database Connection Test")
    print("=" * 50)
    
    # Test database connection
    db_success = await test_database_connection()
    
    if db_success:
        # Test app startup
        app_success = await test_app_startup()
        
        if app_success:
            print("\n✅ All tests passed! Ready for Railway deployment.")
            print("\n📋 Next Steps:")
            print("1. Add DATABASE_URL to Railway environment variables")
            print("2. Redeploy your Railway service")
            print("3. Test the endpoints")
        else:
            print("\n❌ App startup failed. Check the error above.")
    else:
        print("\n❌ Database connection failed. Check your connection string.")

if __name__ == "__main__":
    asyncio.run(main()) 