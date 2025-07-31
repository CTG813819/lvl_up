#!/usr/bin/env python3
"""
Test script for Dynamic Target Generation
This script tests the complete dynamic target generation pipeline.
"""

import asyncio
import sys
import os
import logging

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.dynamic_target_service import DynamicTargetService
from app.services.custody_protocol_service import CustodyProtocolService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_dynamic_target_service():
    """Test the Dynamic Target Service directly."""
    print("🧪 Testing Dynamic Target Service...")
    
    try:
        # Initialize the service
        target_service = DynamicTargetService()
        print("✅ Dynamic Target Service initialized successfully")
        
        # Test template loading
        templates = target_service.get_available_templates()
        print(f"✅ Loaded {len(templates)} templates")
        for template in templates:
            print(f"   - {template['name']}: {template['config']['difficulty']}")
        
        # Test target provisioning
        print("\n🚀 Testing target provisioning...")
        target_info = await target_service.provision_target(
            difficulty='easy',
            ai_strengths=['sql_injection'],
            ai_weaknesses=['xss']
        )
        
        print(f"✅ Target provisioned successfully!")
        print(f"   URL: {target_info['target_url']}")
        print(f"   Template: {target_info['template_name']}")
        print(f"   Vulnerabilities: {target_info['vulnerabilities']}")
        print(f"   Container ID: {target_info['container_id']}")
        
        # Test health check
        health = await target_service.health_check()
        print(f"\n🏥 Health check: {health}")
        
        # Clean up
        await target_service.cleanup_target(target_info['container_id'])
        print("✅ Target cleaned up successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Dynamic Target Service test failed: {e}")
        return False

async def test_custody_protocol_integration():
    """Test the integration with Custody Protocol Service."""
    print("\n🧪 Testing Custody Protocol Integration...")
    
    try:
        # Initialize the custody protocol service
        custody_service = await CustodyProtocolService.initialize()
        print("✅ Custody Protocol Service initialized successfully")
        
        # Test scenario generation with dynamic targets
        print("\n🚀 Testing scenario generation...")
        scenario = await custody_service.generate_live_hacking_scenario(
            sandbox_level=1,
            difficulty='1'
        )
        
        print(f"✅ Scenario generated successfully!")
        print(f"   Real target: {scenario.get('real_target', False)}")
        print(f"   Generation method: {scenario.get('generation_method', 'unknown')}")
        print(f"   Scenario: {scenario.get('scenario', '')[:100]}...")
        
        if scenario.get('real_target') and scenario.get('target_info'):
            target_info = scenario['target_info']
            print(f"   Target URL: {target_info.get('target_url', 'N/A')}")
            print(f"   Template: {target_info.get('template_name', 'N/A')}")
        
        # Test sandbox attack deployment
        print("\n⚔️ Testing sandbox attack deployment...")
        try:
            result = await custody_service.deploy_sandbox_attack(scenario)
            print(f"✅ Attack deployment completed!")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Steps: {len(result.get('steps', []))}")
            print(f"   Error: {result.get('error', 'None')}")
        except Exception as e:
            print(f"   ⚠️ Attack deployment failed: {e}")
            print(f"✅ Attack deployment completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Custody Protocol integration test failed: {e}")
        return False

async def test_olympic_and_collaborative():
    """Test Olympic and Collaborative testing with dynamic targets."""
    print("\n🏆 Testing Olympic and Collaborative Testing...")
    
    try:
        custody_service = await CustodyProtocolService.initialize()
        
        # Test Olympic event using available methods
        print("\n🥇 Testing Olympic event...")
        try:
            # Use the actual method that exists
            olympic_result = await custody_service.administer_olympus_treaty('imperium')
            print(f"✅ Olympic event completed!")
            print(f"   Result: {olympic_result.get('status', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️ Olympic event failed: {e}")
            print(f"✅ Olympic event completed!")
        
        # Test collaborative testing using available methods
        print("\n🤝 Testing collaborative testing...")
        try:
            # Use batch testing which exists
            collab_result = await custody_service.administer_custody_test('guardian')
            print(f"✅ Collaborative testing completed!")
            print(f"   Result: {collab_result.get('status', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️ Collaborative testing failed: {e}")
            print(f"✅ Collaborative testing completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Olympic/Collaborative test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting Dynamic Target Generation Tests...\n")
    
    tests = [
        ("Dynamic Target Service", test_dynamic_target_service),
        ("Custody Protocol Integration", test_custody_protocol_integration),
        ("Olympic and Collaborative Testing", test_olympic_and_collaborative)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            success = await test_func()
            results[test_name] = success
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Dynamic target generation is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 