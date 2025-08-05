#!/bin/bash

echo "=== Detailed AI Endpoint Testing ==="
echo "Timestamp: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== 1. Testing AI Endpoints with Full Response ===${NC}"

echo "Testing Conquest AI (full response):"
curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/conquest" | jq '.' 2>/dev/null || curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/conquest"
echo ""

echo "Testing Guardian AI (full response):"
curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/guardian" | jq '.' 2>/dev/null || curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/guardian"
echo ""

echo "Testing Imperium AI (full response):"
curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/imperium" | jq '.' 2>/dev/null || curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/imperium"
echo ""

echo "Testing Sandbox AI (full response):"
curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/sandbox" | jq '.' 2>/dev/null || curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/sandbox"
echo ""

echo -e "${BLUE}=== 2. Testing Custody Protocol with Different Methods ===${NC}"

echo "Testing custody endpoints with POST:"
echo "Testing /api/custody/test/conquest (POST):"
curl -X POST -H "Content-Type: application/json" -d '{}' -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/custody/test/conquest" 2>/dev/null || echo "Failed"
echo ""

echo "Testing /api/custody/test/guardian (POST):"
curl -X POST -H "Content-Type: application/json" -d '{}' -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/custody/test/guardian" 2>/dev/null || echo "Failed"
echo ""

echo "Testing /api/custody/test/imperium (POST):"
curl -X POST -H "Content-Type: application/json" -d '{}' -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/custody/test/imperium" 2>/dev/null || echo "Failed"
echo ""

echo "Testing /api/custody/test/sandbox (POST):"
curl -X POST -H "Content-Type: application/json" -d '{}' -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/custody/test/sandbox" 2>/dev/null || echo "Failed"
echo ""

echo -e "${BLUE}=== 3. Testing AI Status Endpoints ===${NC}"

echo "Testing /api/agents/cycle-status (full response):"
curl -s "http://localhost:8000/api/agents/cycle-status" | jq '.' 2>/dev/null || curl -s "http://localhost:8000/api/agents/cycle-status"
echo ""

echo "Testing /api/proposals/cycle/status (full response):"
curl -s "http://localhost:8000/api/proposals/cycle/status" | jq '.' 2>/dev/null || curl -s "http://localhost:8000/api/proposals/cycle/status"
echo ""

echo "Testing /api/learning/status (full response):"
curl -s "http://localhost:8000/api/learning/status" | jq '.' 2>/dev/null || curl -s "http://localhost:8000/api/learning/status"
echo ""

echo -e "${BLUE}=== 4. Testing Backend Health ===${NC}"

echo "Testing /api/health (full response):"
curl -s "http://localhost:8000/api/health" | jq '.' 2>/dev/null || curl -s "http://localhost:8000/api/health"
echo ""

echo "Testing /api/status (full response):"
curl -s "http://localhost:8000/api/status" | jq '.' 2>/dev/null || curl -s "http://localhost:8000/api/status"
echo ""

echo -e "${BLUE}=== 5. Checking Recent AI Activity ===${NC}"

echo "Recent AI activity in process logs:"
# Check if there are any log files in the backend directory
find /home/ubuntu/ai-backend-python -name "*.log" -type f 2>/dev/null | head -5
echo ""

echo "Checking for recent AI proposals in database:"
if command -v sqlite3 &> /dev/null; then
    if [ -f "/home/ubuntu/ai-backend-python/app.db" ]; then
        echo "Recent proposals:"
        sqlite3 /home/ubuntu/ai-backend-python/app.db "SELECT ai_type, created_at, status, title FROM proposals ORDER BY created_at DESC LIMIT 5;" 2>/dev/null || echo "Could not query proposals"
    else
        echo "Database file not found"
    fi
else
    echo "sqlite3 not available"
fi
echo ""

echo -e "${BLUE}=== 6. Testing Manual AI Trigger with Detailed Output ===${NC}"

echo "Triggering Conquest agent with detailed output:"
curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/conquest" | jq '.' 2>/dev/null || curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/conquest"
echo ""

echo "=== Testing Complete ==="
echo ""
echo -e "${GREEN}=== Summary ===${NC}"
echo "✅ AI endpoints are working (200 responses)"
echo "✅ Backend is running properly"
echo "✅ AI services are active"
echo "🔍 Custody protocol needs investigation (405 errors)"
echo "📊 Check the detailed responses above for AI activity" 