#!/bin/bash

echo "=== AI Scheduling and Testing Analysis ==="
echo "Timestamp: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== 1. Check for AI Testing Mechanisms ===${NC}"
echo "Looking for test-related code in backend:"
find /home/ubuntu/ai-backend-python -name "*.py" -exec grep -l -i "test\|validate\|verify\|check" {} \; | head -10
echo ""

echo -e "${BLUE}=== 2. Check AI Service Schedules ===${NC}"
echo "Examining AI service files for scheduling:"
for service in guardian conquest imperium sandbox; do
    echo "--- $service service ---"
    if [ -f "/etc/systemd/system/lvl-up-$service.service" ]; then
        echo "Service file exists"
        grep -i "execstart\|workingdirectory\|environment" /etc/systemd/system/lvl-up-$service.service
    else
        echo "Service file not found"
    fi
    echo ""
done

echo -e "${BLUE}=== 3. Check for Background Tasks in Main App ===${NC}"
echo "Looking for background task definitions:"
if [ -f "/home/ubuntu/ai-backend-python/app/main.py" ]; then
    echo "Background tasks in main.py:"
    grep -n -i "background\|task\|schedule\|interval" /home/ubuntu/ai-backend-python/app/main.py || echo "No background tasks found"
else
    echo "main.py not found"
fi
echo ""

echo -e "${BLUE}=== 4. Check AI Agent Service for Scheduling ===${NC}"
if [ -f "/home/ubuntu/ai-backend-python/app/services/ai_agent_service.py" ]; then
    echo "AI Agent Service scheduling:"
    grep -n -i "schedule\|timer\|interval\|background\|run\|execute" /home/ubuntu/ai-backend-python/app/services/ai_agent_service.py || echo "No scheduling found"
else
    echo "ai_agent_service.py not found"
fi
echo ""

echo -e "${BLUE}=== 5. Check for Autonomous AI Cycles ===${NC}"
echo "Looking for autonomous cycle code:"
find /home/ubuntu/ai-backend-python -name "*.py" -exec grep -l -i "autonomous\|cycle\|loop\|continuous" {} \; | head -5
echo ""

echo -e "${BLUE}=== 6. Check Recent AI Activity in Logs ===${NC}"
echo "Recent AI activity (last 50 lines):"
journalctl -u lvl-up-backend | grep -i "ai\|conquest\|guardian\|imperium\|sandbox" | tail -50 || echo "No AI activity found"
echo ""

echo -e "${BLUE}=== 7. Check for Manual AI Testing Endpoints ===${NC}"
echo "Testing manual AI endpoints:"
endpoints=(
    "/api/enhanced-ai/run-ai/conquest"
    "/api/enhanced-ai/run-ai/guardian"
    "/api/enhanced-ai/run-ai/imperium"
    "/api/enhanced-ai/run-ai/sandbox"
    "/api/custody/test/conquest"
    "/api/custody/test/guardian"
    "/api/custody/test/imperium"
    "/api/custody/test/sandbox"
)

for endpoint in "${endpoints[@]}"; do
    echo "Testing $endpoint:"
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000$endpoint" 2>/dev/null || echo "Failed")
    echo "Response: $response"
done
echo ""

echo -e "${BLUE}=== 8. Check for AI Testing Triggers ===${NC}"
echo "Looking for testing triggers in code:"
find /home/ubuntu/ai-backend-python -name "*.py" -exec grep -l -i "trigger\|initiate\|start.*test\|run.*test" {} \; | head -5
echo ""

echo -e "${BLUE}=== 9. Check Database for AI Testing Records ===${NC}"
echo "Recent AI testing activity:"
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

echo -e "${BLUE}=== 10. Check for AI Testing Configuration ===${NC}"
echo "AI testing settings in config:"
if [ -f "/home/ubuntu/ai-backend-python/app/core/config.py" ]; then
    grep -i "test\|validate\|verify\|check\|schedule" /home/ubuntu/ai-backend-python/app/core/config.py || echo "No testing config found"
else
    echo "Config file not found"
fi
echo ""

echo -e "${BLUE}=== 11. Check for AI Service Dependencies ===${NC}"
echo "Checking if AI services depend on each other:"
for service in guardian conquest imperium sandbox; do
    echo "--- $service dependencies ---"
    if [ -f "/etc/systemd/system/lvl-up-$service.service" ]; then
        grep -i "after\|requires\|wants" /etc/systemd/system/lvl-up-$service.service || echo "No dependencies found"
    fi
done
echo ""

echo -e "${BLUE}=== 12. Check for AI Testing Logs ===${NC}"
echo "Recent testing-related logs:"
journalctl -u lvl-up-backend | grep -i "test\|validate\|verify\|check" | tail -20 || echo "No testing logs found"
echo ""

echo "=== Analysis Complete ===" 