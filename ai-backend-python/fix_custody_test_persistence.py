#!/usr/bin/env python3
"""
Comprehensive fix for custody protocol test result persistence
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.custody_protocol_service import CustodyProtocolService
from app.core.database import init_database, get_session
from app.models.sql_models import AgentMetrics
from sqlalchemy import select
import structlog

logger = structlog.get_logger()

async def fix_custody_test_persistence():
    """Fix custody test result persistence by ensuring all metrics are stored in database"""
    try:
        print("🔧 Fixing custody test result persistence...")
        
        # Initialize database
        await init_database()
        
        # Initialize custody service
        custody_service = await CustodyProtocolService.initialize()
        
        # Test AI types
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            print(f"\n📊 Fixing {ai_type} AI custody persistence...")
            
            # Get current custody metrics from memory
            custody_metrics = custody_service.custody_metrics.get(ai_type, {})
            
            # Get current database metrics
            async with get_session() as session:
                result = await session.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == ai_type)
                )
                db_metrics = result.scalar_one_or_none()
                
                if db_metrics:
                    print(f"  Current DB metrics: XP={db_metrics.xp}, Level={db_metrics.level}")
                    
                    # Update database with custody metrics
                    db_metrics.xp = custody_metrics.get("custody_xp", 0)
                    db_metrics.level = custody_metrics.get("custody_level", 1)
                    db_metrics.updated_at = datetime.utcnow()
                    
                    # Add custody-specific fields to learning_patterns if it exists
                    if not db_metrics.learning_patterns:
                        db_metrics.learning_patterns = {}
                    
                    custody_data = {
                        "total_tests_given": custody_metrics.get("total_tests_given", 0),
                        "total_tests_passed": custody_metrics.get("total_tests_passed", 0),
                        "total_tests_failed": custody_metrics.get("total_tests_failed", 0),
                        "consecutive_successes": custody_metrics.get("consecutive_successes", 0),
                        "consecutive_failures": custody_metrics.get("consecutive_failures", 0),
                        "current_difficulty": custody_metrics.get("current_difficulty", "basic"),
                        "last_test_date": custody_metrics.get("last_test_date"),
                        "test_history": custody_metrics.get("test_history", [])
                    }
                    
                    db_metrics.learning_patterns["custody_metrics"] = custody_data
                    
                    await session.commit()
                    print(f"  ✅ Updated {ai_type} custody metrics in database")
                else:
                    print(f"  ❌ No database metrics found for {ai_type}")
        
        print("\n🎯 Custody test persistence fix completed!")
        
    except Exception as e:
        print(f"❌ Error fixing custody test persistence: {str(e)}")
        logger.error(f"Error fixing custody test persistence: {str(e)}")

async def test_custody_persistence():
    """Test that custody metrics are properly persisted and loaded"""
    try:
        print("\n🧪 Testing custody persistence...")
        
        # Initialize custody service
        custody_service = await CustodyProtocolService.initialize()
        
        # Test AI types
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            print(f"\n📊 Testing {ai_type} AI...")
            
            # Get analytics
            analytics = await custody_service.get_custody_analytics()
            ai_metrics = analytics.get("ai_specific_metrics", {}).get(ai_type, {})
            
            print(f"  Analytics XP: {ai_metrics.get('custody_xp', 0)}")
            print(f"  Analytics Level: {ai_metrics.get('custody_level', 1)}")
            print(f"  Tests Given: {ai_metrics.get('total_tests_given', 0)}")
            print(f"  Tests Passed: {ai_metrics.get('total_tests_passed', 0)}")
            
            # Force a test to generate metrics
            print(f"  Running test for {ai_type}...")
            test_result = await custody_service.force_custody_test(ai_type)
            
            if test_result.get("status") == "error":
                print(f"  ❌ Test failed: {test_result.get('message')}")
                continue
            
            # Get updated analytics
            updated_analytics = await custody_service.get_custody_analytics()
            updated_metrics = updated_analytics.get("ai_specific_metrics", {}).get(ai_type, {})
            
            print(f"  Updated XP: {updated_metrics.get('custody_xp', 0)}")
            print(f"  Updated Tests: {updated_metrics.get('total_tests_given', 0)}")
            
            # Reinitialize service to test persistence
            print(f"  Reinitializing service to test persistence...")
            custody_service2 = await CustodyProtocolService.initialize()
            
            # Get final analytics
            final_analytics = await custody_service2.get_custody_analytics()
            final_metrics = final_analytics.get("ai_specific_metrics", {}).get(ai_type, {})
            
            print(f"  Final XP: {final_metrics.get('custody_xp', 0)}")
            print(f"  Final Tests: {final_metrics.get('total_tests_given', 0)}")
            
            # Check if metrics persisted
            if final_metrics.get('total_tests_given', 0) > 0:
                print(f"  ✅ {ai_type} test results persisted successfully!")
            else:
                print(f"  ❌ {ai_type} test results did not persist!")
        
        print("\n🎯 Custody persistence test completed!")
        
    except Exception as e:
        print(f"❌ Error testing custody persistence: {str(e)}")
        logger.error(f"Error testing custody persistence: {str(e)}")

async def create_custody_metrics_table():
    """Create a dedicated custody metrics table for better persistence"""
    try:
        print("\n🗄️ Creating dedicated custody metrics table...")
        
        async with get_session() as session:
            # Create custody metrics table
            await session.execute("""
                CREATE TABLE IF NOT EXISTS custody_metrics (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    ai_type VARCHAR(50) NOT NULL UNIQUE,
                    total_tests_given INTEGER DEFAULT 0,
                    total_tests_passed INTEGER DEFAULT 0,
                    total_tests_failed INTEGER DEFAULT 0,
                    consecutive_successes INTEGER DEFAULT 0,
                    consecutive_failures INTEGER DEFAULT 0,
                    current_difficulty VARCHAR(20) DEFAULT 'basic',
                    custody_level INTEGER DEFAULT 1,
                    custody_xp INTEGER DEFAULT 0,
                    last_test_date TIMESTAMP,
                    test_history JSONB DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await session.execute("""
                CREATE INDEX IF NOT EXISTS idx_custody_metrics_ai_type ON custody_metrics(ai_type)
            """)
            
            await session.execute("""
                CREATE INDEX IF NOT EXISTS idx_custody_metrics_updated_at ON custody_metrics(updated_at DESC)
            """)
            
            await session.commit()
            print("✅ Custody metrics table created successfully!")
            
    except Exception as e:
        print(f"❌ Error creating custody metrics table: {str(e)}")
        logger.error(f"Error creating custody metrics table: {str(e)}")

async def main():
    """Main function"""
    print("🚀 Starting comprehensive custody persistence fix...")
    
    # Create dedicated table
    await create_custody_metrics_table()
    
    # Fix persistence
    await fix_custody_test_persistence()
    
    # Test persistence
    await test_custody_persistence()
    
    print("\n🎉 Comprehensive custody persistence fix completed!")

if __name__ == "__main__":
    asyncio.run(main()) 