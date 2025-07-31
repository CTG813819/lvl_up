import requests
import time
import asyncio
import websockets
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ValidationError

# === CONFIGURATION ===
BASE_URL = "http://localhost:8000"  # Change to your backend URL
AUTH_TOKEN = None  # Set to your Bearer token if needed, else None
HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"} if AUTH_TOKEN else {}
TIMEOUT = 10

# === SCHEMA MODELS ===
class StatusResponse(BaseModel):
    status: str
    data: Optional[dict] = None  # Make data optional

class ProposalsListResponse(BaseModel):
    status: str
    proposals: list

class NotifyTemplatesResponse(BaseModel):
    status: str
    data: dict

class LearningDataResponse(BaseModel):
    Imperium: Optional[dict] = None
    Guardian: Optional[dict] = None
    Sandbox: Optional[dict] = None
    Conquest: Optional[dict] = None  # Make Conquest optional

class AnalyticsResponse(BaseModel):
    status: str
    data: Optional[dict] = None

# Add new schema for oath-papers
class OathPapersResponse(BaseModel):
    papers: Optional[list] = None
    status: Optional[str] = None

# === COMPREHENSIVE ENDPOINTS TO TEST ===
ENDPOINTS = [
    # === IMPERIUM ===
    ("GET", "/api/imperium/", dict, None, None),
    ("GET", "/api/imperium/monitoring", dict, None, None),
    ("GET", "/api/imperium/improvements", dict, None, None),
    ("GET", "/api/imperium/issues", dict, None, None),
    ("POST", "/api/imperium/trigger-scan", dict, None, None),
    ("GET", "/api/imperium/status", StatusResponse, None, None),
    ("GET", "/api/imperium/proposals", ProposalsListResponse, lambda r: len(r.get("proposals", [])) > 0, None),
    ("POST", "/api/imperium/proposals/{proposal_id}/approve", dict, None, {"source": "/api/imperium/proposals", "key": "id"}),
    ("POST", "/api/imperium/proposals/{proposal_id}/reject", dict, None, {"source": "/api/imperium/proposals", "key": "id"}),
    ("POST", "/api/imperium/agents/{agent_id}/approve", dict, None, {"agent_id": "imperium"}),
    ("POST", "/api/imperium/agents/{agent_id}/reject", dict, None, {"agent_id": "guardian"}),
    ("GET", "/api/imperium/growth", dict, None, None),
    ("GET", "/api/imperium/growth/all", dict, None, None),
    ("POST", "/api/imperium/persistence/learning-analytics", dict, None, None),
    ("GET", "/api/imperium/persistence/learning-analytics", dict, None, None),
    
    # === GUARDIAN ===
    ("GET", "/api/guardian/", dict, None, None),
    ("GET", "/api/guardian/security-status", dict, None, None),
    ("GET", "/api/guardian/code-review", dict, None, None),
    ("POST", "/api/guardian/review/{proposal_id}", dict, None, {"source": "/api/proposals/", "key": "id"}),
    ("GET", "/api/guardian/threat-detection", dict, None, None),
    ("GET", "/api/guardian/vulnerability-scan", dict, None, None),
    ("GET", "/api/guardian/access-control", dict, None, None),
    ("POST", "/api/guardian/health-check", dict, None, None),
    ("GET", "/api/guardian/suggestions", dict, None, None),
    ("POST", "/api/guardian/suggestions/{suggestion_id}/approve", dict, None, {"source": "/api/guardian/suggestions", "key": "id"}),
    ("POST", "/api/guardian/suggestions/{suggestion_id}/reject", dict, None, {"source": "/api/guardian/suggestions", "key": "id"}),
    ("GET", "/api/guardian/suggestions/statistics", dict, None, None),
    ("GET", "/api/guardian/health-status", dict, None, None),
    
    # === SANDBOX ===
    ("GET", "/api/sandbox/", dict, None, None),
    ("GET", "/api/sandbox/experiments", dict, None, None),
    ("GET", "/api/sandbox/testing-status", dict, None, None),
    ("GET", "/api/sandbox/performance-metrics", dict, None, None),
    ("GET", "/api/sandbox/integration-status", dict, None, None),
    
    # === CONQUEST ===
    ("GET", "/api/conquest/", dict, None, None),
    ("GET", "/api/conquest/status", dict, None, None),
    ("GET", "/api/conquest/statistics", dict, None, None),
    ("GET", "/api/conquest/enhanced-statistics", dict, None, None),
    ("GET", "/api/conquest/deployments", dict, None, None),
    ("GET", "/api/conquest/progress-logs", dict, None, None),
    ("POST", "/api/conquest/analyze-suggestion", dict, None, None),
    
    # === LEARNING ===
    ("GET", "/api/learning/stats/Imperium", dict, None, None),
    ("GET", "/api/learning/stats/Guardian", dict, None, None),
    ("GET", "/api/learning/stats/Sandbox", dict, None, None),
    ("GET", "/api/learning/stats/Conquest", dict, None, None),
    ("GET", "/api/learning/insights/Imperium", dict, None, None),
    ("GET", "/api/learning/insights/Guardian", dict, None, None),
    ("GET", "/api/learning/insights/Sandbox", dict, None, None),
    ("GET", "/api/learning/insights/Conquest", dict, None, None),
    ("POST", "/api/learning/train", dict, None, None),
    ("GET", "/api/learning/ml-insights", dict, None, None),
    ("GET", "/api/learning/data", LearningDataResponse, lambda r: isinstance(r, dict) and len(r) > 0, None),
    ("GET", "/api/learning/metrics", dict, None, None),
    ("GET", "/api/learning/status", dict, None, None),
    ("GET", "/api/learning/debug-log", dict, None, None),
    ("GET", "/api/learning/periodic-learning-status", dict, None, None),
    ("POST", "/api/learning/trigger-periodic-learning", dict, None, None),
    ("GET", "/api/learning/insights", dict, None, None),
    
    # === PROPOSALS ===
    ("GET", "/api/proposals/", list, None, None),
    ("GET", "/api/proposals/ai-status", dict, None, None),
    ("GET", "/api/proposals/stats/summary", dict, None, None),
    ("GET", "/api/proposals/{proposal_id}", dict, None, {"source": "/api/proposals/", "key": "id"}),
    ("POST", "/api/proposals/{proposal_id}/accept", dict, None, {"source": "/api/proposals/", "key": "id"}),
    ("POST", "/api/proposals/{proposal_id}/reject", dict, None, {"source": "/api/proposals/", "key": "id"}),
    ("PUT", "/api/proposals/{proposal_id}", dict, None, {"source": "/api/proposals/", "key": "id"}),
    ("DELETE", "/api/proposals/{proposal_id}", dict, None, {"source": "/api/proposals/", "key": "id"}),
    
    # === NOTIFY ===
    ("GET", "/api/notify/", dict, None, None),
    ("POST", "/api/notify/send", dict, None, None),
    ("GET", "/api/notify/templates", NotifyTemplatesResponse, lambda r: len(r.get("data", {}).get("templates", [])) > 0, None),
    ("GET", "/api/notify/channels", dict, None, None),
    ("GET", "/api/notify/stats", dict, None, None),
    
    # === ANALYTICS ===
    ("GET", "/api/analytics/", dict, None, None),
    ("GET", "/api/analytics/ai-learning-metrics", AnalyticsResponse, None, None),
    
    # === CODE ===
    ("GET", "/api/code/analysis", dict, None, None),
    
    # === APPROVAL ===
    ("GET", "/api/approval/", dict, None, None),
    
    # === OATH PAPERS ===
    ("GET", "/api/oath-papers/", list, None, None),  # Returns a list, not dict
    ("GET", "/api/oath-papers/ai-insights", dict, None, None),
    
    # === AGENTS ===
    ("POST", "/api/agents/run-all", dict, None, None),
    ("GET", "/api/agents/cycle-status", dict, None, None),
    
    # === GROWTH ===
    ("GET", "/api/growth/status", dict, None, None),
    ("GET", "/api/growth/insights", dict, None, None),
    
    # === NOTIFICATIONS ===
    ("GET", "/api/notifications/", dict, None, None),
    
    # === MISSIONS ===
    ("GET", "/api/missions/", dict, None, None),
    
    # === EXPERIMENTS ===
    ("GET", "/api/experiments/", dict, None, None),
    
    # === GITHUB ===
    ("GET", "/api/github/", dict, None, None),
    ("GET", "/api/github/status", dict, None, None),
    
    # === CODEX ===
    ("GET", "/api/codex/", dict, None, None),
    
    # === PLUGIN ===
    ("GET", "/api/plugins/", dict, None, None),
]

