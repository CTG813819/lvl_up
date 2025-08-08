#!/usr/bin/env python3
"""
Monitor EC2 Testing Progress
"""

import requests
import json
import time
from datetime import datetime

def monitor_ec2_tests():
    """Monitor the progress of EC2 testing"""
    base_url = "http://34.202.215.209:4000"
    
    print("🔍 Monitoring EC2 Testing Progress")
    print("=" * 50)
    print(f"📍 Target: {base_url}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test categories to monitor
    test_categories = [
        ("Basic Connectivity", "/health"),
        ("AI Agents Status", "/api/agents/status"),
        ("Learning System", "/api/learning/status"),
        ("Proposals", "/api/proposals/"),
        ("Oath Papers", "/api/oath-papers/"),
        ("Growth Analytics", "/api/growth/status"),
        ("Conquest AI", "/api/conquest/status"),
        ("GitHub Integration", "/api/github/status")
    ]
    
    results = {}
    
    for category, endpoint in test_categories:
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                status = "✅ PASS"
                data = response.json()
                
                # Extract relevant metrics
                if "agents" in data:
                    agents_count = len(data.get("agents", {}))
                    metric = f"{agents_count} agents"
                elif "total_experiments" in data:
                    experiments = data.get("total_experiments", 0)
                    metric = f"{experiments} experiments"
                elif "proposals" in data:
                    proposals_count = len(data.get("proposals", []))
                    metric = f"{proposals_count} proposals"
                elif "oath_papers" in data:
                    papers_count = len(data.get("oath_papers", []))
                    metric = f"{papers_count} papers"
                elif "conquest_ai" in data:
                    deployments = data.get("conquest_ai", {}).get("total_deployments", 0)
                    metric = f"{deployments} deployments"
                else:
                    metric = "OK"
                
                print(f"{status} {category:<20} {metric:<15} ({response_time:.1f}ms)")
                
            else:
                status = "❌ FAIL"
                metric = f"HTTP {response.status_code}"
                print(f"{status} {category:<20} {metric:<15} ({response_time:.1f}ms)")
                
            results[category] = {
                "status": "pass" if response.status_code == 200 else "fail",
                "response_time": response_time,
                "status_code": response.status_code
            }
            
        except Exception as e:
            status = "❌ ERROR"
            metric = str(e)[:20]
            print(f"{status} {category:<20} {metric:<15}")
            results[category] = {
                "status": "error",
                "error": str(e)
            }
    
    # Calculate summary
    total_tests = len(test_categories)
    passed_tests = sum(1 for result in results.values() if result.get("status") == "pass")
    failed_tests = total_tests - passed_tests
    
    if total_tests > 0:
        success_rate = (passed_tests / total_tests) * 100
    else:
        success_rate = 0
    
    print()
    print("=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! Backend is performing exceptionally well!")
    elif success_rate >= 80:
        print("✅ GOOD! Backend is performing well with minor issues.")
    elif success_rate >= 70:
        print("⚠️ FAIR! Backend has some issues that need attention.")
    else:
        print("❌ POOR! Backend has significant issues that need immediate attention.")
    
    # Save results
    with open("ec2_test_monitor_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate
            }
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: ec2_test_monitor_results.json")

if __name__ == "__main__":
    monitor_ec2_tests() 