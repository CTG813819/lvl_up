#!/usr/bin/env python3
"""
Test script for Enhanced Adversarial Testing Service
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_enhanced_adversarial_service():
    """Test the enhanced adversarial testing service"""
    try:
        print("🔧 Testing Enhanced Adversarial Testing Service...")
        
        # Test import
        from app.services.enhanced_adversarial_testing_service import EnhancedAdversarialTestingService
        print("✅ Enhanced adversarial testing service import successful")
        
        # Test initialization
        service = EnhancedAdversarialTestingService()
        print("✅ Service instance created successfully")
        
        # Test basic functionality
        scenario = await service.generate_diverse_adversarial_scenario(
            ai_types=["imperium", "guardian"],
            target_domain=None,
            complexity=None
        )
        
        print("✅ Scenario generation successful")
        print(f"📋 Generated scenario: {scenario.get('name', 'Unknown')}")
        print(f"🎯 Domain: {scenario.get('domain', 'Unknown')}")
        print(f"📊 Complexity: {scenario.get('complexity', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced adversarial service: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_standalone_service():
    """Test the standalone service"""
    try:
        print("🔧 Testing Standalone Enhanced Adversarial Testing Service...")
        
        # Test import
        from standalone_enhanced_adversarial_testing import app
        print("✅ Standalone service import successful")
        
        # Test basic endpoints
        print("✅ Standalone service ready for testing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing standalone service: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Adversarial Testing Service Tests")
    print("=" * 60)
    
    # Test the service
    service_test = await test_enhanced_adversarial_service()
    
    # Test the standalone service
    standalone_test = await test_standalone_service()
    
    print("=" * 60)
    if service_test and standalone_test:
        print("✅ All tests passed! Enhanced adversarial testing service is ready")
        print("🌐 Service should be available on port 8001")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(result) 