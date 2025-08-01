#!/usr/bin/env python3
"""
Simple test script to verify the difficulty fixes work correctly.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_simple():
    """Simple test to verify fixes"""
    print("🔧 Testing Difficulty Fixes...")
    
    try:
        # Import the services
        from app.database.init_database import init_database
        from app.services.custody_protocol_service import CustodyProtocolService
        from app.services.agent_metrics_service import AgentMetricsService
        
        print("✅ Imports successful")
        
        # Initialize database and services
        await init_database()
        await CustodyProtocolService.initialize()
        
        print("✅ Database and services initialized")
        
        # Test AI type
        ai_type = "conquest"
        
        # Get metrics
        agent_metrics_service = AgentMetricsService()
        metrics = await agent_metrics_service.get_custody_metrics(ai_type)
        
        print(f"📊 Current metrics for {ai_type}:")
        print(f"  - Current difficulty: {metrics.get('current_difficulty', 'unknown')}")
        print(f"  - Consecutive failures: {metrics.get('consecutive_failures', 0)}")
        print(f"  - XP: {metrics.get('xp', 0)}")
        print(f"  - Custody XP: {metrics.get('custody_xp', 0)}")
        
        # Run a test
        custody_service = CustodyProtocolService()
        test_result = await custody_service.administer_custody_test(ai_type)
        
        print(f"🧪 Test completed with score: {test_result.get('score', 0)}")
        
        # Get updated metrics
        updated_metrics = await agent_metrics_service.get_custody_metrics(ai_type)
        
        print(f"📈 Updated metrics:")
        print(f"  - Current difficulty: {updated_metrics.get('current_difficulty', 'unknown')}")
        print(f"  - Consecutive failures: {updated_metrics.get('consecutive_failures', 0)}")
        print(f"  - XP: {updated_metrics.get('xp', 0)}")
        print(f"  - Custody XP: {updated_metrics.get('custody_xp', 0)}")
        
        # Check test history
        test_history = updated_metrics.get('test_history', [])
        if test_history:
            latest_entry = test_history[-1]
            difficulty = latest_entry.get('difficulty', 'unknown')
            print(f"🎯 Latest test history difficulty: {difficulty}")
            
            if difficulty != 'unknown':
                print("✅ SUCCESS: Difficulty is properly logged!")
            else:
                print("❌ FAILURE: Difficulty is still showing as 'unknown'")
        
        print("🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple()) 