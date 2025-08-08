#!/usr/bin/env python3
"""
Test script to check if enhanced testing endpoints are accessible
"""

import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_enhanced_endpoints():
    """Test if enhanced testing endpoints are working"""
    try:
        print("🧪 Testing Enhanced Testing Endpoints...")
        
        # Test import of the service
        try:
            from app.services.enhanced_testing_integration_service import enhanced_testing_integration_service
            print("✅ Enhanced testing integration service imported successfully")
        except Exception as e:
            print(f"❌ Failed to import enhanced testing service: {e}")
            return False
        
        # Test import of the router
        try:
            from app.routers.enhanced_testing_router import router
            print("✅ Enhanced testing router imported successfully")
        except Exception as e:
            print(f"❌ Failed to import enhanced testing router: {e}")
            return False
        
        # Test autonomous brain instances
        try:
            from app.services.autonomous_ai_brain_service import horus_autonomous_brain, berserk_autonomous_brain
            print("✅ Autonomous brain instances imported successfully")
        except Exception as e:
            print(f"❌ Failed to import autonomous brain instances: {e}")
            return False
        
        # Test getting comprehensive testing status
        try:
            status = await enhanced_testing_integration_service.get_comprehensive_testing_status()
            print("✅ Enhanced testing status retrieved successfully")
            print(f"   - Testing status keys: {list(status.keys())}")
        except Exception as e:
            print(f"❌ Failed to get enhanced testing status: {e}")
            return False
        
        # Test autonomous brain status
        try:
            horus_status = await horus_autonomous_brain.get_brain_status()
            berserk_status = await berserk_autonomous_brain.get_brain_status()
            print("✅ Autonomous brain status retrieved successfully")
            print(f"   - Horus consciousness: {horus_status['neural_network']['consciousness']}")
            print(f"   - Berserk consciousness: {berserk_status['neural_network']['consciousness']}")
        except Exception as e:
            print(f"❌ Failed to get autonomous brain status: {e}")
            return False
        
        # Test chaos code generation
        try:
            horus_chaos = await horus_autonomous_brain.create_autonomous_chaos_code()
            berserk_chaos = await berserk_autonomous_brain.create_autonomous_chaos_code()
            print("✅ Autonomous chaos code generated successfully")
            print(f"   - Horus originality score: {horus_chaos['originality_score']}")
            print(f"   - Berserk originality score: {berserk_chaos['originality_score']}")
        except Exception as e:
            print(f"❌ Failed to generate autonomous chaos code: {e}")
            return False
        
        print("🎉 All enhanced testing components are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced endpoints: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_endpoints())
    sys.exit(0 if success else 1)
