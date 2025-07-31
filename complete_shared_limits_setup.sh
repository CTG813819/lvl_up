#!/bin/bash

# Complete Shared Token Limits Setup
# This script finalizes the shared token limits deployment

set -e

echo "🔧 Completing Shared Token Limits Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_DIR="/home/ubuntu/ai-backend-python"
VENV_PATH="$PROJECT_DIR/venv/bin/activate"

print_status "Completing shared token limits setup..."

# Step 1: Navigate to project directory and activate virtual environment
print_status "Setting up environment..."
cd "$PROJECT_DIR"
source "$VENV_PATH"

# Step 2: Initialize the database
print_status "Initializing database..."
python -c "
import asyncio
from app.core.database import init_database
asyncio.run(init_database())
print('Database initialized successfully')
"

# Step 3: Test the shared limits service with database
print_status "Testing shared limits service with database..."
python test_shared_limits.py

# Step 4: Start the backend service
print_status "Starting backend service..."

# Kill any existing backend processes
pkill -f "uvicorn app.main:app" || true
sleep 2

# Start the backend in the background
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for the service to start
sleep 5

# Check if the service is running
if ps -p $BACKEND_PID > /dev/null; then
    print_success "Backend service started successfully (PID: $BACKEND_PID)"
else
    print_error "Failed to start backend service"
    exit 1
fi

# Step 5: Test the API endpoints
print_status "Testing API endpoints..."

# Test the summary endpoint
echo "Testing /api/shared-limits/summary..."
curl -s http://localhost:8000/api/shared-limits/summary | head -10

# Test the test endpoint
echo "Testing /api/shared-limits/test..."
curl -s http://localhost:8000/api/shared-limits/test | head -10

# Step 6: Create a systemd service for the backend
print_status "Creating systemd service..."

sudo tee /etc/systemd/system/ai-backend.service > /dev/null << EOF
[Unit]
Description=AI Backend Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable ai-backend.service

print_success "Systemd service created and enabled"

# Step 7: Create a monitoring script
print_status "Creating monitoring script..."

cat > monitor_shared_limits.sh << 'EOF'
#!/bin/bash

# Monitor Shared Token Limits
echo "📊 Shared Token Limits Monitor"
echo "=============================="

# Get current usage
echo "Current Usage:"
curl -s http://localhost:8000/api/shared-limits/summary | jq '.current_usage' 2>/dev/null || curl -s http://localhost:8000/api/shared-limits/summary

echo ""
echo "Test Results:"
curl -s http://localhost:8000/api/shared-limits/test | jq '.' 2>/dev/null || curl -s http://localhost:8000/api/shared-limits/test

echo ""
echo "Backend Status:"
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not running"
fi
EOF

chmod +x monitor_shared_limits.sh

# Step 8: Create a simple notification system for the app
print_status "Creating simple notification system..."

cat > simple_notification_service.py << 'EOF'
"""
Simple Notification Service for Shared Token Limits
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import structlog

logger = structlog.get_logger()

class SimpleNotificationService:
    """Simple notification service that logs to file for app integration"""
    
    def __init__(self):
        self.notification_file = "/home/ubuntu/ai-backend-python/notifications.json"
        self._notifications = []
        self._load_notifications()
    
    def _load_notifications(self):
        """Load notifications from file"""
        try:
            import json
            with open(self.notification_file, 'r') as f:
                self._notifications = json.load(f)
        except FileNotFoundError:
            self._notifications = []
    
    def _save_notifications(self):
        """Save notifications to file"""
        try:
            import json
            with open(self.notification_file, 'w') as f:
                json.dump(self._notifications, f, indent=2)
        except Exception as e:
            logger.error("Error saving notifications", error=str(e))
    
    async def add_notification(self, title: str, message: str, notification_type: str = "info", metadata: Dict = None):
        """Add a notification"""
        notification = {
            "id": len(self._notifications) + 1,
            "title": title,
            "message": message,
            "type": notification_type,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self._notifications.append(notification)
        self._save_notifications()
        
        # Keep only last 100 notifications
        if len(self._notifications) > 100:
            self._notifications = self._notifications[-100:]
            self._save_notifications()
        
        logger.info("Notification added", notification=notification)
    
    async def get_notifications(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent notifications"""
        self._load_notifications()
        return self._notifications[-limit:]
    
    async def get_unread_count(self) -> int:
        """Get count of unread notifications (all are considered unread for simplicity)"""
        self._load_notifications()
        return len(self._notifications)

# Global instance
simple_notification_service = SimpleNotificationService()
EOF

# Step 9: Update the shared limits service to use simple notifications
print_status "Updating shared limits service with simple notifications..."

# Update the notification method in shared_token_limits_service.py
sed -i 's/async def _send_notification(self, notification: Dict\[str, Any\]) -> None:/async def _send_notification(self, notification: Dict[str, Any]) -> None:\n        try:\n            from simple_notification_service import simple_notification_service\n            await simple_notification_service.add_notification(\n                title=notification["title"],\n                message=notification["message"],\n                notification_type=notification["type"],\n                metadata=notification\n            )\n        except Exception as e:\n            logger.error("Error sending notification", error=str(e))/' shared_token_limits_service.py

# Step 10: Add notification endpoints to the routes
print_status "Adding notification endpoints..."

cat >> shared_limits_routes.py << 'EOF'

@router.get("/notifications")
async def get_notifications(limit: int = 50):
    """Get notifications"""
    try:
        from simple_notification_service import simple_notification_service
        notifications = await simple_notification_service.get_notifications(limit)
        return {
            "notifications": notifications,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting notifications", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting notifications: {str(e)}")

@router.get("/notifications/unread-count")
async def get_unread_count():
    """Get unread notification count"""
    try:
        from simple_notification_service import simple_notification_service
        count = await simple_notification_service.get_unread_count()
        return {
            "unread_count": count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting unread count", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting unread count: {str(e)}")
EOF

# Step 11: Restart the backend with new features
print_status "Restarting backend with new features..."

pkill -f "uvicorn app.main:app" || true
sleep 2

nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

sleep 5

# Step 12: Final test
print_status "Running final tests..."

echo "Testing shared limits summary..."
curl -s http://localhost:8000/api/shared-limits/summary | head -5

echo "Testing notifications..."
curl -s http://localhost:8000/api/shared-limits/notifications | head -5

echo "Testing unread count..."
curl -s http://localhost:8000/api/shared-limits/notifications/unread-count

print_success "Shared Token Limits System setup completed successfully!"

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo "✅ Shared token limits implemented"
echo "✅ All AIs share 40k Anthropic + 6k OpenAI tokens"
echo "✅ Rate limiting and cooldown periods active"
echo "✅ Real-time monitoring and logging"
echo "✅ Simple notification system for app integration"
echo "✅ API endpoints available at /api/shared-limits/*"
echo "✅ Systemd service created and enabled"
echo ""
echo "📊 Monitor usage: ./monitor_shared_limits.sh"
echo "🌐 API endpoints:"
echo "   - Summary: http://localhost:8000/api/shared-limits/summary"
echo "   - Test: http://localhost:8000/api/shared-limits/test"
echo "   - Notifications: http://localhost:8000/api/shared-limits/notifications"
echo "   - Unread count: http://localhost:8000/api/shared-limits/notifications/unread-count"
echo ""
echo "📚 Documentation: SHARED_LIMITS_DOCUMENTATION.md"
echo "" 