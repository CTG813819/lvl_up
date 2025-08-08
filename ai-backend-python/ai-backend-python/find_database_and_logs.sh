#!/bin/bash

echo "=== Finding Database and Checking Backend Logs ==="
echo "Timestamp: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== 1. Finding Database Files ===${NC}"
echo "Searching for database files:"
find /home/ubuntu/ai-backend-python -name "*.db" -type f 2>/dev/null
echo ""

echo "Searching for SQLite files:"
find /home/ubuntu/ai-backend-python -name "*.sqlite" -type f 2>/dev/null
echo ""

echo "Searching for database files in common locations:"
ls -la /home/ubuntu/ai-backend-python/app.db 2>/dev/null || echo "app.db not found"
ls -la /home/ubuntu/ai-backend-python/database.db 2>/dev/null || echo "database.db not found"
ls -la /home/ubuntu/ai-backend-python/lvl_up.db 2>/dev/null || echo "lvl_up.db not found"
echo ""

echo -e "${BLUE}=== 2. Checking Backend Configuration ===${NC}"
echo "Database configuration in config.py:"
if [ -f "/home/ubuntu/ai-backend-python/app/core/config.py" ]; then
    grep -i "database\|sqlite\|db" /home/ubuntu/ai-backend-python/app/core/config.py || echo "No database config found"
else
    echo "Config file not found"
fi
echo ""

echo -e "${BLUE}=== 3. Checking Backend Logs ===${NC}"
echo "Recent backend logs from uvicorn processes:"
echo "Checking for log files:"
find /home/ubuntu/ai-backend-python -name "*.log" -type f 2>/dev/null | head -10
echo ""

echo "Checking uvicorn process logs:"
# Get the PID of the uvicorn process
UVICORN_PID=$(ps aux | grep uvicorn | grep -v grep | head -1 | awk '{print $2}')
if [ ! -z "$UVICORN_PID" ]; then
    echo "Uvicorn PID: $UVICORN_PID"
    echo "Process info:"
    ps -p $UVICORN_PID -o pid,ppid,cmd
    echo ""
    echo "Checking if process is writing to any files:"
    lsof -p $UVICORN_PID 2>/dev/null | grep -E "\.(log|db|txt)" || echo "No log files found"
else
    echo "No uvicorn process found"
fi
echo ""

echo -e "${BLUE}=== 4. Checking Backend Status Endpoints ===${NC}"
echo "Testing backend health:"
curl -s "http://localhost:8000/api/health" 2>/dev/null | head -10 || echo "Health endpoint failed"
echo ""

echo "Testing backend status:"
curl -s "http://localhost:8000/api/status" 2>/dev/null | head -10 || echo "Status endpoint failed"
echo ""

echo -e "${BLUE}=== 5. Checking AI Status Endpoints ===${NC}"
echo "Testing AI cycle status:"
curl -s "http://localhost:8000/api/agents/cycle-status" 2>/dev/null | head -10 || echo "Cycle status failed"
echo ""

echo "Testing proposal cycle status:"
curl -s "http://localhost:8000/api/proposals/cycle/status" 2>/dev/null | head -10 || echo "Proposal status failed"
echo ""

echo -e "${BLUE}=== 6. Checking for Recent AI Activity ===${NC}"
echo "Recent AI activity in process memory:"
ps aux | grep -E "(python|uvicorn)" | grep -v grep | head -5
echo ""

echo "Checking for AI activity in recent files:"
find /home/ubuntu/ai-backend-python -name "*.py" -mtime -1 2>/dev/null | head -5
echo ""

echo -e "${BLUE}=== 7. Testing AI Endpoints Again ===${NC}"
echo "Testing Conquest AI endpoint:"
curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/conquest" | jq '.' 2>/dev/null || curl -X POST -H "Content-Type: application/json" -d '{}' -s "http://localhost:8000/api/enhanced-ai/run-ai/conquest"
echo ""

echo -e "${BLUE}=== 8. Checking for Database Creation ===${NC}"
echo "Checking if database needs to be created:"
if [ -f "/home/ubuntu/ai-backend-python/app/main.py" ]; then
    echo "Main.py exists - checking for database initialization:"
    grep -i "init_database\|create_tables\|database" /home/ubuntu/ai-backend-python/app/main.py || echo "No database initialization found"
else
    echo "Main.py not found"
fi
echo ""

echo "=== Analysis Complete ==="
echo ""
echo -e "${YELLOW}=== Recommendations ===${NC}"
echo "1. The database file might not exist yet - check if it needs to be created"
echo "2. The backend is running but might not have initialized the database"
echo "3. Check the backend logs for database initialization errors"
echo "4. The AI endpoints are working, so the backend is functional"
echo ""
echo "To manually create the database, try:"
echo "cd /home/ubuntu/ai-backend-python"
echo "source venv/bin/activate"
echo "python -c \"from app.core.database import init_database, create_tables; import asyncio; asyncio.run(init_database()); asyncio.run(create_tables())\"" 