#!/usr/bin/env python3
"""
Database Connection Status Checker
Checks the current database connection pool status and health
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

async def check_database_status():
    """Check database connection status"""
    print("🔍 Checking Database Connection Status...")
    print("=" * 50)
    
    try:
        # Import database module
        from app.core.database import get_pool_status, init_database
        
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Initialize database connection
        print("📡 Initializing database connection...")
        await init_database()
        print("✅ Database connection initialized")
        print()
        
        # Get pool status
        print("📊 Getting connection pool status...")
        pool_status = await get_pool_status()
        
        if "error" in pool_status:
            print(f"❌ Error getting pool status: {pool_status['error']}")
            return
        
        print("📈 Connection Pool Statistics:")
        print(f"   Status: {pool_status.get('status', 'Unknown')}")
        print(f"   Engine Initialized: {pool_status.get('engine_initialized', False)}")
        print(f"   Circuit Breaker State: {pool_status.get('circuit_breaker_state', 'Unknown')}")
        print(f"   Circuit Breaker Failures: {pool_status.get('circuit_breaker_failures', 0)}")
        
        if 'pool_size' in pool_status:
            print(f"   Pool Size: {pool_status.get('pool_size', 0)}")
            print(f"   Checked In: {pool_status.get('pool_checked_in', 0)}")
            print(f"   Checked Out: {pool_status.get('pool_checked_out', 0)}")
            print(f"   Overflow: {pool_status.get('pool_overflow', 0)}")
            print(f"   Invalid: {pool_status.get('pool_invalid', 0)}")
            print(f"   Total Connections: {pool_status.get('total_connections', 0)}")
            print(f"   In Use Connections: {pool_status.get('in_use_connections', 0)}")
            print(f"   Available Connections: {pool_status.get('available_connections', 0)}")
            
            # Calculate usage percentage
            total = pool_status.get('total_connections', 0)
            in_use = pool_status.get('in_use_connections', 0)
            if total > 0:
                usage_percent = (in_use / total) * 100
                print(f"   Usage Percentage: {usage_percent:.1f}%")
                
                if usage_percent > 80:
                    print("   ⚠️  WARNING: High connection pool usage!")
                elif usage_percent > 60:
                    print("   ⚠️  CAUTION: Moderate connection pool usage")
                else:
                    print("   ✅ Connection pool usage is normal")
        else:
            print("   ℹ️  Detailed pool statistics not available")
        
        print()
        print("🔧 Configuration:")
        print("   Pool Size: 50 (increased from 25)")
        print("   Max Overflow: 100 (increased from 50)")
        print("   Pool Timeout: 120 seconds (increased from 60)")
        print("   LIFO Management: Enabled")
        print("   Statement Timeout: 120 seconds")
        print("   Idle Transaction Timeout: 300 seconds")
        
        print()
        print("✅ Database status check completed")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this script from the project root directory")
    except Exception as e:
        print(f"❌ Error checking database status: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_database_status()) 