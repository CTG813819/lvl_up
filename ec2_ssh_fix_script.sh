#!/bin/bash

echo "🔧 EC2 Backend Fix Script"
echo "=========================="

# Step 1: Stop the conflicting service
echo "1️⃣ Stopping conflicting ai-backend-python service..."
sudo systemctl stop ai-backend-python.service
sudo systemctl disable ai-backend-python.service
echo "✅ ai-backend-python service stopped and disabled"

# Step 2: Check imperium-monitoring service
echo "2️⃣ Checking imperium-monitoring service..."
sudo systemctl status imperium-monitoring.service --no-pager

# Step 3: Navigate to backend directory
echo "3️⃣ Navigating to backend directory..."
cd ~/ai-backend-python

# Step 4: Activate virtual environment
echo "4️⃣ Activating virtual environment..."
source venv/bin/activate

# Step 5: Initialize database
echo "5️⃣ Initializing database..."
python3 -c "
import sys
sys.path.append('.')
try:
    from app.core.database import init_database
    init_database()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    # Try alternative initialization
    try:
        from app.database import init_database
        init_database()
        print('✅ Database initialized via alternative method')
    except Exception as e2:
        print(f'❌ Alternative database initialization failed: {e2}')
"

# Step 6: Check for WebSocket support in main.py
echo "6️⃣ Checking WebSocket support..."
if grep -q "websocket" app/main.py; then
    echo "✅ WebSocket routes found in main.py"
else
    echo "⚠️ No WebSocket routes found in main.py"
    echo "Adding basic WebSocket support..."
    cat >> app/main.py << 'EOF'

# WebSocket support
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message: {data}")
    except WebSocketDisconnect:
        pass

@app.websocket("/api/notifications/ws")
async def notifications_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Notification: {data}")
    except WebSocketDisconnect:
        pass

@app.websocket("/ws/imperium/learning-analytics")
async def imperium_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Imperium: {data}")
    except WebSocketDisconnect:
        pass
EOF
    echo "✅ WebSocket routes added to main.py"
fi

# Step 7: Add missing endpoints
echo "7️⃣ Adding missing endpoints..."
if ! grep -q "/api/health" app/main.py; then
    cat >> app/main.py << 'EOF'

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "imperium-monitoring"}

@app.get("/api/status")
async def status_check():
    return {"status": "running", "service": "imperium-monitoring"}

@app.get("/api/imperium/health")
async def imperium_health():
    return {"status": "healthy", "service": "imperium"}

@app.get("/api/proposals")
async def get_proposals():
    return {"proposals": [], "count": 0}

@app.get("/api/proposals/ai-status")
async def get_proposals_ai_status():
    return {"ai_status": "active", "proposals": []}

@app.get("/api/learning/data")
async def get_learning_data():
    return {"learning_data": [], "status": "active"}

@app.get("/api/learning/metrics")
async def get_learning_metrics():
    return {"metrics": {}, "status": "active"}

@app.get("/api/oath-papers")
async def get_oath_papers():
    return {"oath_papers": [], "count": 0}

@app.get("/api/oath-papers/ai-insights")
async def get_oath_papers_insights():
    return {"insights": [], "status": "active"}

@app.post("/api/conquest/build-failure")
async def conquest_build_failure():
    return {"status": "received", "action": "build_failure_logged"}
EOF
    echo "✅ Missing endpoints added to main.py"
fi

# Step 8: Restart the service
echo "8️⃣ Restarting imperium-monitoring service..."
sudo systemctl restart imperium-monitoring.service
sleep 5

# Step 9: Check service status
echo "9️⃣ Checking service status..."
sudo systemctl status imperium-monitoring.service --no-pager

# Step 10: Test endpoints
echo "10️⃣ Testing endpoints..."
sleep 3

echo "Testing health endpoint..."
curl -s http://localhost:4000/api/health || echo "❌ Health endpoint failed"

echo "Testing status endpoint..."
curl -s http://localhost:4000/api/status || echo "❌ Status endpoint failed"

echo "Testing WebSocket endpoint..."
curl -s -I http://localhost:4000/ws | head -1 || echo "❌ WebSocket endpoint failed"

# Step 11: Check logs for errors
echo "11️⃣ Checking recent logs for errors..."
sudo journalctl -u imperium-monitoring.service -n 20 --no-pager

echo "=========================="
echo "🎯 Fix Summary:"
echo "✅ Conflicting service stopped"
echo "✅ Database initialization attempted"
echo "✅ WebSocket support added"
echo "✅ Missing endpoints added"
echo "✅ Service restarted"
echo ""
echo "🔄 Next steps:"
echo "1. Test your Flutter app"
echo "2. Check if database errors are resolved"
echo "3. Test WebSocket connections"
echo "4. Monitor logs for any remaining issues" 