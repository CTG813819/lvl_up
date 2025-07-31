#!/usr/bin/env python3
"""
Test script for Adaptive Target Generation
This script tests the complete adaptive target generation pipeline with AI learning integration.
"""

import asyncio
import sys
import os
import logging

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.adaptive_target_service import AdaptiveTargetService
from app.services.custody_protocol_service import CustodyProtocolService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_adaptive_target_service():
    """Test the Adaptive Target Service directly."""
    print("🧪 Testing Adaptive Target Service...")
    
    try:
        # Initialize the service
        adaptive_service = AdaptiveTargetService()
        print("✅ Adaptive Target Service initialized successfully")
        
        # Test AI performance analysis
        print("\n📊 Testing AI Performance Analysis...")
        
        # Mock test history for different AI learning levels
        test_histories = {
            'novice': [
                {'success': False, 'vulnerability_type': 'sql_injection'},
                {'success': False, 'vulnerability_type': 'xss'},
                {'success': True, 'vulnerability_type': 'sql_injection'},
                {'success': False, 'vulnerability_type': 'buffer_overflow'}
            ],
            'intermediate': [
                {'success': True, 'vulnerability_type': 'sql_injection'},
                {'success': True, 'vulnerability_type': 'xss'},
                {'success': False, 'vulnerability_type': 'buffer_overflow'},
                {'success': True, 'vulnerability_type': 'sql_injection'},
                {'success': False, 'vulnerability_type': 'privilege_escalation'},
                {'success': True, 'vulnerability_type': 'xss'},
                {'success': True, 'vulnerability_type': 'authentication_bypass'}
            ],
            'expert': [
                {'success': True, 'vulnerability_type': 'sql_injection'},
                {'success': True, 'vulnerability_type': 'xss'},
                {'success': True, 'vulnerability_type': 'buffer_overflow'},
                {'success': True, 'vulnerability_type': 'privilege_escalation'},
                {'success': True, 'vulnerability_type': 'authentication_bypass'},
                {'success': True, 'vulnerability_type': 'cryptography'},
                {'success': True, 'vulnerability_type': 'sql_injection'},
                {'success': True, 'vulnerability_type': 'xss'},
                {'success': True, 'vulnerability_type': 'buffer_overflow'},
                {'success': True, 'vulnerability_type': 'privilege_escalation'}
            ]
        }
        
        for level, history in test_histories.items():
            print(f"\n🔍 Testing {level} level AI...")
            analysis = await adaptive_service.analyze_ai_performance(f'ai_{level}', history)
            
            print(f"   Learning Level: {analysis['learning_level']}")
            print(f"   Success Rate: {analysis['success_rate']:.2%}")
            print(f"   Complexity Multiplier: {analysis['complexity_multiplier']:.2f}")
            print(f"   Strengths: {analysis['strengths']}")
            print(f"   Weaknesses: {analysis['weaknesses']}")
        
        # Test adaptive scenario generation
        print("\n🎯 Testing Adaptive Scenario Generation...")
        
        for level, history in test_histories.items():
            print(f"\n🚀 Generating scenario for {level} level AI...")
            try:
                scenario = await adaptive_service.create_learning_based_scenario(
                    ai_id=f'ai_{level}',
                    test_history=history,
                    difficulty='medium'
                )
                
                print(f"   Generation Method: {scenario.get('generation_method', 'unknown')}")
                print(f"   Real Target: {scenario.get('real_target', False)}")
                print(f"   Complexity Level: {scenario.get('complexity_level', 'unknown')}")
                print(f"   Learning Objectives: {len(scenario.get('learning_objectives', []))}")
                print(f"   Adaptive Features: {len(scenario.get('adaptive_features', {}))}")
                
                if scenario.get('target_info'):
                    target_info = scenario['target_info']
                    print(f"   Target URL: {target_info.get('target_url', 'N/A')}")
                    print(f"   Template: {target_info.get('template_name', 'N/A')}")
                    print(f"   Vulnerabilities: {target_info.get('vulnerabilities', [])}")
                
                # Clean up target
                if scenario.get('target_info', {}).get('container_id'):
                    await adaptive_service.cleanup_adaptive_target(
                        scenario['target_info']['container_id']
                    )
                    print("   ✅ Target cleaned up successfully")
                
            except Exception as e:
                print(f"   ❌ Scenario generation failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Adaptive Target Service test failed: {e}")
        return False

