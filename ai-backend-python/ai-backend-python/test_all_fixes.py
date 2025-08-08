#!/usr/bin/env python3
"""
Comprehensive test script to verify all implemented fixes:
1. Conquest validation improvements (reduced timeouts, fallback logic)
2. Imperium proposals endpoint
3. GitHub token configuration
4. Overall system health
"""

import subprocess
import json
import time

def run_ssh_command(command):
    """Run SSH command on EC2"""
    ssh_cmd = f'ssh -i "New.pem" ubuntu@34.202.215.209 "{command}"'
    result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def test_backend_health():
    """Test backend health"""
    print("🧪 Testing backend health...")
    
    success, output, error = run_ssh_command("curl -s http://localhost:4000/health")
    if success and "status" in output:
        print("✅ Backend health: Working")
        return True
    else:
        print(f"❌ Backend health: Failed - {error}")
        return False

def test_conquest_validation_improvements():
    """Test Conquest validation improvements"""
    print("\n🧪 Testing Conquest validation improvements...")
    
    # Test app creation with timeout
    success, output, error = run_ssh_command("timeout 30 curl -X POST http://localhost:4000/api/conquest/create-app -H 'Content-Type: application/json' -d @/home/ubuntu/test_app_request.json")
    
    if success:
        print("✅ Conquest app creation: Completed within 30s timeout")
        print(f"   Response: {output[:200]}...")
        return True
    else:
        print(f"❌ Conquest app creation: Failed or timed out - {error}")
        return False

def test_conquest_statistics():
    """Test Conquest statistics"""
    print("\n🧪 Testing Conquest statistics...")
    
    success, output, error = run_ssh_command("curl -s http://localhost:4000/api/conquest/statistics")
    if success and output.strip():
        print("✅ Conquest statistics: Working")
        stats = json.loads(output)
        print(f"   Total apps: {stats.get('statistics', {}).get('totalApps', 0)}")
        return True
    else:
        print(f"❌ Conquest statistics: Failed - {error}")
        return False

def test_imperium_proposals():
    """Test Imperium proposals endpoint"""
    print("\n🧪 Testing Imperium proposals...")
    
    success, output, error = run_ssh_command("curl -s http://localhost:4000/api/imperium/proposals")
    if success and output.strip():
        print("✅ Imperium proposals: Working")
        proposals = json.loads(output)
        count = proposals.get('total_count', 0)
        print(f"   Total proposals: {count}")
        return True
    else:
        print(f"❌ Imperium proposals: Failed - {error}")
        return False

def test_imperium_other_endpoints():
    """Test other Imperium endpoints"""
    print("\n🧪 Testing other Imperium endpoints...")
    
    endpoints = [
        ("Status", "/api/imperium/status"),
        ("Monitoring", "/api/imperium/monitoring"),
        ("Improvements", "/api/imperium/improvements"),
        ("Issues", "/api/imperium/issues")
    ]
    
    results = []
    for name, endpoint in endpoints:
        success, output, error = run_ssh_command(f"curl -s http://localhost:4000{endpoint}")
        if success and output.strip():
            print(f"✅ {name}: Working")
            results.append(True)
        else:
            print(f"❌ {name}: Failed")
            results.append(False)
    
    return all(results)

def test_github_token():
    """Test GitHub token configuration"""
    print("\n🧪 Testing GitHub token configuration...")
    
    success, output, error = run_ssh_command("grep 'GITHUB_TOKEN' /home/ubuntu/ai-backend-python/.env")
    if success and output.strip():
        print("✅ GitHub token: Configured")
        return True
    else:
        print("❌ GitHub token: Not configured")
        return False

def test_all_ai_endpoints():
    """Test all AI service endpoints"""
    print("\n🧪 Testing all AI service endpoints...")
    
    endpoints = [
        ("Guardian Status", "/api/guardian/status"),
        ("Sandbox Status", "/api/sandbox/status"),
        ("Learning Data", "/api/learning/data"),
        ("Growth Insights", "/api/growth/insights"),
        ("Agents Status", "/api/agents/status")
    ]
    
    results = []
    for name, endpoint in endpoints:
        success, output, error = run_ssh_command(f"curl -s http://localhost:4000{endpoint}")
        if success and output.strip():
            print(f"✅ {name}: Working")
            results.append(True)
        else:
            print(f"❌ {name}: Failed")
            results.append(False)
    
    return results

def main():
    """Main test function"""
    print("🚀 Testing all implemented fixes...")
    
    # Test 1: Backend health
    health_ok = test_backend_health()
    if not health_ok:
        print("❌ Backend not healthy, stopping tests")
        return
    
    # Test 2: Conquest validation improvements
    conquest_ok = test_conquest_validation_improvements()
    
    # Test 3: Conquest statistics
    conquest_stats_ok = test_conquest_statistics()
    
    # Test 4: Imperium proposals
    imperium_proposals_ok = test_imperium_proposals()
    
    # Test 5: Other Imperium endpoints
    imperium_other_ok = test_imperium_other_endpoints()
    
    # Test 6: GitHub token
    github_ok = test_github_token()
    
    # Test 7: All AI endpoints
    ai_endpoints_results = test_all_ai_endpoints()
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"✅ Backend Health: {'Working' if health_ok else 'Failed'}")
    print(f"✅ Conquest Validation: {'Improved' if conquest_ok else 'Still Issues'}")
    print(f"✅ Conquest Statistics: {'Working' if conquest_stats_ok else 'Failed'}")
    print(f"✅ Imperium Proposals: {'Working' if imperium_proposals_ok else 'Failed'}")
    print(f"✅ Imperium Other: {'Working' if imperium_other_ok else 'Failed'}")
    print(f"✅ GitHub Token: {'Configured' if github_ok else 'Not Configured'}")
    print(f"✅ AI Endpoints: {sum(ai_endpoints_results)}/{len(ai_endpoints_results)} Working")
    
    # Overall assessment
    total_tests = 6 + len(ai_endpoints_results)
    passed_tests = sum([
        health_ok, conquest_ok, conquest_stats_ok, 
        imperium_proposals_ok, imperium_other_ok, github_ok
    ]) + sum(ai_endpoints_results)
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if success_rate >= 80:
        print("🎉 Excellent! Most fixes are working correctly.")
    elif success_rate >= 60:
        print("⚠️ Good progress, but some issues remain.")
    else:
        print("❌ Significant issues remain to be addressed.")

if __name__ == "__main__":
    main() 