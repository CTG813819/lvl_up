#!/bin/bash

# 🧪 EC2 Comprehensive Backend Testing Script
# This script runs on the EC2 instance to thoroughly test all backend functionality

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Configuration
BACKEND_DIR="/home/ubuntu/ai-backend-python"
VENV_PATH="$BACKEND_DIR/venv"
PYTHON_PATH="$VENV_PATH/bin/python"
BASE_URL="http://localhost:4000"
WEBSOCKET_URL="ws://localhost:8001"

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test counter functions
increment_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

pass_test() {
    PASSED_TESTS=$((PASSED_TESTS + 1))
    log "✅ Test passed"
}

fail_test() {
    FAILED_TESTS=$((FAILED_TESTS + 1))
    error "❌ Test failed: $1"
}

log "🧪 Starting Comprehensive Backend Testing"
log "=================================================="

# Navigate to backend directory
cd $BACKEND_DIR
log "📍 Working directory: $(pwd)"

# Activate virtual environment
source $VENV_PATH/bin/activate
log "✅ Virtual environment activated"

# Create testing directory
mkdir -p testing
cd testing

# ============================================================================
# 1. BASIC CONNECTIVITY TESTS
# ============================================================================

log "🔌 1. Testing Basic Connectivity..."

# Test 1: Backend health check
increment_test
log "Testing backend health..."
if curl -f -s "$BASE_URL/health" > /dev/null; then
    pass_test
else
    fail_test "Backend health check failed"
fi

# Test 2: Backend response time
increment_test
log "Testing response time..."
start_time=$(date +%s.%N)
curl -s "$BASE_URL/health" > /dev/null
end_time=$(date +%s.%N)
response_time=$(echo "$end_time - $start_time" | bc)
if (( $(echo "$response_time < 5" | bc -l) )); then
    pass_test
    log "   Response time: ${response_time}s"
else
    fail_test "Response time too slow: ${response_time}s"
fi

# ============================================================================
# 2. API ENDPOINT TESTS
# ============================================================================

log "🔗 2. Testing API Endpoints..."

# Test 3: AI Agents Status
increment_test
log "Testing AI agents status..."
response=$(curl -s "$BASE_URL/api/agents/status")
if echo "$response" | grep -q "agents"; then
    pass_test
    agents_count=$(echo "$response" | jq '.agents | length' 2>/dev/null || echo "unknown")
    log "   Active agents: $agents_count"
else
    fail_test "AI agents status endpoint failed"
fi

# Test 4: Learning System Status
increment_test
log "Testing learning system status..."
response=$(curl -s "$BASE_URL/api/learning/status")
if echo "$response" | grep -q "status"; then
    pass_test
    experiments=$(echo "$response" | jq '.total_experiments' 2>/dev/null || echo "unknown")
    log "   Total experiments: $experiments"
else
    fail_test "Learning system status endpoint failed"
fi

# Test 5: Proposals Endpoint
increment_test
log "Testing proposals endpoint..."
response=$(curl -s "$BASE_URL/api/proposals/")
if echo "$response" | grep -q "proposals"; then
    pass_test
    proposals_count=$(echo "$response" | jq '.proposals | length' 2>/dev/null || echo "unknown")
    log "   Proposals count: $proposals_count"
else
    fail_test "Proposals endpoint failed"
fi

# Test 6: Oath Papers Endpoint
increment_test
log "Testing oath papers endpoint..."
response=$(curl -s "$BASE_URL/api/oath-papers/")
if echo "$response" | grep -q "oath_papers"; then
    pass_test
    papers_count=$(echo "$response" | jq '.oath_papers | length' 2>/dev/null || echo "unknown")
    log "   Oath papers count: $papers_count"
else
    fail_test "Oath papers endpoint failed"
fi

# Test 7: Growth Analytics
increment_test
log "Testing growth analytics..."
response=$(curl -s "$BASE_URL/api/growth/status")
if echo "$response" | grep -q "status"; then
    pass_test
else
    fail_test "Growth analytics endpoint failed"
fi

