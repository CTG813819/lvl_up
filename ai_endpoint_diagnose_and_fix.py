import requests
import json
from datetime import datetime

BACKEND_URL = "http://ec2-34-202-215-209.compute-1.amazonaws.com:4001"

# List of endpoints to test (GET by default)
ENDPOINTS = [
    # Imperium
    "/api/imperium/agents",
    "/api/imperium/status",
    "/api/imperium/dashboard",
    "/api/imperium/trusted-sources",
    "/api/imperium/internet-learning/topics",
    "/api/imperium/persistence/learning-analytics",
    "/api/imperium/growth",
    "/api/imperium/proposals",
    "/api/imperium/monitoring",
    "/api/imperium/issues",
    "/api/imperium/health",
    # Conquest
    "/api/conquest/statistics",
    "/api/conquest/enhanced-statistics",
    "/api/conquest/deployments",
    "/api/conquest/progress-logs",
    "/api/conquest/status",
    "/api/conquest/ai/imperium/learnings",
    "/api/conquest/ai/guardian/learnings",
    "/api/conquest/ai/sandbox/learnings",
    # Guardian
    "/api/guardian/suggestions",
    "/api/guardian/security-status",
    "/api/guardian/code-review",
    "/api/guardian/threat-detection",
    # Sandbox
    "/api/sandbox/experiments",
    "/api/sandbox/testing-status",
    "/api/sandbox/performance-metrics",
    "/api/sandbox/integration-status",
    # Oath Papers
    "/api/oath-papers/",
    "/api/oath-papers/categories",
    "/api/oath-papers/ai-insights",
    # Learning
    "/api/learning/data",
    "/api/learning/metrics",
    "/api/learning/status",
    "/api/learning/insights",
    # Growth
    "/api/growth/status",
    "/api/growth/insights",
    # Notifications
    "/api/notify/stats",
    "/api/notify/templates",
    "/api/notify/channels",
    # Proposals
    "/api/proposals/",
    "/api/proposals/ai-status",
    "/api/proposals/status",
]

METHODS = {
    # endpoint: method
    "/api/oath-papers/": "GET",
    "/api/proposals/": "GET",
}

def suggest_fix(endpoint, status_code, content):
    if status_code == 404:
        if endpoint.startswith("/api/conquest/"):
            return "404: Check conquest router registration in main.py and endpoint implementation in conquest.py."
        if endpoint.startswith("/api/imperium/"):
            return "404: Check imperium router registration in main.py and endpoint implementation in imperium.py."
        if endpoint.startswith("/api/guardian/"):
            return "404: Check guardian router registration in main.py and endpoint implementation in guardian.py."
        if endpoint.startswith("/api/sandbox/"):
            return "404: Check sandbox router registration in main.py and endpoint implementation in sandbox.py."
        if endpoint.startswith("/api/oath-papers/"):
            return "404: Check oath_papers router registration in main.py and endpoint implementation in oath_papers.py."
        if endpoint.startswith("/api/learning/"):
            return "404: Check learning router registration in main.py and endpoint implementation in learning.py."
        if endpoint.startswith("/api/growth/"):
            return "404: Check growth router registration in main.py and endpoint implementation in growth.py."
        if endpoint.startswith("/api/notify/"):
            return "404: Check notify router registration in main.py and endpoint implementation in notify.py."
        if endpoint.startswith("/api/proposals/"):
            return "404: Check proposals router registration in main.py and endpoint implementation in proposals.py."
        return "404: Check router registration and endpoint implementation."
    elif status_code == 405:
        return "405: Method Not Allowed. Check if the correct HTTP method is implemented for this endpoint."
    elif status_code == 500:
        return "500: Internal Server Error. Check backend logs for stack trace and fix the underlying bug."
    elif status_code == 422:
        return "422: Unprocessable Entity. Check request payload and backend validation logic."
    elif status_code == 401:
        return "401: Unauthorized. Check authentication/authorization requirements."
    elif status_code == 403:
        return "403: Forbidden. Check permissions and CORS settings."
    elif status_code == 'timeout':
        return "Timeout: Check if the endpoint is running, open in the firewall/security group, and not blocked by CORS."
    else:
        return f"{status_code}: Check endpoint implementation and backend logs."

def test_endpoint(endpoint, method="GET"):
    url = f"{BACKEND_URL}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, timeout=8)
        elif method == "POST":
            resp = requests.post(url, timeout=8)
        else:
            return {"endpoint": endpoint, "status_code": "unsupported", "fix": "Unsupported HTTP method."}
        content = resp.text
        if resp.status_code in [200, 201]:
            return {"endpoint": endpoint, "status_code": resp.status_code, "ok": True, "content": content}
        else:
            return {
                "endpoint": endpoint,
                "status_code": resp.status_code,
                "ok": False,
                "content": content[:200],
                "fix": suggest_fix(endpoint, resp.status_code, content)
            }
    except requests.Timeout:
        return {
            "endpoint": endpoint,
            "status_code": "timeout",
            "ok": False,
            "content": "Timeout",
            "fix": suggest_fix(endpoint, 'timeout', None)
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status_code": "error",
            "ok": False,
            "content": str(e),
            "fix": f"Error: {e}"
        }

def main():
    print("\n🚀 AI Endpoint Diagnose & Fix Script")
    print(f"Testing backend: {BACKEND_URL}")
    print(f"Started: {datetime.now().isoformat()}")
    results = []
    for endpoint in ENDPOINTS:
        method = METHODS.get(endpoint, "GET")
        print(f"\nTesting {method} {endpoint} ...", end=" ")
        result = test_endpoint(endpoint, method)
        if result.get("ok"):
            print("✅ OK")
        else:
            print(f"❌ {result['status_code']} - {result.get('fix','')}")
        results.append(result)
    # Save results
    with open("ai_endpoint_diagnose_results.json", "w") as f:
        json.dump(results, f, indent=2)
    # Print summary
    failed = [r for r in results if not r.get("ok")]
    print(f"\n\nSummary: {len(results)-len(failed)} OK, {len(failed)} failed.")
    if failed:
        print("\nActionable Fixes:")
        for r in failed:
            print(f"- {r['endpoint']}: {r['fix']}")
    print("\nDetailed results saved to ai_endpoint_diagnose_results.json")

if __name__ == "__main__":
    main() 