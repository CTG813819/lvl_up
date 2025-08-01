#!/usr/bin/env python3
"""
Simple verification script for difficulty and XP fixes
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def verify_fixes():
    """Verify that the difficulty and XP fixes work correctly"""
    try:
        print("=== Verifying Difficulty and XP Fixes ===")
        
        # Import required modules
        from app.core.database import init_database
        from app.services.custody_protocol_service import CustodyProtocolService
        
        print("1. Initializing database...")
        await init_database()
        
        print("2. Initializing CustodyProtocolService...")
        await CustodyProtocolService.initialize()
        
        custody_service = CustodyProtocolService()
        
        # Test with conquest AI (which has 103+ consecutive failures)
        ai_type = "conquest"
        
        print(f"3. Testing {ai_type} AI...")
        
        # Get initial metrics
        initial_metrics = await custody_service.agent_metrics_service.get_custody_metrics(ai_type)
        
        if initial_metrics:
            print(f"   Initial difficulty: {initial_metrics.get('current_difficulty', 'unknown')}")
            print(f"   Initial XP: {initial_metrics.get('custody_xp', 0)}")
            print(f"   Consecutive failures: {initial_metrics.get('consecutive_failures', 0)}")
        else:
            print("   No initial metrics found")
        
        # Run a test
        print("4. Running custody test...")
        test_result = await custody_service.administer_custody_test(ai_type)
        
        print(f"   Test passed: {test_result.get('test_result', {}).get('passed', False)}")
        print(f"   Test score: {test_result.get('test_result', {}).get('score', 0)}")
        print(f"   Test difficulty: {test_result.get('test_difficulty', 'unknown')}")
        
        # Get updated metrics
        updated_metrics = await custody_service.agent_metrics_service.get_custody_metrics(ai_type)
        
        if updated_metrics:
            print(f"5. Updated metrics:")
            print(f"   Updated difficulty: {updated_metrics.get('current_difficulty', 'unknown')}")
            print(f"   Updated XP: {updated_metrics.get('custody_xp', 0)}")
            print(f"   Consecutive failures: {updated_metrics.get('consecutive_failures', 0)}")
            
            # Check if difficulty decreased
            initial_difficulty = initial_metrics.get('current_difficulty', 'basic') if initial_metrics else 'basic'
            updated_difficulty = updated_metrics.get('current_difficulty', 'basic')
            
            if initial_difficulty != updated_difficulty:
                print(f"   ✓ Difficulty changed: {initial_difficulty} -> {updated_difficulty}")
            else:
                print(f"   - Difficulty unchanged: {initial_difficulty}")
            
            # Check XP persistence
            initial_xp = initial_metrics.get('custody_xp', 0) if initial_metrics else 0
            updated_xp = updated_metrics.get('custody_xp', 0)
            
            if updated_xp > initial_xp:
                print(f"   ✓ XP increased: {initial_xp} -> {updated_xp}")
            else:
                print(f"   - XP unchanged: {initial_xp}")
            
            # Check test history
            test_history = updated_metrics.get('test_history', [])
            if test_history:
                latest_entry = test_history[-1]
                difficulty_in_history = latest_entry.get('difficulty', 'unknown')
                print(f"   Latest test history difficulty: {difficulty_in_history}")
                
                if difficulty_in_history != 'unknown':
                    print(f"   ✓ Test history shows correct difficulty: {difficulty_in_history}")
                else:
                    print(f"   - Test history shows unknown difficulty")
        else:
            print("   No updated metrics found")
        
        print("6. Verification completed!")
        
    except Exception as e:
        print(f"Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_fixes()) 