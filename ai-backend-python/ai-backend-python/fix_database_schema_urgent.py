#!/usr/bin/env python3
"""
Urgent Database Schema Fix
Fixes the missing 'xp' attribute that's preventing AIs from taking tests
"""

import asyncio
import sys
import os

# Add the ai-backend-python directory to the path
sys.path.append('/home/ubuntu/ai-backend-python')

async def fix_agent_learning_metrics():
    """Fix the AgentLearningMetrics table schema"""
    try:
        print("🔧 Fixing AgentLearningMetrics database schema...")
        
        from app.core.database import get_session
        from sqlalchemy import text
        
        session = get_session()
        async with session as s:
            # Check if xp column exists in agent_learning_metrics
            result = await s.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'agent_learning_metrics' 
                AND column_name = 'xp'
            """))
            
            if not result.fetchone():
                print("  📝 Adding missing columns to agent_learning_metrics table...")
                
                # Add all missing columns
                columns_to_add = [
                    "ALTER TABLE agent_learning_metrics ADD COLUMN IF NOT EXISTS xp INTEGER DEFAULT 0",
                    "ALTER TABLE agent_learning_metrics ADD COLUMN IF NOT EXISTS level INTEGER DEFAULT 1",
                    "ALTER TABLE agent_learning_metrics ADD COLUMN IF NOT EXISTS total_tests_given INTEGER DEFAULT 0",
                    "ALTER TABLE agent_learning_metrics ADD COLUMN IF NOT EXISTS total_tests_passed INTEGER DEFAULT 0",
                    "ALTER TABLE agent_learning_metrics ADD COLUMN IF NOT EXISTS total_tests_failed INTEGER DEFAULT 0",
                    "ALTER TABLE agent_learning_metrics ADD COLUMN IF NOT EXISTS consecutive_successes INTEGER DEFAULT 0",
                    "ALTER TABLE agent_learning_metrics ADD COLUMN IF NOT EXISTS consecutive_failures INTEGER DEFAULT 0",
                    "ALTER TABLE agent_learning_metrics ADD COLUMN IF NOT EXISTS last_test_date TIMESTAMP",
                    "ALTER TABLE agent_learning_metrics ADD COLUMN IF NOT EXISTS test_history JSONB DEFAULT '[]'::jsonb"
                ]
                
                for column_sql in columns_to_add:
                    try:
                        await s.execute(text(column_sql))
                        print(f"    ✅ Added column: {column_sql.split()[-1]}")
                    except Exception as e:
                        print(f"    ⚠️ Column might already exist: {str(e)}")
                
                await s.commit()
                print("  ✅ Database schema updated successfully")
            else:
                print("  ✅ Database schema already correct")
                
            # Update existing records to have default values
            print("  🔄 Updating existing records with default values...")
            await s.execute(text("""
                UPDATE agent_learning_metrics 
                SET xp = COALESCE(xp, 0),
                    level = COALESCE(level, 1),
                    total_tests_given = COALESCE(total_tests_given, 0),
                    total_tests_passed = COALESCE(total_tests_passed, 0),
                    total_tests_failed = COALESCE(total_tests_failed, 0),
                    consecutive_successes = COALESCE(consecutive_successes, 0),
                    consecutive_failures = COALESCE(consecutive_failures, 0),
                    test_history = COALESCE(test_history, '[]'::jsonb)
                WHERE xp IS NULL OR level IS NULL
            """))
            await s.commit()
            print("  ✅ Existing records updated")
                
    except Exception as e:
        print(f"  ❌ Error fixing database schema: {str(e)}")
        raise

async def check_ai_test_status():
    """Check if AIs are actually taking tests"""
    try:
        print("\n🧪 Checking AI Test Status...")
        
        from app.services.custody_protocol_service import CustodyProtocolService
        
        # Initialize the service
        service = await CustodyProtocolService.initialize()
        
        print("  📊 Current AI Test Metrics:")
        print("  " + "-" * 50)
        
        for ai_type, metrics in service.custody_metrics.items():
            print(f"  {ai_type.upper()}:")
            print(f"    XP: {metrics['custody_xp']}")
            print(f"    Level: {metrics['custody_level']}")
            print(f"    Tests Given: {metrics['total_tests_given']}")
            print(f"    Tests Passed: {metrics['total_tests_passed']}")
            print(f"    Tests Failed: {metrics['total_tests_failed']}")
            print(f"    Pass Rate: {(metrics['total_tests_passed'] / max(metrics['total_tests_given'], 1) * 100):.1f}%")
            print(f"    Can Level Up: {metrics['can_level_up']}")
            print(f"    Can Create Proposals: {metrics['can_create_proposals']}")
            print(f"    Last Test: {metrics.get('last_test_date', 'Never')}")
            print()
        
        # Check if tests are actually being administered
        print("  🔍 Test Administration Status:")
        print("  " + "-" * 50)
        
        # Check if the custody service is properly configured
        if hasattr(service, 'test_scheduler'):
            print("    ✅ Test scheduler is configured")
        else:
            print("    ⚠️ Test scheduler not found")
        
        # Check if test categories are available
        if hasattr(service, 'test_categories'):
            print(f"    ✅ {len(service.test_categories)} test categories available")
        else:
            print("    ⚠️ Test categories not found")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error checking AI test status: {str(e)}")
        return False

async def trigger_test_for_ai(ai_type: str):
    """Trigger a test for a specific AI to verify functionality"""
    try:
        print(f"\n🎯 Triggering test for {ai_type.upper()}...")
        
        from app.services.custody_protocol_service import CustodyProtocolService
        from app.services.custody_protocol_service import TestCategory
        
        # Initialize the service
        service = await CustodyProtocolService.initialize()
        
        # Trigger a test
        test_result = await service.administer_custody_test(
            ai_type=ai_type,
            test_category=TestCategory.KNOWLEDGE_VERIFICATION
        )
        
        print(f"  📝 Test Result for {ai_type.upper()}:")
        print(f"    Passed: {test_result.get('passed', False)}")
        print(f"    Score: {test_result.get('score', 0)}")
        print(f"    Duration: {test_result.get('duration', 0)} seconds")
        print(f"    Category: {test_result.get('category', 'Unknown')}")
        
        return test_result
        
    except Exception as e:
        print(f"  ❌ Error triggering test for {ai_type}: {str(e)}")
        return None

async def main():
    """Main function"""
    print("🚀 Starting Urgent Database Schema Fix...")
    print("=" * 60)
    
    # Fix the database schema
    await fix_agent_learning_metrics()
    
    # Check AI test status
    await check_ai_test_status()
    
    # Trigger a test for Imperium to verify functionality
    print("\n🎯 Testing AI Test Functionality...")
    test_result = await trigger_test_for_ai("imperium")
    
    if test_result:
        print("\n✅ AI Test System is Working!")
        print("🎉 AIs can now take tests and receive XP rewards!")
    else:
        print("\n❌ AI Test System needs further investigation")
    
    print("\n" + "=" * 60)
    print("🔧 Database schema fix completed!")
    print("📊 Check the logs above for AI test status")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 