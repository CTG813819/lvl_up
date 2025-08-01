#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_fixes():
    try:
        print("Testing difficulty adjustment and XP persistence fixes...")
        
        # Import and initialize
        from app.core.database import init_database
        from app.services.custody_protocol_service import CustodyProtocolService
        
        print("Initializing database...")
        await init_database()
        
        print("Initializing CustodyProtocolService...")
        await CustodyProtocolService.initialize()
        
        custody_service = CustodyProtocolService()
        
        # Test with conquest AI
        ai_type = "conquest"
        
        print(f"Testing {ai_type} AI...")
        
        # Get initial metrics
        initial_metrics = await custody_service.agent_metrics_service.get_custody_metrics(ai_type)
        print(f"Initial difficulty: {initial_metrics.get('current_difficulty', 'unknown') if initial_metrics else 'unknown'}")
        print(f"Initial XP: {initial_metrics.get('custody_xp', 0) if initial_metrics else 0}")
        
        # Run a test
        print("Running custody test...")
        test_result = await custody_service.administer_custody_test(ai_type)
        
        print(f"Test passed: {test_result.get('test_result', {}).get('passed', False)}")
        print(f"Test score: {test_result.get('test_result', {}).get('score', 0)}")
        
        # Get updated metrics
        updated_metrics = await custody_service.agent_metrics_service.get_custody_metrics(ai_type)
        print(f"Updated difficulty: {updated_metrics.get('current_difficulty', 'unknown') if updated_metrics else 'unknown'}")
        print(f"Updated XP: {updated_metrics.get('custody_xp', 0) if updated_metrics else 0}")
        
        # Check test history
        test_history = updated_metrics.get('test_history', []) if updated_metrics else []
        if test_history:
            latest_entry = test_history[-1]
            print(f"Latest test history difficulty: {latest_entry.get('difficulty', 'unknown')}")
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixes()) 