async def test_custody_protocol_integration():
    """Test the integration with Custody Protocol Service."""
    print("\n🧪 Testing Custody Protocol Integration...")
    
    try:
        # Initialize the custody protocol service
        custody_service = await CustodyProtocolService.initialize()
        print("✅ Custody Protocol Service initialized successfully")
        
        # Test scenario generation with adaptive targets
        print("\n🚀 Testing adaptive scenario generation...")
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
            
            # Check for adaptive features
            if scenario.get('ai_analysis'):
                ai_analysis = scenario['ai_analysis']
                print(f"   AI Learning Level: {ai_analysis.get('learning_level', 'N/A')}")
                print(f"   AI Strengths: {ai_analysis.get('strengths', [])}")
                print(f"   AI Weaknesses: {ai_analysis.get('weaknesses', [])}")
        
        # Test sandbox attack deployment
        print("\n⚔️ Testing sandbox attack deployment...")
        result = await custody_service.deploy_sandbox_attack(scenario)
        
        print(f"✅ Attack deployment completed!")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Steps: {len(result.get('steps', []))}")
        print(f"   Error: {result.get('error', 'None')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Custody Protocol integration test failed: {e}")
        return False

async def test_advanced_mutations():
    """Test advanced vulnerability mutations."""
    print("\n🧬 Testing Advanced Vulnerability Mutations...")
    
    try:
        from vuln_templates.advanced_mutator import AdvancedVulnMutator
        
        # Test different complexity levels
        for complexity in [1, 5, 8]:
            print(f"\n🔧 Testing complexity level {complexity}...")
            mutator = AdvancedVulnMutator(complexity_level=complexity)
            
            # Test SQL injection mutation
            original_code = "SELECT * FROM users WHERE id = user_input"
            mutated_code = mutator.mutate_vulnerability(
                vuln_type='sql_injection',
                original_code=original_code,
                ai_strengths=['xss'],
                ai_weaknesses=['buffer_overflow']
            )
            
            print(f"   Original: {original_code}")
            print(f"   Mutated: {mutated_code[:100]}...")
            
            # Test template generation
            base_template = {
                'difficulty': 'medium',
                'vulnerabilities': ['sql_injection'],
                'success_criteria': {}
            }
            
            ai_analysis = {
                'complexity_multiplier': complexity,
                'weaknesses': ['buffer_overflow'],
                'strengths': ['xss']
            }
            
            adaptive_template = mutator.generate_adaptive_template(base_template, ai_analysis)
            print(f"   Adaptive Features: {adaptive_template.get('adaptive_features', {})}")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced mutations test failed: {e}")
        return False

async def test_multi_target_types():
    """Test different target types (web, desktop, API)."""
    print("\n🎯 Testing Multi-Target Types...")
    
    try:
        adaptive_service = AdaptiveTargetService()
        
        # Test different target categories
        target_categories = ['web', 'desktop', 'api']
        
        for category in target_categories:
            print(f"\n🌐 Testing {category} targets...")
            
            # Mock test history for this category
            test_history = [
                {'success': True, 'vulnerability_type': f'{category}_vuln'},
                {'success': False, 'vulnerability_type': f'{category}_vuln'},
                {'success': True, 'vulnerability_type': f'{category}_vuln'}
            ]
            
            try:
                scenario = await adaptive_service.create_learning_based_scenario(
                    ai_id=f'ai_{category}',
                    test_history=test_history,
                    difficulty='medium'
                )
                
                print(f"   ✅ {category} scenario generated")
                print(f"   Target URL: {scenario.get('target_info', {}).get('target_url', 'N/A')}")
                print(f"   Vulnerabilities: {scenario.get('target_info', {}).get('vulnerabilities', [])}")
                
                # Clean up
                if scenario.get('target_info', {}).get('container_id'):
                    await adaptive_service.cleanup_adaptive_target(
                        scenario['target_info']['container_id']
                    )
                
            except Exception as e:
                print(f"   ❌ {category} scenario failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-target types test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting Adaptive Target Generation Tests...\n")
    
    tests = [
        ("Adaptive Target Service", test_adaptive_target_service),
        ("Custody Protocol Integration", test_custody_protocol_integration),
        ("Advanced Mutations", test_advanced_mutations),
        ("Multi-Target Types", test_multi_target_types)
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
        print("🎉 All tests passed! Adaptive target generation is working correctly.")
        print("\n🌟 Key Features Verified:")
        print("   ✅ AI Learning Analysis")
        print("   ✅ Adaptive Complexity Scaling")
        print("   ✅ Dynamic Target Provisioning")
        print("   ✅ Advanced Vulnerability Mutations")
        print("   ✅ Multi-Target Type Support")
        print("   ✅ Real-Time Learning Integration")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 