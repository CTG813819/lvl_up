import pytest
import requests

# Set your backend base URL here
BASE_URL = "http://ec2-34-202-215-209.compute-1.amazonaws.com:4000"

ENDPOINTS = [
    ("Health", "/health", "GET"),
    ("API Health", "/api/health", "GET"),
    ("Debug", "/debug", "GET"),
    ("App Status", "/api/app/status", "GET"),
    ("Agents Status", "/api/agents/status", "GET"),
    ("Agents Run All", "/api/agents/run-all", "POST"),
    ("Agents Autonomous Status", "/api/agents/autonomous/status", "GET"),
    ("Growth Status", "/api/growth/status", "GET"),
    ("Growth Analysis Imperium", "/api/growth/analysis/Imperium", "GET"),
    ("Growth Auto-Improve", "/api/growth/auto-improve", "POST"),
    ("Conquest Status", "/api/conquest/status", "GET"),
    ("Learning Data", "/api/learning/data", "GET"),
    ("Oath Papers", "/api/oath-papers/", "GET"),
    ("Oath Papers AI Insights", "/api/oath-papers/ai-insights", "GET"),
    ("Proposals", "/api/proposals/", "GET"),
    ("Codex", "/api/codex/", "GET"),
    ("GitHub Status", "/api/github/status", "GET"),
]

@pytest.mark.parametrize("name,path,method", ENDPOINTS)
def test_endpoint(name, path, method):
    url = BASE_URL + path
    if method == "POST":
        resp = requests.post(url, json={})
    else:
        resp = requests.get(url)
    status = resp.status_code
    ok = 200 <= status < 300
    print(f"[{name}] {url} => {status} {'\u2705' if ok else '\u274c'}")
    if not ok:
        print(f"  Response: {resp.text}")
    assert ok, f"{name} failed with status {status}: {resp.text}" 