# === WEBSOCKET ENDPOINTS ===
WEBSOCKETS = [
    ("ws://localhost:8000/ws/imperium/learning-analytics", "test message"),
    ("ws://localhost:8000/api/notifications/ws", "test notification"),
]

# === MINIMAL PAYLOADS FOR POST/PUT ===
PAYLOADS = {
    "/api/notify/send": {
        "title": "Test Notification",
        "message": "This is a test notification.",
        "channel": "system",
        "priority": "normal"
    },
    "/api/conquest/analyze-suggestion": {
        "name": "Test App",
        "description": "A test app for endpoint validation.",
        "keywords": ["test", "validation"],
        "app_type": "general",
        "features": ["feature1", "feature2"],
        "operation_type": "create_new"
    },
    "/api/guardian/review/{proposal_id}": {},
    "/api/guardian/suggestions/{suggestion_id}/approve": {"user_feedback": "test"},
    "/api/guardian/suggestions/{suggestion_id}/reject": {"user_feedback": "test"},
    "/api/imperium/persistence/learning-analytics": {},
    "/api/learning/train": {},
    "/api/learning/trigger-periodic-learning": {},
    "/api/agents/run-all": {},
    "/api/imperium/trigger-scan": {},
    "/api/guardian/health-check": {},
    "/api/proposals/{proposal_id}/accept": {},
    "/api/proposals/{proposal_id}/reject": {},
    "/api/proposals/{proposal_id}": {"status": "updated"},
    "/api/imperium/proposals/{proposal_id}/approve": {},
    "/api/imperium/proposals/{proposal_id}/reject": {},
    "/api/imperium/agents/{agent_id}/approve": {},
    "/api/imperium/agents/{agent_id}/reject": {},
}

