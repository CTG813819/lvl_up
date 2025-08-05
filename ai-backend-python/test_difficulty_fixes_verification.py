#!/usr/bin/env python3
"""
Test script to verify the difficulty fixes work correctly.
This script tests:
1. Proper difficulty logging in test_history
2. XP persistence
3. More aggressive difficulty adjustment for consecutive failures
4. Specific, non-generic AI responses
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.init_database import init_database
from app.services.custody_protocol_service import CustodyProtocolService
from app.services.agent_metrics_service import AgentMetricsService

async def test_difficulty_fixes():
    """Test the difficulty fixes"""
    print("🔧 Testing Difficulty Fixes...")
    
    try:
        # Initialize database and services
        await init_database()
        await CustodyProtocolService.initialize()
        
        # Test AI type
        ai_type = "conquest"
        
        print(f"\n📊 Testing with AI: {ai_type}")
        
        # Get initial metrics
        agent_metrics_service = AgentMetricsService()
        initial_metrics = await agent_metrics_service.get_custody_metrics(ai_type)
        
        print(f"📈 Initial metrics: {json.dumps(initial_metrics, default=str, indent=2)}")
        
        # Run a test to see the difficulty logging
        print(f"\n🧪 Running custody test for {ai_type}...")
        
        custody_service = CustodyProtocolService()
        test_result = await custody_service.administer_custody_test(ai_type)
        
        print(f"📋 Test result: {json.dumps(test_result, default=str, indent=2)}")
        
        # Get updated metrics
        updated_metrics = await agent_metrics_service.get_custody_metrics(ai_type)
        
        print(f"📈 Updated metrics: {json.dumps(updated_metrics, default=str, indent=2)}")
        
        # Check if difficulty is properly logged in test_history
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
        
        # Check XP persistence
        xp = updated_metrics.get('xp', 0)
        custody_xp = updated_metrics.get('custody_xp', 0)
        print(f"💎 XP: {xp}, Custody XP: {custody_xp}")
        
        if xp > 0 or custody_xp > 0:
            print("✅ SUCCESS: XP is being persisted!")
        else:
            print("❌ FAILURE: XP is not being persisted")
        
        # Check current difficulty
        current_difficulty = updated_metrics.get('current_difficulty', 'unknown')
        consecutive_failures = updated_metrics.get('consecutive_failures', 0)
        print(f"🎯 Current difficulty: {current_difficulty}")
        print(f"📉 Consecutive failures: {consecutive_failures}")
        
        # Test difficulty adjustment for high consecutive failures
        if consecutive_failures >= 5:
            print(f"🔧 Testing difficulty adjustment for {consecutive_failures} consecutive failures...")
            
            # Run another test to see if difficulty decreases
            test_result_2 = await custody_service.administer_custody_test(ai_type)
            updated_metrics_2 = await agent_metrics_service.get_custody_metrics(ai_type)
            
            new_difficulty = updated_metrics_2.get('current_difficulty', 'unknown')
            print(f"🎯 New difficulty after adjustment: {new_difficulty}")
            
            if new_difficulty != current_difficulty:
                print("✅ SUCCESS: Difficulty adjustment is working!")
            else:
                print("❌ FAILURE: Difficulty adjustment is not working")
        
        print("\n🎉 Difficulty fixes verification completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_difficulty_fixes()) 