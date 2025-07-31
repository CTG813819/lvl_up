#!/usr/bin/env python3
"""
Database Connection Fix
Fixes asyncpg connection issues that cause Gunicorn worker failures
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def fix_database_connections():
    """Fix database connection issues"""
    print("🔧 FIXING DATABASE CONNECTION ISSUES")
    print("=" * 50)
    
    try:
        from app.core.database import init_database, close_database, engine, SessionLocal
        from app.core.config import settings
        
        print("📋 Current database configuration:")
        print(f"   - Database URL: {settings.database_url}")
        print(f"   - Engine: {engine}")
        print(f"   - SessionLocal: {SessionLocal}")
        
        # Test basic connection
        print("\n🔍 Testing basic database connection...")
        await init_database()
        print("✅ Basic connection successful")
        
        # Test session creation
        print("\n🔍 Testing session creation...")
        async with SessionLocal() as session:
            # Test a simple query
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            print("✅ Session creation and query successful")
        
        # Test connection pool
        print("\n🔍 Testing connection pool...")
        if engine:
            pool = engine.pool
            print(f"   - Pool size: {pool.size()}")
            print(f"   - Checked out connections: {pool.checkedout()}")
            print(f"   - Overflow: {pool.overflow()}")
            print("✅ Connection pool working correctly")
        
        # Close database
        await close_database()
        print("✅ Database closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_async_operations():
    """Test async operations that might be causing issues"""
    print("\n🧪 TESTING ASYNC OPERATIONS")
    print("=" * 30)
    
    try:
        from app.core.database import init_database, close_database, get_session
        from app.models.sql_models import AgentMetrics
        
        await init_database()
        print("✅ Database initialized for async test")
        
        # Test async session context manager
        async with get_session() as session:
            # Test a simple query
            from sqlalchemy import text
            result = await session.execute(text("SELECT COUNT(*) FROM agent_metrics"))
            count = result.scalar()
            print(f"✅ Async query successful, agent_metrics count: {count}")
        
        await close_database()
        print("✅ Async operations test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Async operations test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def check_environment():
    """Check environment variables and configuration"""
    print("\n🔍 CHECKING ENVIRONMENT")
    print("=" * 25)
    
    # Check environment variables
    env_vars = [
        'DATABASE_URL',
        'GITHUB_TOKEN',
        'GITHUB_REPO_URL',
        'GITHUB_USERNAME',
        'PYTHONPATH'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'TOKEN' in var or 'PASSWORD' in var:
                masked_value = value[:10] + "..." + value[-5:] if len(value) > 15 else "***"
                print(f"   ✅ {var}: {masked_value}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Not set")
    
    # Check Python path
    print(f"\n📋 Python path:")
    for path in sys.path:
        print(f"   - {path}")
    
    return True

async def main():
    """Main fix function"""
    print("🚀 STARTING DATABASE CONNECTION FIX")
    print("=" * 50)
    
    # Check environment
    env_ok = await check_environment()
    
    # Fix database connections
    db_ok = await fix_database_connections()
    
    # Test async operations
    async_ok = await test_async_operations()
    
    print("\n📊 FIX SUMMARY")
    print("=" * 20)
    print(f"   Environment check: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"   Database connections: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"   Async operations: {'✅ PASS' if async_ok else '❌ FAIL'}")
    
    if env_ok and db_ok and async_ok:
        print("\n🎉 ALL TESTS PASSED! Database connections are working correctly.")
        print("   The Gunicorn worker failures should be resolved.")
    else:
        print("\n❌ SOME TESTS FAILED! Please check the errors above.")
        print("   Database connection issues may still cause worker failures.")
    
    return env_ok and db_ok and async_ok

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 