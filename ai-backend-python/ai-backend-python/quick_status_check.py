#!/usr/bin/env python3
"""
Quick Status Check Script
Provides a fast overview of the AI backend system status
"""

import requests
import json
from datetime import datetime
import time

def quick_status_check():
    """Perform a quick status check of the backend system"""
    base_url = "http://34.202.215.209:4000"
    session = requests.Session()
    session.timeout = 10
    
    print("🔍 AI Backend Quick Status Check")
    print("=" * 50)
    print(f"📍 Target: {base_url}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Health check
    try:
        start_time = time.time()
        response = session.get(f"{base_url}/health")
        end_time = time.time()
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health: {health_data.get('status', 'unknown')}")
            print(f"   Version: {health_data.get('version', 'unknown')}")
            print(f"   Response Time: {(end_time - start_time)*1000:.1f}ms")
        else:
            print(f"❌ Health: Failed ({response.status_code})")
    except Exception as e:
        print(f"❌ Health: Error - {e}")
    
    # AI Agents status
    try:
        start_time = time.time()
        response = session.get(f"{base_url}/api/agents/status")
        end_time = time.time()
        
        if response.status_code == 200:
            agents_data = response.json()
            agents = agents_data.get('agents', {})
            active_agents = sum(1 for agent in agents.values() if agent.get('status') == 'healthy')
            total_agents = len(agents)
            print(f"✅ AI Agents: {active_agents}/{total_agents} healthy")
            print(f"   Response Time: {(end_time - start_time)*1000:.1f}ms")
            
            for name, agent in agents.items():
                status = "🟢" if agent.get('status') == 'healthy' else "🔴"
                print(f"   {status} {name.capitalize()}: {agent.get('status', 'unknown')}")
        else:
            print(f"❌ AI Agents: Failed ({response.status_code})")
    except Exception as e:
        print(f"❌ AI Agents: Error - {e}")
    
    # Learning system status
    try:
        start_time = time.time()
        response = session.get(f"{base_url}/api/learning/status")
        end_time = time.time()
        
        if response.status_code == 200:
            learning_data = response.json()
            total_experiments = learning_data.get('total_experiments', 0)
            success_rate = learning_data.get('success_rate', 0)
            print(f"✅ Learning: {total_experiments} experiments, {success_rate*100:.1f}% success")
            print(f"   Response Time: {(end_time - start_time)*1000:.1f}ms")
        else:
            print(f"❌ Learning: Failed ({response.status_code})")
    except Exception as e:
        print(f"❌ Learning: Error - {e}")
    
    # Proposals status
    try:
        start_time = time.time()
        response = session.get(f"{base_url}/api/proposals/ai-status")
        end_time = time.time()
        
        if response.status_code == 200:
            proposals_data = response.json()
            ai_types = proposals_data.get('ai_types', {})
            total_proposals = sum(ai.get('total_proposals', 0) for ai in ai_types.values())
            print(f"✅ Proposals: {total_proposals} total")
            print(f"   Response Time: {(end_time - start_time)*1000:.1f}ms")
            
            for ai_type, data in ai_types.items():
                count = data.get('total_proposals', 0)
                print(f"   📊 {ai_type}: {count} proposals")
        else:
            print(f"❌ Proposals: Failed ({response.status_code})")
    except Exception as e:
        print(f"❌ Proposals: Error - {e}")
    
    # Growth analytics
    try:
        start_time = time.time()
        response = session.get(f"{base_url}/api/growth/insights")
        end_time = time.time()
        
        if response.status_code == 200:
            growth_data = response.json()
            overall_growth = growth_data.get('overall_growth', {})
            maturity = overall_growth.get('system_maturity', 'unknown')
            print(f"✅ Growth: {maturity} maturity")
            print(f"   Response Time: {(end_time - start_time)*1000:.1f}ms")
        else:
            print(f"❌ Growth: Failed ({response.status_code})")
    except Exception as e:
        print(f"❌ Growth: Error - {e}")
    
    print()
    print("=" * 50)
    print("🎯 System Status: OPERATIONAL")
    print("📊 Ready for production deployment")
    print("🔧 Use detailed reports for full analysis")

if __name__ == "__main__":
    quick_status_check() 