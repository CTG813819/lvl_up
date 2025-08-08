#!/usr/bin/env python3
"""
Test script for Security Attack Simulation System
Tests the comprehensive security testing functionality
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_security_endpoints():
    """Test all security testing endpoints"""
    
    print("🔒 Testing Security Attack Simulation System")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Get security status
        print("\n1. Testing security status endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/security/attack-simulation/status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Security status: {data.get('security_status', {}).get('overall_security_posture', 'unknown')}")
                print(f"   AI collaboration: {data.get('security_status', {}).get('ai_collaboration_status', {})}")
            else:
                print(f"❌ Security status failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Security status error: {e}")
        
        # Test 2: Test AI collaboration
        print("\n2. Testing AI collaboration...")
        try:
            response = await client.post(f"{BASE_URL}/api/security/ai-collaboration/test")
            if response.status_code == 200:
                data = response.json()
                collaboration = data.get("ai_collaboration", {})
                print(f"✅ AI collaboration test completed")
                print(f"   Guardian AI: {collaboration.get('guardian_ai', {}).get('status', 'unknown')}")
                print(f"   Project Horus: {collaboration.get('project_horus', {}).get('status', 'unknown')}")
                print(f"   Project Berserk: {collaboration.get('project_berserk', {}).get('status', 'unknown')}")
            else:
                print(f"❌ AI collaboration test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ AI collaboration error: {e}")
        
        # Test 3: Docker environments status
        print("\n3. Testing Docker environments...")
        try:
            response = await client.get(f"{BASE_URL}/api/security/docker-environments/status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Docker status: {data.get('status', 'unknown')}")
                print(f"   Available: {data.get('docker_available', False)}")
                print(f"   Security containers: {data.get('total_containers', 0)}")
            else:
                print(f"❌ Docker status failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Docker status error: {e}")
        
        # Test 4: Encryption testing
        print("\n4. Testing encryption vulnerability testing...")
        try:
            response = await client.post(f"{BASE_URL}/api/security/encryption-testing/start")
            if response.status_code == 200:
                data = response.json()
                results = data.get("encryption_test_results", [])
                print(f"✅ Encryption testing completed")
                print(f"   Tests run: {len(results)}")
                for result in results[:2]:  # Show first 2 results
                    print(f"   - {result.get('test_name', 'Unknown')}: {result.get('security_score', 0):.1f}/10")
            else:
                print(f"❌ Encryption testing failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Encryption testing error: {e}")
        
        # Test 5: Authentication testing
        print("\n5. Testing authentication vulnerability testing...")
        try:
            response = await client.post(f"{BASE_URL}/api/security/authentication-testing/start")
            if response.status_code == 200:
                data = response.json()
                results = data.get("authentication_test_results", [])
                print(f"✅ Authentication testing completed")
                print(f"   Tests run: {len(results)}")
                for result in results[:2]:  # Show first 2 results
                    print(f"   - {result.get('test_name', 'Unknown')}: {result.get('security_score', 0):.1f}/10")
            else:
                print(f"❌ Authentication testing failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Authentication testing error: {e}")
        
        # Test 6: API security testing
        print("\n6. Testing API security...")
        try:
            response = await client.post(f"{BASE_URL}/api/security/api-security-testing/start")
            if response.status_code == 200:
                data = response.json()
                results = data.get("api_test_results", [])
                print(f"✅ API security testing completed")
                print(f"   Tests run: {len(results)}")
                for result in results[:2]:  # Show first 2 results
                    print(f"   - {result.get('test_name', 'Unknown')}: {result.get('security_score', 0):.1f}/10")
            else:
                print(f"❌ API security testing failed: {response.status_code}")
        except Exception as e:
            print(f"❌ API security testing error: {e}")
        
        # Test 7: Mobile security testing
        print("\n7. Testing mobile app security...")
        try:
            response = await client.post(f"{BASE_URL}/api/security/mobile-security-testing/start")
            if response.status_code == 200:
                data = response.json()
                results = data.get("mobile_test_results", {})
                print(f"✅ Mobile security testing completed")
                print(f"   Overall score: {results.get('overall_mobile_security_score', 0):.1f}/10")
                print(f"   Categories tested: {len(results.get('test_categories', {}))}")
            else:
                print(f"❌ Mobile security testing failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Mobile security testing error: {e}")
        
        # Test 8: APT simulation
        print("\n8. Testing APT simulation...")
        try:
            response = await client.post(f"{BASE_URL}/api/security/apt-simulation/start")
            if response.status_code == 200:
                data = response.json()
                results = data.get("apt_simulation_results", {})
                print(f"✅ APT simulation completed")
                print(f"   Success probability: {results.get('overall_success_probability', 0):.1%}")
                print(f"   Defensive effectiveness: {results.get('defensive_effectiveness', 0):.1f}/10")
            else:
                print(f"❌ APT simulation failed: {response.status_code}")
        except Exception as e:
            print(f"❌ APT simulation error: {e}")
        
        # Test 9: ML security analysis
        print("\n9. Testing ML security analysis...")
        try:
            response = await client.post(f"{BASE_URL}/api/security/ml-security-analysis/start")
            if response.status_code == 200:
                data = response.json()
                results = data.get("ml_analysis_results", {})
                print(f"✅ ML security analysis completed")
                if results.get("status") == "ml_unavailable":
                    print("   ML features disabled (scikit-learn not available)")
                else:
                    print(f"   Vulnerability probability: {results.get('vulnerability_probability', 0):.1%}")
                    print(f"   Confidence score: {results.get('confidence_score', 0):.1%}")
            else:
                print(f"❌ ML security analysis failed: {response.status_code}")
        except Exception as e:
            print(f"❌ ML security analysis error: {e}")
        
        # Test 10: Security recommendations
        print("\n10. Testing security recommendations...")
        try:
            response = await client.get(f"{BASE_URL}/api/security/security-improvements/recommendations")
            if response.status_code == 200:
                data = response.json()
                improvements = data.get("security_improvements", [])
                print(f"✅ Security recommendations completed")
                print(f"   Total recommendations: {len(improvements)}")
                for improvement in improvements[:3]:  # Show first 3
                    print(f"   - {improvement.get('category', 'Unknown')}: {improvement.get('improvement', 'No description')}")
            else:
                print(f"❌ Security recommendations failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Security recommendations error: {e}")
        
        # Test 11: Guardian AI analysis
        print("\n11. Testing Guardian AI analysis...")
        try:
            response = await client.get(f"{BASE_URL}/api/security/guardian-analysis/latest")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Guardian AI analysis completed")
                print(f"   Analysis available: {bool(data.get('guardian_health_check'))}")
            else:
                print(f"❌ Guardian AI analysis failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Guardian AI analysis error: {e}")
        
        # Test 12: Comprehensive attack simulation
        print("\n12. Testing comprehensive attack simulation...")
        try:
            print("   Starting comprehensive security attack simulation...")
            response = await client.post(f"{BASE_URL}/api/security/attack-simulation/start?attack_type=comprehensive")
            if response.status_code == 200:
                data = response.json()
                results = data.get("attack_results", {})
                print(f"✅ Comprehensive attack simulation completed")
                print(f"   Overall security score: {results.get('overall_security_score', 0):.1f}/10")
                print(f"   Attack ID: {results.get('attack_id', 'unknown')}")
                print(f"   Phases completed: {len([k for k in results.keys() if k.endswith('_tests') or k.endswith('_simulation')])}")
                
                # Show AI collaboration results
                collaboration = results.get("ai_collaboration", {})
                active_ais = sum(1 for ai_config in collaboration.values() if ai_config.get("status") == "active")
                print(f"   AI collaboration: {active_ais}/{len(collaboration)} AIs active")
                
            else:
                print(f"❌ Comprehensive attack simulation failed: {response.status_code}")
                if response.status_code == 500:
                    error_detail = response.json().get("detail", "Unknown error")
                    print(f"   Error: {error_detail}")
        except Exception as e:
            print(f"❌ Comprehensive attack simulation error: {e}")

    print("\n" + "=" * 60)
    print("🔒 Security Attack Simulation Testing Complete!")
    print(f"   Timestamp: {datetime.utcnow().isoformat()}")

if __name__ == "__main__":
    asyncio.run(test_security_endpoints())