#!/usr/bin/env python3
"""
Test script to verify critical fixes:
1. DateTime import error fix
2. Difficulty adjustment for consecutive failures
3. Difficulty logging in test_history
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_critical_fixes():
    """Test the critical fixes"""
    print("🔧 Testing Critical Fixes...")
    
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
        
        # Get initial metrics
        agent_metrics_service = AgentMetricsService()
        initial_metrics = await agent_metrics_service.get_custody_metrics(ai_type)
        
        print(f"📊 Initial metrics for {ai_type}:")
        print(f"  - Current difficulty: {initial_metrics.get('current_difficulty', 'unknown')}")
        print(f"  - Consecutive failures: {initial_metrics.get('consecutive_failures', 0)}")
        print(f"  - XP: {initial_metrics.get('xp', 0)}")
        
        # Run a test to trigger the fixes
        custody_service = CustodyProtocolService()
        test_result = await custody_service.administer_custody_test(ai_type)
        
        print(f"🧪 Test completed with score: {test_result.get('score', 0)}")
        print(f"📋 Test result difficulty: {test_result.get('difficulty', 'unknown')}")
        
        # Get updated metrics
        updated_metrics = await agent_metrics_service.get_custody_metrics(ai_type)
        
        print(f"📈 Updated metrics:")
        print(f"  - Current difficulty: {updated_metrics.get('current_difficulty', 'unknown')}")
        print(f"  - Consecutive failures: {updated_metrics.get('consecutive_failures', 0)}")
        print(f"  - XP: {updated_metrics.get('xp', 0)}")
        
        # Check test history for difficulty logging
        test_history = updated_metrics.get('test_history', [])
        if test_history:
            latest_entry = test_history[-1]
            difficulty = latest_entry.get('difficulty', 'unknown')
            print(f"🎯 Latest test history difficulty: {difficulty}")
            
            if difficulty != 'unknown':
                print("✅ SUCCESS: Difficulty is properly logged!")
            else:
                print("❌ FAILURE: Difficulty is still showing as 'unknown'")
        else:
            print("❌ FAILURE: No test history found")
        
        # Check if difficulty adjustment is working
        consecutive_failures = updated_metrics.get('consecutive_failures', 0)
        current_difficulty = updated_metrics.get('current_difficulty', 'unknown')
        
        if consecutive_failures >= 3 and current_difficulty == 'basic':
            print("✅ SUCCESS: Difficulty adjustment is working!")
        elif consecutive_failures >= 3:
            print(f"❌ FAILURE: Difficulty should be 'basic' but is '{current_difficulty}' with {consecutive_failures} consecutive failures")
        else:
            print(f"ℹ️  INFO: Not enough consecutive failures ({consecutive_failures}) to test difficulty adjustment")
        
        print("🎉 Critical fixes test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_critical_fixes()) 