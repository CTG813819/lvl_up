#!/bin/bash

echo "=== LVL UP EC2 Backend & AI Scheduling Check ==="
echo "Timestamp: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== 1. System Overview ===${NC}"
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime)"
echo "Memory Usage:"
free -h
echo ""
echo "Disk Usage:"
df -h /
echo ""

echo -e "${BLUE}=== 2. Main Backend Service Status ===${NC}"
if systemctl is-active --quiet lvl-up-backend; then
    echo -e "${GREEN}✓ Main backend is running${NC}"
    echo "Status: $(systemctl is-active lvl-up-backend)"
    echo "Enabled: $(systemctl is-enabled lvl-up-backend)"
else
    echo -e "${RED}✗ Main backend is not running${NC}"
    echo "Status: $(systemctl is-active lvl-up-backend)"
fi
echo ""

echo -e "${BLUE}=== 3. AI Services Status ===${NC}"
services=("lvl-up-guardian" "lvl-up-conquest" "lvl-up-imperium" "lvl-up-sandbox")
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}✓ $service is running${NC}"
    else
        echo -e "${RED}✗ $service is not running${NC}"
    fi
done
echo ""

echo -e "${BLUE}=== 4. Main Backend Logs (Last 30 lines) ===${NC}"
journalctl -u lvl-up-backend -n 30 --no-pager
echo ""

echo -e "${BLUE}=== 5. Main Backend Error Logs (Last 20 lines) ===${NC}"
journalctl -u lvl-up-backend -p err -n 20 --no-pager
echo ""

echo -e "${BLUE}=== 6. Conquest Service Logs (Last 30 lines) ===${NC}"
journalctl -u lvl-up-conquest -n 30 --no-pager
echo ""

echo -e "${BLUE}=== 7. Guardian Service Logs (Last 30 lines) ===${NC}"
journalctl -u lvl-up-guardian -n 30 --no-pager
echo ""

echo -e "${BLUE}=== 8. Imperium Service Logs (Last 30 lines) ===${NC}"
journalctl -u lvl-up-imperium -n 30 --no-pager
echo ""

echo -e "${BLUE}=== 9. Sandbox Service Logs (Last 30 lines) ===${NC}"
journalctl -u lvl-up-sandbox -n 30 --no-pager
echo ""

echo -e "${BLUE}=== 10. Check for AI Scheduling/Timers ===${NC}"
echo "System timers:"
systemctl list-timers --all | grep -i "lvl\|ai\|conquest\|guardian\|imperium\|sandbox" || echo "No AI-related timers found"
echo ""

echo -e "${BLUE}=== 11. Check Crontab for AI Scheduling ===${NC}"
echo "User crontab:"
crontab -l 2>/dev/null | grep -i "ai\|conquest\|guardian\|imperium\|sandbox" || echo "No AI-related cron jobs found"
echo ""

echo -e "${BLUE}=== 12. Check for Background Processes ===${NC}"
echo "Python processes related to AI:"
ps aux | grep -i "python.*ai\|python.*conquest\|python.*guardian\|python.*imperium\|python.*sandbox" | grep -v grep || echo "No AI Python processes found"
echo ""

echo -e "${BLUE}=== 13. Check Backend Configuration ===${NC}"
if [ -f "/home/ubuntu/ai-backend-python/app/core/config.py" ]; then
    echo "Backend config file exists"
    echo "AI scheduling settings:"
    grep -i "schedule\|timer\|interval\|frequency" /home/ubuntu/ai-backend-python/app/core/config.py || echo "No scheduling settings found in config"
else
    echo "Backend config file not found"
fi
echo ""

echo -e "${BLUE}=== 14. Check Database for AI Activity ===${NC}"
echo "Recent AI proposals in database:"
if command -v sqlite3 &> /dev/null; then
    if [ -f "/home/ubuntu/ai-backend-python/app.db" ]; then
        sqlite3 /home/ubuntu/ai-backend-python/app.db "SELECT ai_type, created_at, status FROM proposals ORDER BY created_at DESC LIMIT 10;" 2>/dev/null || echo "Could not query database"
    else
        echo "Database file not found"
    fi
else
    echo "sqlite3 not available"
fi
echo ""

echo -e "${BLUE}=== 15. Check Token Usage and Rate Limits ===${NC}"
echo "Recent token usage logs:"
journalctl -u lvl-up-backend | grep -i "token\|rate.*limit\|usage" | tail -10 || echo "No token usage logs found"
echo ""

echo -e "${BLUE}=== 16. Check for AI Testing Endpoints ===${NC}"
echo "Testing if AI endpoints are responding:"
echo "Testing /api/enhanced-ai/run-ai/conquest:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/enhanced-ai/run-ai/conquest || echo "Failed to connect"
echo ""
echo "Testing /api/custody/test/conquest:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/custody/test/conquest || echo "Failed to connect"
echo ""

echo -e "${BLUE}=== 17. Check for Scheduled Tasks in Code ===${NC}"
echo "Looking for scheduling code in backend:"
find /home/ubuntu/ai-backend-python -name "*.py" -exec grep -l -i "schedule\|timer\|interval\|background\|task" {} \; | head -5
echo ""

echo "=== Check Complete ===" 