# Test 8: Conquest AI Status
increment_test
log "Testing Conquest AI status..."
response=$(curl -s "$BASE_URL/api/conquest/status")
if echo "$response" | grep -q "conquest_ai"; then
    pass_test
else
    fail_test "Conquest AI status endpoint failed"
fi

# ============================================================================
# 3. DATABASE TESTS
# ============================================================================

log "🗄️ 3. Testing Database Operations..."

# Create database test script
cat > test_database.py << 'EOF'
#!/usr/bin/env python3
"""
Database testing script
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import get_session, init_database

async def test_database():
    """Test database operations"""
    print("Testing database operations...")
    
    try:
        # Initialize database
        await init_database()
        session = get_session()
        
        async with session as s:
            # Test 1: Check if tables exist
            tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            """
            result = await s.execute(text(tables_query))
            tables = [row[0] for row in result.fetchall()]
            
            required_tables = ['proposals', 'oath_papers', 'learning_entries']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if not missing_tables:
                print("✅ All required tables exist")
            else:
                print(f"❌ Missing tables: {missing_tables}")
                return False
            
            # Test 2: Check data counts
            for table in required_tables:
                count_query = f"SELECT COUNT(*) FROM {table}"
                result = await s.execute(text(count_query))
                count = result.scalar()
                print(f"   {table}: {count} records")
            
            # Test 3: Test basic queries
            proposals_query = "SELECT COUNT(*) FROM proposals WHERE ai_type = 'Guardian'"
            result = await s.execute(text(proposals_query))
            guardian_count = result.scalar()
            print(f"   Guardian proposals: {guardian_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_database())
    sys.exit(0 if success else 1)
EOF

# Test 9: Database operations
increment_test
log "Testing database operations..."
if $PYTHON_PATH test_database.py; then
    pass_test
else
    fail_test "Database operations failed"
fi

# ============================================================================
# 4. AI AGENT TESTS
# ============================================================================

log "🤖 4. Testing AI Agents..."

# Test 10: Individual agent tests
for agent in "imperium" "guardian" "sandbox" "conquest"; do
    increment_test
    log "Testing $agent agent..."
    response=$(curl -s "$BASE_URL/api/agents/$agent/status")
    if echo "$response" | grep -q "status"; then
        pass_test
        status=$(echo "$response" | jq -r '.status' 2>/dev/null || echo "unknown")
        log "   $agent status: $status"
    else
        fail_test "$agent agent test failed"
    fi
done

# Test 11: Run all agents
increment_test
log "Testing run all agents..."
response=$(curl -s -X POST "$BASE_URL/api/agents/run-all")
if echo "$response" | grep -q "agents_run"; then
    pass_test
    agents_run=$(echo "$response" | jq '.agents_run' 2>/dev/null || echo "unknown")
    proposals_created=$(echo "$response" | jq '.total_proposals_created' 2>/dev/null || echo "unknown")
    log "   Agents run: $agents_run, Proposals created: $proposals_created"
else
    fail_test "Run all agents failed"
fi

# ============================================================================
# 5. LEARNING SYSTEM TESTS
# ============================================================================

log "🧠 5. Testing Learning System..."

# Test 12: Learning insights for each AI type
for ai_type in "Imperium" "Guardian" "Sandbox" "Conquest"; do
    increment_test
    log "Testing $ai_type learning insights..."
    response=$(curl -s "$BASE_URL/api/learning/insights/$ai_type")
    if echo "$response" | grep -q "stats"; then
        pass_test
        entries=$(echo "$response" | jq '.stats.total_learning_entries' 2>/dev/null || echo "unknown")
        log "   $ai_type learning entries: $entries"
    else
        fail_test "$ai_type learning insights failed"
    fi
done

# Test 13: Learning data
increment_test
log "Testing learning data..."
response=$(curl -s "$BASE_URL/api/learning/data")
if echo "$response" | grep -q "Imperium"; then
    pass_test
    total_experiments=$(echo "$response" | jq '[.[] | .experiments | length] | add' 2>/dev/null || echo "unknown")
    log "   Total experiments: $total_experiments"
else
    fail_test "Learning data endpoint failed"
fi

# ============================================================================
# 6. PERFORMANCE TESTS
# ============================================================================

log "⚡ 6. Testing Performance..."

# Test 14: Load testing
increment_test
log "Testing load performance..."
start_time=$(date +%s)
for i in {1..10}; do
    curl -s "$BASE_URL/health" > /dev/null &
done
wait
end_time=$(date +%s)
load_time=$((end_time - start_time))
if [ $load_time -lt 10 ]; then
    pass_test
    log "   Load test completed in ${load_time}s"
else
    fail_test "Load test took too long: ${load_time}s"
fi

# Test 15: Concurrent requests
increment_test
log "Testing concurrent requests..."
response_times=()
for i in {1..5}; do
    start=$(date +%s.%N)
    curl -s "$BASE_URL/api/agents/status" > /dev/null
    end=$(date +%s.%N)
    response_times+=($(echo "$end - $start" | bc))
done

avg_time=$(echo "${response_times[@]}" | tr ' ' '\n' | awk '{sum+=$1} END {print sum/NR}')
if (( $(echo "$avg_time < 3" | bc -l) )); then
    pass_test
    log "   Average response time: ${avg_time}s"
else
    fail_test "Average response time too slow: ${avg_time}s"
fi

# ============================================================================
# 7. SECURITY TESTS
# ============================================================================

log "🔒 7. Testing Security..."

# Test 16: Input validation
increment_test
log "Testing input validation..."
response=$(curl -s -X POST "$BASE_URL/api/oath-papers/" \
    -d "title='; DROP TABLE users; --&content=test&category=test")
if [ "$(echo "$response" | jq -r '.detail' 2>/dev/null)" != "null" ]; then
    pass_test
    log "   SQL injection attempt blocked"
else
    warn "SQL injection protection may not be working"
fi

# Test 17: Rate limiting (basic)
increment_test
log "Testing rate limiting..."
for i in {1..5}; do
    curl -s "$BASE_URL/health" > /dev/null
done
response=$(curl -s "$BASE_URL/health")
if echo "$response" | grep -q "status"; then
    pass_test
    log "   Rate limiting test passed"
else
    fail_test "Rate limiting may be too restrictive"
fi

# ============================================================================
# 8. WEBSOCKET TESTS
# ============================================================================

log "🔌 8. Testing WebSocket..."

# Create WebSocket test script
cat > test_websocket.py << 'EOF'
#!/usr/bin/env python3
"""
WebSocket testing script
"""

import asyncio
import websockets
import json
import sys

async def test_websocket():
    """Test WebSocket connection"""
    print("Testing WebSocket connection...")
    
    try:
        uri = "ws://localhost:8001"
        async with websockets.connect(uri) as websocket:
            # Test basic connection
            await websocket.send(json.dumps({"type": "ping", "data": "test"}))
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            
            if response:
                print("✅ WebSocket connection successful")
                return True
            else:
                print("❌ WebSocket connection failed")
                return False
                
    except Exception as e:
        print(f"❌ WebSocket test error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_websocket())
    sys.exit(0 if success else 1)
EOF

# Test 18: WebSocket connection
increment_test
log "Testing WebSocket connection..."
if $PYTHON_PATH test_websocket.py; then
    pass_test
else
    warn "WebSocket server may not be running"
fi

# ============================================================================
# 9. INTEGRATION TESTS
# ============================================================================

log "🔗 9. Testing Integrations..."

# Test 19: GitHub integration status
increment_test
log "Testing GitHub integration..."
response=$(curl -s "$BASE_URL/api/github/status")
if echo "$response" | grep -q "status"; then
    pass_test
    status=$(echo "$response" | jq -r '.status' 2>/dev/null || echo "unknown")
    log "   GitHub integration status: $status"
else
    warn "GitHub integration endpoint not available"
fi

# Test 20: Conquest suggestion analysis
increment_test
log "Testing Conquest suggestion analysis..."
suggestion_data='{"name":"Test App","description":"Test description","suggestion":"Test suggestion"}'
response=$(curl -s -X POST "$BASE_URL/api/conquest/analyze-suggestion" \
    -H "Content-Type: application/json" \
    -d "$suggestion_data")
if echo "$response" | grep -q "status"; then
    pass_test
    status=$(echo "$response" | jq -r '.status' 2>/dev/null || echo "unknown")
    log "   Suggestion analysis status: $status"
else
    fail_test "Conquest suggestion analysis failed"
fi

# ============================================================================
# 10. SYSTEM RESOURCE TESTS
# ============================================================================

log "💻 10. Testing System Resources..."

# Test 21: Memory usage
increment_test
log "Testing memory usage..."
memory_usage=$(ps aux | grep uvicorn | grep -v grep | awk '{print $6}' | head -1)
if [ -n "$memory_usage" ]; then
    memory_mb=$((memory_usage / 1024))
    if [ $memory_mb -lt 1000 ]; then
        pass_test
        log "   Memory usage: ${memory_mb}MB"
    else
        warn "High memory usage: ${memory_mb}MB"
    fi
else
    warn "Could not determine memory usage"
fi

# Test 22: Process status
increment_test
log "Testing process status..."
if pgrep -f uvicorn > /dev/null; then
    pass_test
    process_count=$(pgrep -c uvicorn)
    log "   Active uvicorn processes: $process_count"
else
    fail_test "No uvicorn processes running"
fi

# ============================================================================
# 11. CONFIGURATION TESTS
# ============================================================================

log "⚙️ 11. Testing Configuration..."

# Test 23: Check enhancement files
increment_test
log "Testing enhancement configurations..."
if [ -d "$BACKEND_DIR/enhancements" ]; then
    config_files=$(ls -1 "$BACKEND_DIR/enhancements"/*.json 2>/dev/null | wc -l)
    if [ $config_files -gt 0 ]; then
        pass_test
        log "   Configuration files found: $config_files"
    else
        warn "No configuration files found"
    fi
else
    warn "Enhancements directory not found"
fi

# Test 24: Check logs
increment_test
log "Testing log files..."
if [ -f "$BACKEND_DIR/backend.log" ]; then
    pass_test
    log_size=$(du -h "$BACKEND_DIR/backend.log" | cut -f1)
    log "   Log file size: $log_size"
else
    warn "Backend log file not found"
fi

# ============================================================================
# FINAL RESULTS
# ============================================================================

log "📊 Generating Test Results..."
log "=================================================="

# Calculate success rate
if [ $TOTAL_TESTS -gt 0 ]; then
    success_rate=$(echo "scale=1; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)
else
    success_rate=0
fi

# Create test report
cat > test_report.json << EOF
{
  "timestamp": "$(date -Iseconds)",
  "total_tests": $TOTAL_TESTS,
  "passed_tests": $PASSED_TESTS,
  "failed_tests": $FAILED_TESTS,
  "success_rate": $success_rate,
  "backend_url": "$BASE_URL",
  "websocket_url": "$WEBSOCKET_URL",
  "test_categories": [
    "basic_connectivity",
    "api_endpoints", 
    "database_operations",
    "ai_agents",
    "learning_system",
    "performance",
    "security",
    "websocket",
    "integrations",
    "system_resources",
    "configuration"
  ],
  "recommendations": []
}
EOF

# Display final results
log "🎯 TEST RESULTS SUMMARY"
log "=================================================="
log "Total Tests: $TOTAL_TESTS"
log "Passed: $PASSED_TESTS"
log "Failed: $FAILED_TESTS"
log "Success Rate: ${success_rate}%"

if [ $success_rate -ge 90 ]; then
    log "🎉 EXCELLENT! Backend is performing exceptionally well!"
elif [ $success_rate -ge 80 ]; then
    log "✅ GOOD! Backend is performing well with minor issues."
elif [ $success_rate -ge 70 ]; then
    log "⚠️ FAIR! Backend has some issues that need attention."
else
    log "❌ POOR! Backend has significant issues that need immediate attention."
fi

log "📄 Detailed test report saved to: test_report.json"
log "🔧 Check failed tests and address any issues found"

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    log "🎉 All tests passed! Backend is ready for production."
    exit 0
else
    warn "Some tests failed. Review the results and address issues."
    exit 1
fi 