# === UTILITY FUNCTIONS ===
def fetch_id(source_path: str, key: str) -> Optional[str]:
    url = BASE_URL + source_path
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        data = resp.json()
        if isinstance(data, list) and data:
            return str(data[0].get(key))
        elif isinstance(data, dict):
            proposals = data.get("proposals")
            if isinstance(proposals, list) and proposals:
                return str(proposals[0].get(key))
        return None
    except Exception as e:
        print(f"  [ID Discovery] Failed to fetch ID from {url}: {e}")
        return None

def validate_schema(schema, data):
    if schema is None:
        return True, None
    if schema is dict:
        return isinstance(data, dict), None
    if schema is list:
        return isinstance(data, list), None
    try:
        schema.model_validate(data)  # Use model_validate instead of parse_obj
        return True, None
    except ValidationError as ve:
        return False, str(ve)

def test_endpoint(method, path, schema=None, custom_check=None, param_discovery=None):
    # Handle param discovery
    if param_discovery:
        if isinstance(param_discovery, dict) and "source" in param_discovery:
            discovered_id = fetch_id(param_discovery["source"], param_discovery["key"])
            if not discovered_id:
                print(f"  [SKIP] Could not discover ID for {path}")
                return False, "id_discovery_failed", 0
            path = path.replace("{proposal_id}", discovered_id).replace("{suggestion_id}", discovered_id)
        elif isinstance(param_discovery, dict) and "agent_id" in param_discovery:
            path = path.replace("{agent_id}", param_discovery["agent_id"])
    
    url = BASE_URL + path
    start = time.time()
    
    # Get payload for POST/PUT requests
    payload = None
    if method in ["POST", "PUT"]:
        payload = PAYLOADS.get(path, {})
    
    try:
        resp = requests.request(method, url, headers=HEADERS, json=payload, timeout=TIMEOUT)
        elapsed = time.time() - start
        print(f"{method} {url} -> {resp.status_code} ({elapsed:.2f}s)")
        if 200 <= resp.status_code < 300:
            try:
                data = resp.json()
            except Exception:
                print("  ❌ Response is not valid JSON")
                return False, "not_json", elapsed
            valid, err = validate_schema(schema, data)
            if not valid:
                print(f"  ❌ Schema validation failed: {err}")
                return False, "schema", elapsed
            if custom_check:
                try:
                    if not custom_check(data):
                        print("  ⚠️  Custom check failed (possible stub or empty data)")
                        return False, "custom_check", elapsed
                except Exception as e:
                    print(f"  ⚠️  Custom check error: {e}")
                    return False, "custom_check_error", elapsed
            print("  ✅ Passed")
            return True, "ok", elapsed
        else:
            print(f"  ❌ HTTP error: {resp.status_code}")
            return False, "http", elapsed
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False, "exception", 0

async def test_websocket(ws_url, test_message):
    print(f"WebSocket {ws_url}")
    try:
        async with websockets.connect(ws_url) as websocket:
            await websocket.send(test_message)
            response = await websocket.recv()
            print(f"  ✅ Received: {response}")
            return True
    except Exception as e:
        print(f"  ❌ WebSocket error: {e}")
        return False

def main():
    print("\n=== HTTP Endpoint Tests ===\n")
    results = []
    for entry in ENDPOINTS:
        method, path, schema, custom_check, param_discovery = entry
        print("-"*60)
        ok, reason, elapsed = test_endpoint(method, path, schema, custom_check, param_discovery)
        results.append((path, ok, reason, elapsed))
    
    print("\n=== WebSocket Tests ===\n")
    ws_results = []
    for ws_url, test_message in WEBSOCKETS:
        ok = asyncio.run(test_websocket(ws_url, test_message))  # Use asyncio.run instead
        ws_results.append((ws_url, ok))
    
    print("\n=== SUMMARY ===\n")
    passed = sum(1 for r in results if r[1])
    failed = len(results) - passed
    print(f"HTTP Endpoints: {passed} passed, {failed} failed")
    for path, ok, reason, elapsed in results:
        if not ok:
            print(f"  ❌ {path} failed: {reason}")
    
    ws_passed = sum(1 for r in ws_results if r[1])
    ws_failed = len(ws_results) - ws_passed
    print(f"WebSockets: {ws_passed} passed, {ws_failed} failed")
    for ws_url, ok in ws_results:
        if not ok:
            print(f"  ❌ {ws_url} failed")

if __name__ == "__main__":
    main() 