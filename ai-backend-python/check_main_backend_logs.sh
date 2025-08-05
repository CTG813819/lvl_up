#!/bin/bash

echo "=== LVL UP Main Backend Logs Check ==="
echo "Timestamp: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== 1. Main Backend Service Status ===${NC}"
if systemctl is-active --quiet lvl-up-backend; then
    echo -e "${GREEN}✓ Main backend is running${NC}"
    echo "Status: $(systemctl is-active lvl-up-backend)"
    echo "Enabled: $(systemctl is-enabled lvl-up-backend)"
else
    echo -e "${RED}✗ Main backend is not running${NC}"
    echo "Status: $(systemctl is-active lvl-up-backend)"
fi
echo ""

echo -e "${BLUE}=== 2. Main Backend Logs (Last 50 lines) ===${NC}"
journalctl -u lvl-up-backend -n 50 --no-pager
echo ""

echo -e "${BLUE}=== 3. Main Backend Error Logs (Last 30 lines) ===${NC}"
journalctl -u lvl-up-backend -p err -n 30 --no-pager
echo ""

echo -e "${BLUE}=== 4. Main Backend Process ===${NC}"
ps aux | grep "lvl-up-backend\|main.py" | grep -v grep
echo ""

echo -e "${BLUE}=== 5. Main Backend Port Check ===${NC}"
echo "Checking if port 8000 is listening:"
netstat -tlnp | grep :8000 || echo "Port 8000 not found"
echo ""

echo -e "${BLUE}=== 6. Main Backend Directory Check ===${NC}"
BACKEND_DIR="/home/ubuntu/lvl_up/ai-backend-python"
if [ -d "$BACKEND_DIR" ]; then
    echo "Backend directory exists: $BACKEND_DIR"
    echo "Main.py exists: $([ -f "$BACKEND_DIR/main.py" ] && echo "Yes" || echo "No")"
    echo "Requirements.txt exists: $([ -f "$BACKEND_DIR/requirements.txt" ] && echo "Yes" || echo "No")"
    echo ""
    
    echo "Recent files in backend directory:"
    ls -la "$BACKEND_DIR" | head -10
    echo ""
else
    echo -e "${RED}Backend directory not found: $BACKEND_DIR${NC}"
fi

echo -e "${BLUE}=== 7. Main Backend Environment ===${NC}"
systemctl show lvl-up-backend --property=Environment 2>/dev/null | grep -v "^$" || echo "No environment variables found"
echo ""

echo -e "${BLUE}=== 8. Main Backend Health Check ===${NC}"
echo "Testing main backend endpoint:"
if curl -s --connect-timeout 5 http://localhost:8000/health >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Main backend is responding on /health${NC}"
else
    echo -e "${RED}✗ Main backend is not responding on /health${NC}"
fi

if curl -s --connect-timeout 5 http://localhost:8000/docs >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Main backend docs are accessible${NC}"
else
    echo -e "${RED}✗ Main backend docs are not accessible${NC}"
fi
echo ""

echo -e "${BLUE}=== 9. Real-time Log Monitoring ===${NC}"
echo "To monitor logs in real-time, run:"
echo "journalctl -u lvl-up-backend -f"
echo ""
echo "To restart the main backend:"
echo "sudo systemctl restart lvl-up-backend"
echo ""
echo "To check service configuration:"
echo "sudo systemctl cat lvl-up-backend" 