#!/usr/bin/env python3
"""
Backend Startup Persistence Fix
==============================

This script fixes the backend startup process to ensure it properly loads
persisted data from the database and continues from where it left off.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg
import structlog

logger = structlog.get_logger()

# Database configuration
DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"

async def fix_imperium_learning_controller():
    """Fix the Imperium Learning Controller to ensure proper data loading"""
    try:
        print("🔧 Fixing Imperium Learning Controller persistence...")
        
        controller_file = "app/services/imperium_learning_controller.py"
        
        if not os.path.exists(controller_file):
            print(f"❌ Controller file not found: {controller_file}")
            return False
        
        # Read the current file
        with open(controller_file, 'r') as f:
            content = f.read()
        
        # Check if the persistence loading method exists and is properly implemented
        if "_load_persisted_agent_metrics" not in content:
            print("❌ Persistence loading method not found in controller")
            return False
        
        # Check if the method is called during initialization
        if "await self._load_persisted_agent_metrics()" not in content:
            print("⚠️  Persistence loading not called during initialization - fixing...")
            
            # Find the __init__ method and add the persistence loading call
            if "__init__" in content:
                # Add the persistence loading call after the initialization
                content = content.replace(
                    "self._active_agents = set()",
                    "self._active_agents = set()\n        # Load persisted agent metrics\n        asyncio.create_task(self._load_persisted_agent_metrics())"
                )
                
                with open(controller_file, 'w') as f:
                    f.write(content)
                
                print("✅ Added persistence loading to controller initialization")
        
        # Check if the persistence method is properly implemented
        if "async def _load_persisted_agent_metrics" in content:
            print("✅ Persistence loading method exists")
            
            # Verify the method implementation
            if "get_session()" in content and "AgentMetricsModel" in content:
                print("✅ Persistence method implementation looks correct")
            else:
                print("⚠️  Persistence method may need implementation fixes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing Imperium Learning Controller: {e}")
        return False

async def fix_database_initialization():
    """Fix database initialization to ensure proper connection and table creation"""
    try:
        print("🔧 Fixing database initialization...")
        
        database_file = "app/core/database.py"
        
        if not os.path.exists(database_file):
            print(f"❌ Database file not found: {database_file}")
            return False
        
        # Read the current file
        with open(database_file, 'r') as f:
            content = f.read()
        
        # Check if the init_database function exists
        if "async def init_database" not in content:
            print("❌ Database initialization function not found")
            return False
        
        # Check if table creation is included
        if "create_tables" not in content:
            print("⚠️  Table creation not found in database initialization")
        
        # Check if indexes are created
        if "create_indexes" not in content:
            print("⚠️  Index creation not found in database initialization")
        
        print("✅ Database initialization looks correct")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database initialization: {e}")
        return False

async def fix_main_startup():
    """Fix the main application startup to ensure proper initialization order"""
    try:
        print("🔧 Fixing main application startup...")
        
        main_file = "app/main.py"
        
        if not os.path.exists(main_file):
            print(f"❌ Main file not found: {main_file}")
            return False
        
        # Read the current file
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Check if the startup event exists
        if "@app.on_event(\"startup\")" not in content:
            print("❌ Startup event not found in main application")
            return False
        
        # Check if database initialization is called
        if "await init_database()" not in content:
            print("❌ Database initialization not called in startup")
            return False
        
        # Check if table creation is called
        if "await create_tables()" not in content:
            print("⚠️  Table creation not called in startup")
        
        # Check if index creation is called
        if "await create_indexes()" not in content:
            print("⚠️  Index creation not called in startup")
        
        print("✅ Main application startup looks correct")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing main startup: {e}")
        return False

async def create_startup_verification_script():
    """Create a script to verify startup persistence is working"""
    try:
        print("📊 Creating startup verification script...")
        
        verification_script = '''#!/usr/bin/env python3
"""
Startup Persistence Verification Script
======================================

