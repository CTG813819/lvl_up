#!/bin/bash
# Deploy Updated AI Backend with New Frequencies
echo "Deploying Updated AI Backend with New Frequencies..."

# Stop existing services
echo "Stopping existing services..."
sudo systemctl stop ai-backend.service 2>/dev/null || true
sudo systemctl stop imperium-ai.service 2>/dev/null || true
sudo systemctl stop sandbox-ai.service 2>/dev/null || true
sudo systemctl stop custodes-ai.service 2>/dev/null || true
sudo systemctl stop guardian-ai.service 2>/dev/null || true

# Wait for services to stop
sleep 5

# Kill any remaining processes
echo "Cleaning up processes..."
pkill -f "main.py" 2>/dev/null || true
pkill -f "main_updated.py" 2>/dev/null || true
pkill -f "imperium_runner.py" 2>/dev/null || true
pkill -f "sandbox_runner.py" 2>/dev/null || true
pkill -f "custodes_runner.py" 2>/dev/null || true
pkill -f "guardian_runner.py" 2>/dev/null || true

# Wait for cleanup
sleep 3

# Make startup script executable
chmod +x start_updated_backend.sh

# Start the updated backend
echo "Starting updated backend..."
nohup ./start_updated_backend.sh > backend_updated.log 2>&1 &

# Wait for startup
sleep 10

# Check if backend is running
if pgrep -f "main_updated.py" > /dev/null; then
    echo "Updated backend started successfully!"
    echo "Backend process: $(pgrep -f 'main_updated.py')"
    echo "New AI Agent Schedule:"
    echo "  * Imperium: Every 1.5 hours (starts immediately)"
    echo "  * Sandbox: Every 2 hours (starts 30min after Imperium)"
    echo "  * Guardian: Every 5 hours (starts 1hr after Imperium)"
    echo "  * Custodes: Every 1.5 hours (starts 1.5hr after Imperium, tests others)"
    echo ""
    echo "Check status: curl http://localhost:8000/ai-agents/status"
    echo "Check health: curl http://localhost:8000/health"
else
    echo "Failed to start updated backend"
    echo "Check logs: tail -f backend_updated.log"
fi
