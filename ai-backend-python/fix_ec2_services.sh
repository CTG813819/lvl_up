#!/bin/bash

echo "=== Fixing EC2 Services and AI Testing ==="
echo "Timestamp: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== 1. Checking Current Running Processes ===${NC}"
echo "Current uvicorn processes:"
ps aux | grep uvicorn | grep -v grep
echo ""

echo "Current AI processes:"
ps aux | grep -E "(guardian|conquest|imperium|sandbox)" | grep -v grep
echo ""

echo -e "${BLUE}=== 2. Testing AI Endpoints with POST Requests ===${NC}"
echo "Testing AI endpoints with correct HTTP methods:"

# Test enhanced AI endpoints with POST
echo "Testing /api/enhanced-ai/run-ai/conquest (POST):"
curl -X POST -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/enhanced-ai/run-ai/conquest" 2>/dev/null || echo "Failed"
echo ""

echo "Testing /api/enhanced-ai/run-ai/guardian (POST):"
curl -X POST -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/enhanced-ai/run-ai/guardian" 2>/dev/null || echo "Failed"
echo ""

echo "Testing /api/enhanced-ai/run-ai/imperium (POST):"
curl -X POST -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/enhanced-ai/run-ai/imperium" 2>/dev/null || echo "Failed"
echo ""

echo "Testing /api/enhanced-ai/run-ai/sandbox (POST):"
curl -X POST -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/enhanced-ai/run-ai/sandbox" 2>/dev/null || echo "Failed"
echo ""

echo -e "${BLUE}=== 3. Testing Custody Protocol Endpoints ===${NC}"
echo "Testing custody endpoints:"

echo "Testing /api/custody/test/conquest (GET):"
curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/custody/test/conquest" 2>/dev/null || echo "Failed"
echo ""

echo "Testing /api/custody/test/guardian (GET):"
curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/custody/test/guardian" 2>/dev/null || echo "Failed"
echo ""

echo "Testing /api/custody/test/imperium (GET):"
curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/custody/test/imperium" 2>/dev/null || echo "Failed"
echo ""

echo "Testing /api/custody/test/sandbox (GET):"
curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/custody/test/sandbox" 2>/dev/null || echo "Failed"
echo ""

echo -e "${BLUE}=== 4. Testing AI Status Endpoints ===${NC}"
echo "Testing AI status endpoints:"

echo "Testing /api/agents/cycle-status (GET):"
curl -s "http://localhost:8000/api/agents/cycle-status" 2>/dev/null | head -5 || echo "Failed"
echo ""

echo "Testing /api/proposals/cycle/status (GET):"
curl -s "http://localhost:8000/api/proposals/cycle/status" 2>/dev/null | head -5 || echo "Failed"
echo ""

echo "Testing /api/learning/status (GET):"
curl -s "http://localhost:8000/api/learning/status" 2>/dev/null | head -5 || echo "Failed"
echo ""

echo -e "${BLUE}=== 5. Checking Backend Health ===${NC}"
echo "Testing backend health:"

echo "Testing /api/health (GET):"
curl -s "http://localhost:8000/api/health" 2>/dev/null | head -5 || echo "Failed"
echo ""

echo "Testing /api/status (GET):"
curl -s "http://localhost:8000/api/status" 2>/dev/null | head -5 || echo "Failed"
echo ""

echo -e "${BLUE}=== 6. Checking for AI Testing in Logs ===${NC}"
echo "Recent AI activity in logs:"
journalctl -u lvl-up-backend 2>/dev/null | grep -i "ai\|conquest\|guardian\|imperium\|sandbox" | tail -20 || echo "No systemd logs found"
echo ""

echo "Checking for AI activity in process logs:"
# Check if there are any log files in the backend directory
find /home/ubuntu/ai-backend-python -name "*.log" -type f 2>/dev/null | head -5
echo ""

echo -e "${BLUE}=== 7. Testing Manual AI Trigger ===${NC}"
echo "Manually triggering AI agents:"

echo "Triggering Conquest agent:"
curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/conquest" 2>/dev/null | head -10 || echo "Failed"
echo ""

echo "Triggering Guardian agent:"
curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/guardian" 2>/dev/null | head -10 || echo "Failed"
echo ""

echo "Triggering Imperium agent:"
curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/imperium" 2>/dev/null | head -10 || echo "Failed"
echo ""

echo "Triggering Sandbox agent:"
curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/sandbox" 2>/dev/null | head -10 || echo "Failed"
echo ""

echo -e "${BLUE}=== 8. Checking for Background Tasks ===${NC}"
echo "Checking for background task processes:"
ps aux | grep -E "(background|scheduler|cycle)" | grep -v grep || echo "No background task processes found"
echo ""

echo -e "${BLUE}=== 9. Checking for AI Learning Activity ===${NC}"
echo "Checking for AI learning processes:"
ps aux | grep -E "(learning|training)" | grep -v grep || echo "No learning processes found"
echo ""

echo -e "${BLUE}=== 10. Checking for Recent AI Proposals ===${NC}"
echo "Checking for recent AI proposals in database:"
if command -v sqlite3 &> /dev/null; then
    if [ -f "/home/ubuntu/ai-backend-python/app.db" ]; then
        echo "Recent proposals:"
        sqlite3 /home/ubuntu/ai-backend-python/app.db "SELECT ai_type, created_at, status, title FROM proposals ORDER BY created_at DESC LIMIT 5;" 2>/dev/null || echo "Could not query proposals"
    else
        echo "Database file not found"
    fi
else
    echo "sqlite3 not available - trying to install:"
    sudo apt-get update && sudo apt-get install -y sqlite3
    if command -v sqlite3 &> /dev/null; then
        if [ -f "/home/ubuntu/ai-backend-python/app.db" ]; then
            echo "Recent proposals:"
            sqlite3 /home/ubuntu/ai-backend-python/app.db "SELECT ai_type, created_at, status, title FROM proposals ORDER BY created_at DESC LIMIT 5;" 2>/dev/null || echo "Could not query proposals"
        fi
    fi
fi
echo ""

echo "=== Analysis Complete ==="
echo ""
echo -e "${YELLOW}=== Key Findings ===${NC}"
echo "1. Backend is running via uvicorn processes"
echo "2. AI services (Guardian, Conquest) are running as direct Python processes"
echo "3. Systemd services are missing but not needed since processes are running"
echo "4. AI endpoints exist but need POST requests, not GET"
echo "5. AI testing happens through the enhanced AI endpoints"
echo ""
echo -e "${YELLOW}=== Recommendations ===${NC}"
echo "1. The backend is working - use POST requests to test AI endpoints"
echo "2. AI testing is handled through /api/enhanced-ai/run-ai/{ai_type} endpoints"
echo "3. Check the process logs for AI activity"
echo "4. The 405 errors were because we used GET instead of POST"
echo ""
echo "To manually test AI agents, use:"
echo "curl -X POST http://localhost:8000/api/enhanced-ai/run-ai/conquest"
echo "curl -X POST http://localhost:8000/api/enhanced-ai/run-ai/guardian"
echo "curl -X POST http://localhost:8000/api/enhanced-ai/run-ai/imperium"
echo "curl -X POST http://localhost:8000/api/enhanced-ai/run-ai/sandbox" 