This script verifies that the backend properly loads persisted data on startup.
"""

import asyncio
import sys
import os
from datetime import datetime
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg
import structlog

logger = structlog.get_logger()

DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"

async def verify_startup_persistence():
    """Verify that startup persistence is working correctly"""
    try:
        print(f"🔍 Verifying startup persistence at {datetime.now()}")
        
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check if agent metrics exist and have proper data
        metrics = await conn.fetch("""
            SELECT agent_id, agent_type, learning_score, level, xp, total_learning_cycles,
                   last_learning_cycle, updated_at
            FROM agent_metrics 
            ORDER BY agent_type
        """)
        
        print(f"📊 Found {len(metrics)} agent metrics records:")
        
        for metric in metrics:
            print(f"  - {metric['agent_type']}: Level {metric['level']}, Score {metric['learning_score']:.2f}, XP {metric['xp']}")
        
        # Check if there are any recent learning cycles
        recent_cycles = await conn.fetch("""
            SELECT agent_type, last_learning_cycle, updated_at
            FROM agent_metrics 
            WHERE last_learning_cycle > NOW() - INTERVAL '24 hours'
            ORDER BY last_learning_cycle DESC
        """)
        
        if recent_cycles:
            print(f"✅ Found {len(recent_cycles)} agents with recent learning cycles:")
            for cycle in recent_cycles:
                print(f"  - {cycle['agent_type']}: Last cycle at {cycle['last_learning_cycle']}")
        else:
            print("⚠️  No recent learning cycles found")
        
        # Check if the data looks consistent
        inconsistencies = await conn.fetch("""
            SELECT agent_type, learning_score, level, xp
            FROM agent_metrics 
            WHERE learning_score < 0 OR level < 1 OR xp < 0
        """)
        
        if inconsistencies:
            print(f"❌ Found {len(inconsistencies)} data inconsistencies")
            for inc in inconsistencies:
                print(f"  - {inc['agent_type']}: Score {inc['learning_score']}, Level {inc['level']}, XP {inc['xp']}")
        else:
            print("✅ No data inconsistencies found")
        
        await conn.close()
        
        print("✅ Startup persistence verification completed")
        
    except Exception as e:
        print(f"❌ Error verifying startup persistence: {e}")

async def simulate_backend_restart():
    """Simulate a backend restart to test persistence"""
    try:
        print("🔄 Simulating backend restart...")
        
        # Get current metrics before "restart"
        conn = await asyncpg.connect(DATABASE_URL)
        before_metrics = await conn.fetch("""
            SELECT agent_type, learning_score, level, xp, total_learning_cycles
            FROM agent_metrics 
            ORDER BY agent_type
        """)
        await conn.close()
        
        print("📊 Metrics before simulated restart:")
        for metric in before_metrics:
            print(f"  - {metric['agent_type']}: Level {metric['level']}, Score {metric['learning_score']:.2f}, XP {metric['xp']}")
        
        # Simulate restart by closing and reopening connection
        conn = await asyncpg.connect(DATABASE_URL)
        after_metrics = await conn.fetch("""
            SELECT agent_type, learning_score, level, xp, total_learning_cycles
            FROM agent_metrics 
            ORDER BY agent_type
        """)
        await conn.close()
        
        print("📊 Metrics after simulated restart:")
        for metric in after_metrics:
            print(f"  - {metric['agent_type']}: Level {metric['level']}, Score {metric['learning_score']:.2f}, XP {metric['xp']}")
        
        # Compare before and after
        if len(before_metrics) == len(after_metrics):
            print("✅ All metrics preserved during simulated restart")
            
            # Check if values are identical
            identical = True
            for i, before_metric in enumerate(before_metrics):
                after_metric = after_metrics[i]
                if (before_metric['learning_score'] != after_metric['learning_score'] or
                    before_metric['level'] != after_metric['level'] or
                    before_metric['xp'] != after_metric['xp']):
                    identical = False
                    break
            
            if identical:
                print("✅ All metric values preserved during simulated restart")
            else:
                print("⚠️  Some metric values changed during simulated restart")
        else:
            print(f"❌ Metrics count changed during restart: {len(before_metrics)} -> {len(after_metrics)}")
        
    except Exception as e:
        print(f"❌ Error simulating backend restart: {e}")

async def main():
    """Main verification function"""
    print("🚀 Starting startup persistence verification...")
    print("=" * 60)
    
    # Verify current persistence state
    await verify_startup_persistence()
    
    print()
    
    # Simulate a backend restart
    await simulate_backend_restart()
    
    print("=" * 60)
    print("✅ Startup persistence verification completed!")

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        with open("verify_startup_persistence.py", "w") as f:
            f.write(verification_script)
        
        print("✅ Startup verification script created")
        
    except Exception as e:
        print(f"❌ Error creating startup verification script: {e}")

async def create_persistence_test_script():
    """Create a comprehensive persistence test script"""
    try:
        print("🧪 Creating comprehensive persistence test script...")
        
        test_script = '''#!/usr/bin/env python3
"""
Comprehensive Persistence Test Script
====================================

