#!/usr/bin/env python3
"""
Test script to debug the Horus weapon synthesis endpoint
"""

import asyncio
import sys
sys.path.append('.')

from app.services.enhanced_project_horus_service import enhanced_project_horus_service

async def test_horus_endpoint():
    """Test the Horus weapon synthesis functionality"""
    
    try:
        print("🚀 Testing Enhanced Project Horus Service...")
        
        # Test 1: Check if service is initialized
        print("\n1. ✅ Service initialization check...")
        print(f"   Service type: {type(enhanced_project_horus_service)}")
        print(f"   Has ML models: {hasattr(enhanced_project_horus_service, 'ml_models')}")
        
        # Test 2: Test basic method calls
        print("\n2. 🧠 Testing learn_from_ai_experiences...")
        try:
            learning_result = await enhanced_project_horus_service.learn_from_ai_experiences(["imperium"])
            print(f"   Learning result: {learning_result}")
        except Exception as e:
            print(f"   ❌ Learning failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Test evolve_chaos_language
        print("\n3. 🔮 Testing evolve_chaos_language...")
        try:
            chaos_result = await enhanced_project_horus_service.evolve_chaos_language()
            print(f"   Chaos evolution result: {chaos_result}")
        except Exception as e:
            print(f"   ❌ Chaos evolution failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 4: Test get_weapon_synthesis_report
        print("\n4. ⚔️ Testing get_weapon_synthesis_report...")
        try:
            report = await enhanced_project_horus_service.get_weapon_synthesis_report()
            print(f"   Report keys: {list(report.keys())}")
            print(f"   Total weapons: {report.get('total_weapons', 0)}")
        except Exception as e:
            print(f"   ❌ Weapon synthesis report failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n✅ Horus endpoint test completed!")
        
    except Exception as e:
        print(f"\n❌ Horus endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_horus_endpoint())
    if not success:
        sys.exit(1)