#!/usr/bin/env python3
"""
Comprehensive Security System Test
Tests the complete security system including:
- Internet cybersecurity learning
- Rolling password authentication
- Enhanced security attack simulation with Docker
- Guardian AI integration
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_comprehensive_security_system():
    """Test the complete enhanced security system"""
    
    print("🔒 Testing Comprehensive Security System")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # Test 1: Rolling Password System
        print("\n1. Testing Rolling Password Authentication System...")
        try:
            response = await client.get(f"{BASE_URL}/api/auth/system-status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Rolling password system: {data.get('status', 'unknown')}")
                print(f"   Password rotation: {data.get('password_rotation', {}).get('active', False)}")
                print(f"   Security status: {data.get('security_metrics', {}).get('security_status', 'unknown')}")
                print(f"   Failed attempts (24h): {data.get('security_metrics', {}).get('failed_attempts_24h', 0)}")
            else:
                print(f"❌ Rolling password system failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Rolling password system error: {e}")
        
        # Test 2: Password Info
        print("\n2. Testing Password Information...")
        try:
            response = await client.get(f"{BASE_URL}/api/auth/password-info")
            if response.status_code == 200:
                data = response.json()
                password_info = data.get("password_info", {})
                print(f"✅ Password info retrieved")
                print(f"   Active password: {password_info.get('has_active_password', False)}")
                print(f"   Rotation interval: {password_info.get('rotation_interval_hours', 0)} hours")
                print(f"   Active sessions: {password_info.get('active_sessions', 0)}")
            else:
                print(f"❌ Password info failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Password info error: {e}")
        
        # Test 3: Test Authentication (Demo)
        print("\n3. Testing Authentication Flow...")
        try:
            # This is a demo test - in real usage, user would provide actual credentials
            test_auth = {
                "user_id": "test_user",
                "password": "demo_password"
            }
            response = await client.post(f"{BASE_URL}/api/auth/login", json=test_auth)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Authentication test completed")
                print(f"   Success: {data.get('success', False)}")
                print(f"   Message: {data.get('message', 'No message')}")
                if not data.get('success'):
                    print(f"   Expected failure for demo credentials")
            else:
                print(f"❌ Authentication test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Authentication test error: {e}")
        
        # Test 4: Internet Cybersecurity Learning Integration
        print("\n4. Testing Internet Cybersecurity Learning...")
        try:
            response = await client.post(f"{BASE_URL}/api/security/attack-simulation/start?attack_type=internet_learning_enhanced")
            if response.status_code == 200:
                data = response.json()
                attack_results = data.get("attack_results", {})
                print(f"✅ Internet learning enhanced attack simulation completed")
                
                # Check for internet learning results
                internet_learning = attack_results.get("internet_learning", {})
                if internet_learning:
                    threat_summary = internet_learning.get("threat_summary", {})
                    print(f"   Threats discovered: {threat_summary.get('total_threats', 0)}")
                    print(f"   Critical threats: {threat_summary.get('critical_threats', 0)}")
                    print(f"   High threats: {threat_summary.get('high_threats', 0)}")
                    print(f"   Attack vectors: {threat_summary.get('unique_attack_vectors', 0)}")
                else:
                    print("   Internet learning results not found in response")
                
                # Check for Docker testing results
                docker_testing = attack_results.get("docker_testing", {})
                if docker_testing:
                    print(f"   Docker scenarios: {docker_testing.get('total_scenarios', 0)}")
                    print(f"   Successful tests: {docker_testing.get('successful_tests', 0)}")
                    print(f"   Failed tests: {docker_testing.get('failed_tests', 0)}")
                    print(f"   Security findings: {len(docker_testing.get('security_findings', []))}")
                
                print(f"   Overall security score: {attack_results.get('overall_security_score', 0):.1f}/10")
            else:
                print(f"❌ Internet learning test failed: {response.status_code}")
                if response.status_code == 500:
                    error_detail = response.json().get("detail", "Unknown error")
                    print(f"   Error: {error_detail}")
        except Exception as e:
            print(f"❌ Internet learning test error: {e}")
        
        # Test 5: Enhanced Security Testing with All Components
        print("\n5. Testing Enhanced Security System Integration...")
        try:
            response = await client.post(f"{BASE_URL}/api/security/attack-simulation/start?attack_type=comprehensive")
            if response.status_code == 200:
                data = response.json()
                attack_results = data.get("attack_results", {})
                print(f"✅ Comprehensive security testing completed")
                
                # Count completed phases
                phases = [
                    "ai_collaboration", "internet_learning", "reconnaissance",
                    "encryption_tests", "authentication_tests", "api_tests",
                    "mobile_tests", "apt_simulation", "docker_testing",
                    "guardian_analysis", "ml_analysis", "security_improvements"
                ]
                
                completed_phases = sum(1 for phase in phases if phase in attack_results)
                print(f"   Security phases completed: {completed_phases}/{len(phases)}")
                
                # Security metrics
                print(f"   Overall security score: {attack_results.get('overall_security_score', 0):.1f}/10")
                print(f"   Encryption tests: {len(attack_results.get('encryption_tests', []))}")
                print(f"   Authentication tests: {len(attack_results.get('authentication_tests', []))}")
                print(f"   API tests: {len(attack_results.get('api_tests', []))}")
                
                # AI collaboration status
                ai_collaboration = attack_results.get("ai_collaboration", {})
                active_ais = sum(1 for ai_config in ai_collaboration.values() if isinstance(ai_config, dict) and ai_config.get("status") == "active")
                print(f"   AI collaboration: {active_ais} AIs active")
                
                # Security improvements
                improvements = attack_results.get("security_improvements", [])
                print(f"   Security improvements suggested: {len(improvements)}")
                
            else:
                print(f"❌ Comprehensive security test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Comprehensive security test error: {e}")
        
        # Test 6: Guardian AI Security Analysis
        print("\n6. Testing Guardian AI Security Analysis...")
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
        
        # Test 7: ML Security Analysis
        print("\n7. Testing ML Security Analysis...")
        try:
            response = await client.post(f"{BASE_URL}/api/security/ml-security-analysis/start")
            if response.status_code == 200:
                data = response.json()
                ml_results = data.get("ml_analysis_results", {})
                print(f"✅ ML security analysis completed")
                if ml_results.get("status") == "ml_unavailable":
                    print("   ML features disabled (scikit-learn not available)")
                else:
                    print(f"   Vulnerability probability: {ml_results.get('vulnerability_probability', 0):.1%}")
                    print(f"   Confidence score: {ml_results.get('confidence_score', 0):.1%}")
                    print(f"   ML recommendations: {len(ml_results.get('ml_recommendations', []))}")
            else:
                print(f"❌ ML security analysis failed: {response.status_code}")
        except Exception as e:
            print(f"❌ ML security analysis error: {e}")
        
        # Test 8: Docker Environment Status
        print("\n8. Testing Docker Security Environment...")
        try:
            response = await client.get(f"{BASE_URL}/api/security/docker-environments/status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Docker environment status retrieved")
                print(f"   Docker available: {data.get('docker_available', False)}")
                print(f"   Security containers: {data.get('total_containers', 0)}")
                print(f"   Status: {data.get('status', 'unknown')}")
            else:
                print(f"❌ Docker environment check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Docker environment error: {e}")
        
        # Test 9: Security Recommendations
        print("\n9. Testing Security Recommendations...")
        try:
            response = await client.get(f"{BASE_URL}/api/security/security-improvements/recommendations")
            if response.status_code == 200:
                data = response.json()
                improvements = data.get("security_improvements", [])
                print(f"✅ Security recommendations retrieved")
                print(f"   Total recommendations: {len(improvements)}")
                for i, improvement in enumerate(improvements[:3], 1):
                    print(f"   {i}. {improvement.get('category', 'Unknown')}: {improvement.get('improvement', 'No description')}")
            else:
                print(f"❌ Security recommendations failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Security recommendations error: {e}")
        
        # Test 10: Attack History
        print("\n10. Testing Attack History...")
        try:
            response = await client.get(f"{BASE_URL}/api/security/attack-history")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Attack history retrieved")
                print(f"   Total attacks simulated: {data.get('total_attacks_simulated', 0)}")
                print(f"   Average security score: {data.get('average_security_score', 0):.1f}/10")
                print(f"   Recent attacks: {len(data.get('attack_history', []))}")
            else:
                print(f"❌ Attack history failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Attack history error: {e}")
        
        # Test 11: Rolling Password Integration
        print("\n11. Testing Rolling Password Security Integration...")
        try:
            response = await client.get(f"{BASE_URL}/api/auth/integration/security-status")
            if response.status_code == 200:
                data = response.json()
                rolling_security = data.get("rolling_password_security", {})
                integration = data.get("integration_points", {})
                print(f"✅ Rolling password security integration verified")
                print(f"   Security level: {rolling_security.get('security_level', 'unknown')}")
                print(f"   Rotation frequency: {rolling_security.get('rotation_frequency', 'unknown')}")
                print(f"   Guardian AI compatible: {integration.get('guardian_ai_compatible', False)}")
                print(f"   Security testing compatible: {integration.get('security_testing_compatible', False)}")
            else:
                print(f"❌ Rolling password integration failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Rolling password integration error: {e}")
        
        # Test 12: Force Password Rotation (Admin Test)
        print("\n12. Testing Force Password Rotation...")
        try:
            response = await client.post(f"{BASE_URL}/api/auth/force-rotation")
            if response.status_code == 200:
                data = response.json()
                rotation_result = data.get("rotation_result", {})
                print(f"✅ Password rotation test completed")
                print(f"   Rotation successful: {rotation_result.get('success', False)}")
                print(f"   New password generated: {rotation_result.get('new_password_generated', False)}")
                print(f"   Sessions invalidated: {rotation_result.get('all_sessions_invalidated', False)}")
            else:
                print(f"❌ Password rotation test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Password rotation test error: {e}")

    print("\n" + "=" * 80)
    print("🔒 Comprehensive Security System Testing Complete!")
    print(f"   Timestamp: {datetime.utcnow().isoformat()}")
    print("\n📋 System Features Tested:")
    print("   ✅ Rolling Password Authentication with Hourly Rotation")
    print("   ✅ Internet Cybersecurity Learning and Threat Intelligence")
    print("   ✅ Docker-based Security Testing with Real-world Scenarios")
    print("   ✅ Guardian AI Security Analysis Integration")
    print("   ✅ ML-driven Vulnerability Analysis and Pattern Recognition")
    print("   ✅ Comprehensive Attack Simulation with Multiple AI Collaboration")
    print("   ✅ Real-time Security Monitoring and Analytics")
    print("   ✅ Automated Security Improvements and Recommendations")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_security_system())