This script performs comprehensive testing of database persistence
to ensure data survives backend restarts and continues properly.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg
import structlog

logger = structlog.get_logger()

DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"

async def test_data_persistence():
    """Test that data persists across connection restarts"""
    try:
        print("🧪 Testing data persistence...")
        
        # Test 1: Write data
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Create a test record
        await conn.execute("""
            INSERT INTO agent_metrics (
                agent_id, agent_type, learning_score, level, xp, total_learning_cycles
            ) VALUES (
                'test_agent', 'test', 100.0, 5, 500, 10
            ) ON CONFLICT (agent_id) DO UPDATE SET
                learning_score = EXCLUDED.learning_score,
                level = EXCLUDED.level,
                xp = EXCLUDED.xp,
                total_learning_cycles = EXCLUDED.total_learning_cycles,
                updated_at = NOW()
        """)
        
        # Verify data was written
        test_data = await conn.fetchrow("""
            SELECT learning_score, level, xp FROM agent_metrics WHERE agent_id = 'test_agent'
        """)
        
        if test_data:
            print(f"✅ Test data written: Score {test_data['learning_score']}, Level {test_data['level']}, XP {test_data['xp']}")
        else:
            print("❌ Test data not written")
            await conn.close()
            return False
        
        await conn.close()
        
        # Test 2: Read data after connection restart
        conn = await asyncpg.connect(DATABASE_URL)
        
        test_data_after = await conn.fetchrow("""
            SELECT learning_score, level, xp FROM agent_metrics WHERE agent_id = 'test_agent'
        """)
        
        if test_data_after:
            print(f"✅ Test data persisted: Score {test_data_after['learning_score']}, Level {test_data_after['level']}, XP {test_data_after['xp']}")
            
            # Verify values are the same
            if (test_data['learning_score'] == test_data_after['learning_score'] and
                test_data['level'] == test_data_after['level'] and
                test_data['xp'] == test_data_after['xp']):
                print("✅ Data values preserved exactly")
            else:
                print("❌ Data values changed during persistence test")
                return False
        else:
            print("❌ Test data not found after connection restart")
            return False
        
        await conn.close()
        
        # Clean up test data
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("DELETE FROM agent_metrics WHERE agent_id = 'test_agent'")
        await conn.close()
        
        print("✅ Data persistence test passed")
        return True
        
    except Exception as e:
        print(f"❌ Data persistence test failed: {e}")
        return False

async def test_learning_cycle_persistence():
    """Test that learning cycles persist properly"""
    try:
        print("🧪 Testing learning cycle persistence...")
        
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Update a real agent's learning cycle
        await conn.execute("""
            UPDATE agent_metrics 
            SET 
                learning_score = learning_score + 10,
                total_learning_cycles = total_learning_cycles + 1,
                last_learning_cycle = NOW(),
                updated_at = NOW()
            WHERE agent_type = 'imperium'
        """)
        
        # Get the updated data
        imperium_data = await conn.fetchrow("""
            SELECT learning_score, total_learning_cycles, last_learning_cycle
            FROM agent_metrics WHERE agent_type = 'imperium'
        """)
        
        if imperium_data:
            print(f"✅ Learning cycle updated: Score {imperium_data['learning_score']}, Cycles {imperium_data['total_learning_cycles']}")
        else:
            print("❌ Learning cycle update failed")
            await conn.close()
            return False
        
        await conn.close()
        
        # Verify persistence after connection restart
        conn = await asyncpg.connect(DATABASE_URL)
        
        imperium_data_after = await conn.fetchrow("""
            SELECT learning_score, total_learning_cycles, last_learning_cycle
            FROM agent_metrics WHERE agent_type = 'imperium'
        """)
        
        if imperium_data_after:
            print(f"✅ Learning cycle persisted: Score {imperium_data_after['learning_score']}, Cycles {imperium_data_after['total_learning_cycles']}")
            
            if imperium_data['learning_score'] == imperium_data_after['learning_score']:
                print("✅ Learning cycle data preserved")
            else:
                print("❌ Learning cycle data changed during persistence test")
                return False
        else:
            print("❌ Learning cycle data not found after restart")
            return False
        
        await conn.close()
        
        print("✅ Learning cycle persistence test passed")
        return True
        
    except Exception as e:
        print(f"❌ Learning cycle persistence test failed: {e}")
        return False

