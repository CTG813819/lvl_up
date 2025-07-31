import pytest
import requests
import time

BASE_URL = "http://34.202.215.209:8000/api/imperium"
AI_TYPES = ["imperium", "guardian", "sandbox", "conquest"]

@pytest.mark.parametrize("ai", AI_TYPES)
def test_agent_endpoints(ai):
    agent_id = f"test_{ai}_agent"
    # Register agent
    r = requests.post(f"{BASE_URL}/agents/register", json={"agent_id": agent_id, "agent_type": ai, "priority": "high"})
    assert r.status_code == 200
    # Get agent
    r = requests.get(f"{BASE_URL}/agents/{agent_id}")
    assert r.status_code == 200
    # Pause agent
    r = requests.post(f"{BASE_URL}/agents/{agent_id}/pause")
    assert r.status_code == 200
    # Resume agent
    r = requests.post(f"{BASE_URL}/agents/{agent_id}/resume")
    assert r.status_code == 200
    # Add topic
    r = requests.post(f"{BASE_URL}/agents/{agent_id}/topics", json={"topic": "AI Growth"})
    assert r.status_code == 200
    # Get all agents
    r = requests.get(f"{BASE_URL}/agents")
    assert r.status_code == 200
    # Get agent metrics
    r = requests.get(f"{BASE_URL}/agents/{agent_id}")
    assert r.status_code == 200
    # Persist agent metrics
    r = requests.post(f"{BASE_URL}/persistence/agent-metrics", json={"agent_id": agent_id})
    assert r.status_code == 200
    # Get persisted agent metrics
    r = requests.get(f"{BASE_URL}/persistence/agent-metrics?agent_id={agent_id}")
    assert r.status_code == 200
    # Get learning analytics
    r = requests.get(f"{BASE_URL}/persistence/learning-analytics?agent_id={agent_id}")
    assert r.status_code == 200
    # Log learning event
    r = requests.post(f"{BASE_URL}/persistence/log-learning-event", json={"event_type": "test_event", "agent_id": agent_id, "agent_type": ai, "topic": "AI Growth"})
    assert r.status_code == 200
    # Persist internet learning result
    r = requests.post(f"{BASE_URL}/persistence/internet-learning-result", json={"agent_id": agent_id, "topic": "AI Growth", "source": "test", "result": {"summary": "Test result"}})
    assert r.status_code == 200
    # Trigger internet learning
    r = requests.post(f"{BASE_URL}/internet-learning/trigger", json={})
    assert r.status_code == 200
    # Trigger agent internet learning
    r = requests.post(f"{BASE_URL}/internet-learning/agent/{agent_id}", json={"topic": "AI Growth"})
    assert r.status_code == 200
    # Get internet learning log
    r = requests.get(f"{BASE_URL}/internet-learning/log")
    assert r.status_code == 200
    # Get internet learning impact
    r = requests.get(f"{BASE_URL}/internet-learning/impact")
    assert r.status_code == 200
    # Get cycles
    r = requests.get(f"{BASE_URL}/cycles")
    assert r.status_code == 200
    # Trigger learning cycle
    r = requests.post(f"{BASE_URL}/cycles/trigger", json={})
    assert r.status_code == 200
    # Dashboard
    r = requests.get(f"{BASE_URL}/dashboard")
    assert r.status_code == 200
    # Trusted sources
    r = requests.get(f"{BASE_URL}/trusted-sources")
    assert r.status_code == 200
    r = requests.post(f"{BASE_URL}/trusted-sources", json={"url": f"https://{ai}.ai"})
    assert r.status_code == 200
    r = requests.delete(f"{BASE_URL}/trusted-sources", json={"url": f"https://{ai}.ai"})
    assert r.status_code == 200
    # Unregister agent
    r = requests.delete(f"{BASE_URL}/agents/{agent_id}")
    assert r.status_code == 200
    time.sleep(0.5) 