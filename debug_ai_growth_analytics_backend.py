#!/usr/bin/env python3
"""
Debug AI Growth Analytics Backend
=================================

This script tests all backend endpoints that provide data for the AI Growth Analytics dashboard
to identify why the data is not updating or displaying correctly.

Endpoints tested:
- /api/imperium/growth/all (Growth Scores)
- /api/learning/data (Recent Activity)
- /api/agents/status (AI Agent Status)
- /api/imperium/internet-learning/log (Current Learnings)
- /api/imperium/internet-learning/impact (Learning Impact)
- /api/learning/insights/{ai_type} (Learning Insights)
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, List
import sys

# Backend configuration
BACKEND_BASE_URL = "http://ec2-34-202-215-209.compute-1.amazonaws.com:4000"

# Endpoints to test
ENDPOINTS = {
    "growth_all": "/api/imperium/growth/all",
    "learning_data": "/api/learning/data", 
    "agents_status": "/api/agents/status",
    "internet_learning_log": "/api/imperium/internet-learning/log",
    "internet_learning_impact": "/api/imperium/internet-learning/impact",
    "learning_insights_imperium": "/api/learning/insights/Imperium",
    "learning_insights_guardian": "/api/learning/insights/Guardian",
    "learning_insights_sandbox": "/api/learning/insights/Sandbox",
    "learning_insights_conquest": "/api/learning/insights/Conquest",
}

async def test_endpoint(session: aiohttp.ClientSession, name: str, endpoint: str) -> Dict[str, Any]:
    """Test a single endpoint and return results"""
    url = f"{BACKEND_BASE_URL}{endpoint}"
    print(f"\n🔍 Testing {name}: {url}")
    
    try:
        async with session.get(url, timeout=30) as response:
            status = response.status
            if status == 200:
                data = await response.json()
                print(f"✅ {name}: Status {status}")
                print(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Analyze data structure and content
                if isinstance(data, dict):
                    if name == "growth_all":
                        analyze_growth_data(data)
                    elif name == "learning_data":
                        analyze_learning_data(data)
                    elif name == "agents_status":
                        analyze_agents_status(data)
                    elif name == "internet_learning_log":
                        analyze_internet_learning_log(data)
                    elif name == "internet_learning_impact":
                        analyze_internet_learning_impact(data)
                    elif name.startswith("learning_insights"):
                        analyze_learning_insights(data, name)
                
                return {"status": "success", "data": data, "status_code": status}
            else:
                print(f"❌ {name}: Status {status}")
                error_text = await response.text()
                print(f"   Error: {error_text}")
                return {"status": "error", "status_code": status, "error": error_text}
                
    except Exception as e:
        print(f"❌ {name}: Exception {type(e).__name__}: {str(e)}")
        return {"status": "error", "exception": str(e)}

def analyze_growth_data(data: Dict[str, Any]):
    """Analyze growth data structure"""
    print("   📊 Growth Data Analysis:")
    
    if "ai_growth_insights" in data:
        insights = data["ai_growth_insights"]
        print(f"   - AI Growth Insights: {list(insights.keys())}")
        
        for ai_type, insight in insights.items():
            if isinstance(insight, dict):
                growth_potential = insight.get("growth_potential", {})
                current_performance = insight.get("current_performance", {})
                
                growth_score = growth_potential.get("growth_score", "N/A")
                growth_stage = growth_potential.get("growth_stage", "N/A")
                avg_confidence = current_performance.get("avg_confidence", "N/A")
                approval_rate = current_performance.get("approval_rate", "N/A")
                
                print(f"     {ai_type}: Score={growth_score}, Stage={growth_stage}, Confidence={avg_confidence}, Approval={approval_rate}")
    
    if "overall_growth" in data:
        overall = data["overall_growth"]
        system_maturity = overall.get("system_maturity", "N/A")
        avg_growth_score = overall.get("average_growth_score", "N/A")
        total_learning = overall.get("total_learning_entries", "N/A")
        opportunities = overall.get("total_expansion_opportunities", "N/A")
        
        print(f"   - Overall: Maturity={system_maturity}, AvgScore={avg_growth_score}, Learning={total_learning}, Opportunities={opportunities}")

def analyze_learning_data(data: Dict[str, Any]):
    """Analyze learning data structure"""
    print("   📚 Learning Data Analysis:")
    
    # Check for expected structure based on frontend expectations
    expected_keys = ["userFeedback", "backendTestResults", "lessons"]
    found_keys = []
    
    for key in expected_keys:
        if key in data:
            found_keys.append(key)
            items = data[key] if isinstance(data[key], list) else []
            print(f"   - {key}: {len(items)} items")
        else:
            print(f"   - {key}: MISSING")
    
    if not found_keys:
        print("   ⚠️  No expected learning data keys found!")
        print(f"   Available keys: {list(data.keys())}")

def analyze_agents_status(data: Dict[str, Any]):
    """Analyze agents status data"""
    print("   🤖 Agents Status Analysis:")
    
    if "agents" in data:
        agents = data["agents"]
        print(f"   - Agents: {list(agents.keys())}")
        
        for agent, status in agents.items():
            if isinstance(status, dict):
                agent_status = status.get("status", "unknown")
                last_run = status.get("last_run", "unknown")
                print(f"     {agent}: Status={agent_status}, LastRun={last_run}")
    
    autonomous_running = data.get("autonomous_cycle_running", False)
    print(f"   - Autonomous Cycle Running: {autonomous_running}")

def analyze_internet_learning_log(data: Dict[str, Any]):
    """Analyze internet learning log data"""
    print("   🌐 Internet Learning Log Analysis:")
    
    if "log" in data:
        log_entries = data["log"]
        print(f"   - Log entries: {len(log_entries)}")
        
        if log_entries:
            # Show last few entries
            for i, entry in enumerate(log_entries[-3:], 1):
                if isinstance(entry, dict):
                    agent_id = entry.get("agent_id", "unknown")
                    topic = entry.get("topic", "unknown")
                    timestamp = entry.get("timestamp", "unknown")
                    print(f"     Entry {i}: Agent={agent_id}, Topic={topic}, Time={timestamp}")
        else:
            print("   ⚠️  No log entries found!")
    else:
        print("   ⚠️  No 'log' key found in response!")

def analyze_internet_learning_impact(data: Dict[str, Any]):
    """Analyze internet learning impact data"""
    print("   📈 Internet Learning Impact Analysis:")
    
    if "impact" in data:
        impact = data["impact"]
        print(f"   - Impact keys: {list(impact.keys())}")
        
        for agent, agent_impact in impact.items():
            if isinstance(agent_impact, dict):
                suggestions = agent_impact.get("improvement_suggestions", [])
                print(f"     {agent}: {len(suggestions)} suggestions")
    else:
        print("   ⚠️  No 'impact' key found in response!")

def analyze_learning_insights(data: Dict[str, Any], endpoint_name: str):
    """Analyze learning insights data"""
    ai_type = endpoint_name.split("_")[-1]
    print(f"   💡 Learning Insights Analysis for {ai_type}:")
    
    if "recommendations" in data:
        recommendations = data["recommendations"]
        print(f"   - Recommendations: {len(recommendations)} items")
        if recommendations:
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"     {i}. {rec}")
    else:
        print("   ⚠️  No 'recommendations' key found!")

async def main():
    """Main diagnostic function"""
    print("🚀 AI Growth Analytics Backend Diagnostic")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    results = {}
    
    async with aiohttp.ClientSession() as session:
        # Test all endpoints
        for name, endpoint in ENDPOINTS.items():
            result = await test_endpoint(session, name, endpoint)
            results[name] = result
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    success_count = 0
    error_count = 0
    
    for name, result in results.items():
        if result["status"] == "success":
            success_count += 1
            print(f"✅ {name}: OK")
        else:
            error_count += 1
            print(f"❌ {name}: FAILED")
    
    print(f"\nResults: {success_count} successful, {error_count} failed")
    
    # Recommendations
    print("\n" + "=" * 50)
    print("🔧 RECOMMENDATIONS")
    print("=" * 50)
    
    if error_count > 0:
        print("1. Fix failing endpoints first")
        print("2. Check backend logs for errors")
        print("3. Verify database connections")
    
    if success_count > 0:
        print("4. Check if endpoints return meaningful data")
        print("5. Verify data structure matches frontend expectations")
        print("6. Test with real data generation")
    
    print("\n7. Restart backend services if needed")
    print("8. Check database for empty tables")
    print("9. Verify AI agents are actually running and generating data")

if __name__ == "__main__":
    asyncio.run(main()) 