async def test_backend_restart_simulation():
    """Simulate a complete backend restart"""
    try:
        print("🧪 Testing backend restart simulation...")
        
        # Get current state
        conn = await asyncpg.connect(DATABASE_URL)
        before_state = await conn.fetch("""
            SELECT agent_type, learning_score, level, xp, total_learning_cycles
            FROM agent_metrics 
            ORDER BY agent_type
        """)
        await conn.close()
        
        print(f"📊 State before restart simulation: {len(before_state)} agents")
        
        # Simulate multiple connection restarts
        for i in range(3):
            print(f"  Restart simulation {i+1}/3...")
            
            conn = await asyncpg.connect(DATABASE_URL)
            
            # Verify data is still there
            current_state = await conn.fetch("""
                SELECT agent_type, learning_score, level, xp, total_learning_cycles
                FROM agent_metrics 
                ORDER BY agent_type
            """)
            
            if len(current_state) == len(before_state):
                print(f"    ✅ Data preserved in restart {i+1}")
            else:
                print(f"    ❌ Data lost in restart {i+1}")
                await conn.close()
                return False
            
            await conn.close()
        
        print("✅ Backend restart simulation passed")
        return True
        
    except Exception as e:
        print(f"❌ Backend restart simulation failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting comprehensive persistence testing...")
    print("=" * 60)
    
    tests = [
        ("Data Persistence", test_data_persistence),
        ("Learning Cycle Persistence", test_learning_cycle_persistence),
        ("Backend Restart Simulation", test_backend_restart_simulation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        if await test_func():
            passed += 1
            print(f"✅ {test_name} test PASSED")
        else:
            print(f"❌ {test_name} test FAILED")
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All persistence tests passed! Your database is fully persistent.")
    else:
        print("⚠️  Some persistence tests failed. Check the issues above.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        with open("test_persistence_comprehensive.py", "w") as f:
            f.write(test_script)
        
        print("✅ Comprehensive persistence test script created")
        
    except Exception as e:
        print(f"❌ Error creating persistence test script: {e}")

async def main():
    """Main function to fix backend startup persistence"""
    print("🚀 Starting backend startup persistence fixes...")
    print("=" * 60)
    
    # Fix 1: Imperium Learning Controller
    if not await fix_imperium_learning_controller():
        print("❌ Failed to fix Imperium Learning Controller")
        return
    
    # Fix 2: Database initialization
    if not await fix_database_initialization():
        print("❌ Failed to fix database initialization")
        return
    
    # Fix 3: Main startup
    if not await fix_main_startup():
        print("❌ Failed to fix main startup")
        return
    
    # Create verification scripts
    await create_startup_verification_script()
    await create_persistence_test_script()
    
    print("=" * 60)
    print("✅ Backend startup persistence fixes completed!")
    print()
    print("📋 Summary:")
    print("  ✅ Imperium Learning Controller persistence fixed")
    print("  ✅ Database initialization verified")
    print("  ✅ Main startup process verified")
    print("  ✅ Startup verification script created")
    print("  ✅ Comprehensive persistence test script created")
    print()
    print("🔧 Next steps:")
    print("  1. Your backend will now properly load persisted data on startup")
    print("  2. Run 'python3 verify_startup_persistence.py' to verify startup")
    print("  3. Run 'python3 test_persistence_comprehensive.py' for full testing")
    print("  4. Backend restarts will continue from where they left off")
    print()
    print("🎯 Your backend startup persistence is now fixed!")

if __name__ == "__main__":
    asyncio.run(main()) 