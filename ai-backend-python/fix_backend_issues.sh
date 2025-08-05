#!/bin/bash

echo "=== Fixing LVL UP Backend Issues ==="
echo "Timestamp: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== 1. Checking Current Backend Status ===${NC}"
if systemctl is-active --quiet lvl-up-backend; then
    echo -e "${GREEN}✓ Main backend is running${NC}"
else
    echo -e "${RED}✗ Main backend is not running${NC}"
    echo "Starting backend..."
    sudo systemctl start lvl-up-backend
fi
echo ""

echo -e "${BLUE}=== 2. Checking AI Services Status ===${NC}"
services=("lvl-up-guardian" "lvl-up-conquest" "lvl-up-imperium" "lvl-up-sandbox")
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}✓ $service is running${NC}"
    else
        echo -e "${RED}✗ $service is not running${NC}"
        echo "Starting $service..."
        sudo systemctl start "$service"
    fi
done
echo ""

echo -e "${BLUE}=== 3. Checking Token Usage and Rate Limits ===${NC}"
echo "Recent token usage logs:"
journalctl -u lvl-up-backend | grep -i "token\|rate.*limit\|usage" | tail -10 || echo "No token usage logs found"
echo ""

echo -e "${BLUE}=== 4. Testing AI Endpoints Manually ===${NC}"
echo "Testing AI endpoints to check if they're working:"
endpoints=(
    "/api/enhanced-ai/run-ai/conquest"
    "/api/enhanced-ai/run-ai/guardian"
    "/api/enhanced-ai/run-ai/imperium"
    "/api/enhanced-ai/run-ai/sandbox"
)

for endpoint in "${endpoints[@]}"; do
    echo "Testing $endpoint:"
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000$endpoint" 2>/dev/null || echo "Failed")
    echo "Response: $response"
done
echo ""

echo -e "${BLUE}=== 5. Checking Database for Recent AI Activity ===${NC}"
if command -v sqlite3 &> /dev/null; then
    if [ -f "/home/ubuntu/ai-backend-python/app.db" ]; then
        echo "Recent proposals:"
        sqlite3 /home/ubuntu/ai-backend-python/app.db "SELECT ai_type, created_at, status, title FROM proposals ORDER BY created_at DESC LIMIT 5;" 2>/dev/null || echo "Could not query proposals"
        echo ""
        echo "Recent learning events:"
        sqlite3 /home/ubuntu/ai-backend-python/app.db "SELECT ai_type, created_at, event_type FROM learning ORDER BY created_at DESC LIMIT 5;" 2>/dev/null || echo "Could not query learning"
    else
        echo "Database file not found"
    fi
else
    echo "sqlite3 not available"
fi
echo ""

echo -e "${BLUE}=== 6. Checking for Background Tasks ===${NC}"
echo "Python processes related to AI:"
ps aux | grep -i "python.*ai\|python.*conquest\|python.*guardian\|python.*imperium\|python.*sandbox" | grep -v grep || echo "No AI Python processes found"
echo ""

echo -e "${BLUE}=== 7. Checking Recent Backend Logs ===${NC}"
echo "Recent backend logs (last 20 lines):"
journalctl -u lvl-up-backend -n 20 --no-pager
echo ""

echo -e "${BLUE}=== 8. Checking for AI Testing Triggers ===${NC}"
echo "Looking for testing triggers in code:"
find /home/ubuntu/ai-backend-python -name "*.py" -exec grep -l -i "trigger\|initiate\|start.*test\|run.*test" {} \; | head -5
echo ""

echo -e "${BLUE}=== 9. Checking AI Scheduling Configuration ===${NC}"
echo "AI scheduling settings in config:"
if [ -f "/home/ubuntu/ai-backend-python/app/core/config.py" ]; then
    grep -i "schedule\|timer\|interval\|frequency" /home/ubuntu/ai-backend-python/app/core/config.py || echo "No scheduling settings found in config"
else
    echo "Config file not found"
fi
echo ""

echo -e "${BLUE}=== 10. Checking for Manual AI Testing Endpoints ===${NC}"
echo "Testing manual AI testing endpoints:"
manual_endpoints=(
    "/api/custody/test/conquest"
    "/api/custody/test/guardian"
    "/api/custody/test/imperium"
    "/api/custody/test/sandbox"
    "/api/agents/cycle-status"
    "/api/proposals/cycle/status"
)

for endpoint in "${manual_endpoints[@]}"; do
    echo "Testing $endpoint:"
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000$endpoint" 2>/dev/null || echo "Failed")
    echo "Response: $response"
done
echo ""

echo -e "${BLUE}=== 11. Checking for Autonomous AI Cycles ===${NC}"
echo "Looking for autonomous cycle code:"
find /home/ubuntu/ai-backend-python -name "*.py" -exec grep -l -i "autonomous\|cycle\|loop\|continuous" {} \; | head -5
echo ""

echo -e "${BLUE}=== 12. Checking for Background Service Status ===${NC}"
echo "Background service status:"
curl -s "http://localhost:8000/api/agents/cycle-status" 2>/dev/null || echo "Failed to get cycle status"
echo ""

echo -e "${BLUE}=== 13. Checking for Proposal Generation Status ===${NC}"
echo "Proposal generation status:"
curl -s "http://localhost:8000/api/proposals/cycle/status" 2>/dev/null || echo "Failed to get proposal cycle status"
echo ""

echo -e "${BLUE}=== 14. Checking for AI Learning Status ===${NC}"
echo "AI learning status:"
curl -s "http://localhost:8000/api/learning/status" 2>/dev/null || echo "Failed to get learning status"
echo ""

echo -e "${BLUE}=== 15. Checking for Recent AI Activity in Logs ===${NC}"
echo "Recent AI activity (last 30 lines):"
journalctl -u lvl-up-backend | grep -i "ai\|conquest\|guardian\|imperium\|sandbox" | tail -30 || echo "No AI activity found"
echo ""

echo "=== Analysis Complete ==="
echo ""
echo -e "${YELLOW}=== Recommendations ===${NC}"
echo "1. The backend has autonomous AI cycles that run every 45 minutes"
echo "2. AI testing is handled through the Custodes Protocol and proposal generation"
echo "3. Token rate limits are causing failures - check API keys and limits"
echo "4. Database model errors need to be fixed"
echo "5. ML model training errors need to be resolved"
echo ""
echo "To manually trigger AI testing, use:"
echo "curl -X POST http://localhost:8000/api/enhanced-ai/run-ai/conquest"
echo "curl -X POST http://localhost:8000/api/enhanced-ai/run-ai/guardian"
echo "curl -X POST http://localhost:8000/api/enhanced-ai/run-ai/imperium"
echo "curl -X POST http://localhost:8000/api/enhanced-ai/run-ai/sandbox" 