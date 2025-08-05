import requests
import time
import uuid
from typing import Optional

BASE_URL = "http://localhost:8000"  # Change if needed
TIMEOUT = 10

# Utility functions

def print_header(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)

def fetch_json(method, path, **kwargs):
    url = BASE_URL + path
    try:
        resp = requests.request(method, url, timeout=TIMEOUT, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  ❌ {method} {url} failed: {e}")
        return None

def create_proposal():
    print_header("Create Proposal")
    payload = {
        "ai_type": "Imperium",
        "file_path": f"test_{uuid.uuid4().hex[:8]}.py",
        "code_before": "print('Hello World')\n# TODO: Refactor this",
        "code_after": "print('Hello, Universe!')",
        "status": "pending",
        "improvement_type": "refactor",
        "confidence": 0.9
    }
    resp = fetch_json("POST", "/api/proposals/", json=payload)
    if resp and isinstance(resp, dict) and resp.get("id"):
        print(f"  ✅ Created proposal: {resp['id']}")
        return resp["id"]
    print("  ❌ Failed to create proposal")
    return None

def approve_proposal(proposal_id):
    print_header("Approve Proposal")
    resp = fetch_json("POST", f"/api/approval/approve/{proposal_id}", json={"approval_notes": "Looks good"})
    if resp and resp.get("status") == "success":
        print(f"  ✅ Approved proposal: {proposal_id}")
    else:
        print(f"  ❌ Failed to approve proposal: {proposal_id}")

def check_proposal_status(proposal_id):
    print_header("Check Proposal Status")
    resp = fetch_json("GET", f"/api/proposals/{proposal_id}")
    if resp:
        print(f"  Status: {resp.get('status')}")
        return resp.get('status')
    return None

def test_code_analysis():
    print_header("Test Code Analysis")
    resp = fetch_json("GET", "/api/code/analysis")
    if resp:
        print(f"  Code analysis data: {resp.get('data')}")

def test_experiments():
    print_header("Test Experiments")
    resp = fetch_json("GET", "/api/experiments/active")
    if resp:
        print(f"  Active experiments: {resp.get('data', {}).get('experiments')}")
    resp = fetch_json("GET", "/api/experiments/history")
    if resp:
        print(f"  Experiment history: {resp.get('data', {}).get('history')}")

def test_plugins():
    print_header("Test Plugins")
    resp = fetch_json("GET", "/api/plugins/")
    if resp:
        print(f"  Plugins: {resp.get('plugins')}")

def test_notify():
    print_header("Test Notify")
    payload = {
        "title": "Test Notification",
        "message": "This is a test notification.",
        "channel": "system",
        "priority": "normal"
    }
    # Try as JSON, fallback to params
    resp = fetch_json("POST", "/api/notify/send", json=payload)
    if not resp or resp.get("status") != "success":
        resp = fetch_json("POST", "/api/notify/send", params=payload)
    if resp:
        print(f"  Notify response: {resp}")

def test_proposal_to_approval_flow():
    print_header("Test Proposal to Approval Flow")
    proposal_id = create_proposal()
    if not proposal_id:
        return
    status_before = check_proposal_status(proposal_id)
    approve_proposal(proposal_id)
    status_after = check_proposal_status(proposal_id)
    if status_before != status_after:
        print(f"  ✅ Status changed from {status_before} to {status_after}")
    else:
        print(f"  ❌ Status did not change after approval")

def test_all():
    test_code_analysis()
    test_experiments()
    test_plugins()
    test_notify()
    test_proposal_to_approval_flow()

if __name__ == "__main__":
    test_all() 