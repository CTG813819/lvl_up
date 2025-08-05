#!/bin/bash
# Deploy Final AI Backend with New Schedule
echo "Deploying Final AI Backend with New Schedule..."

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
pkill -f "main_final.py" 2>/dev/null || true
pkill -f "imperium_runner.py" 2>/dev/null || true
pkill -f "sandbox_runner.py" 2>/dev/null || true
pkill -f "custodes_runner.py" 2>/dev/null || true
pkill -f "guardian_runner.py" 2>/dev/null || true

# Wait for cleanup
sleep 3

# Make startup script executable
chmod +x start_final_backend.sh

# Start the final backend
echo "Starting final backend..."
nohup ./start_final_backend.sh > backend_final.log 2>&1 &

# Wait for startup
sleep 10

# Check if backend is running
if pgrep -f "main_final.py" > /dev/null; then
    echo "Final backend started successfully!"
    echo "Backend process: $(pgrep -f 'main_final.py')"
    echo "Final AI Agent Schedule:"
    echo "  * Imperium: Every 1 hour (starts immediately)"
    echo "  * Custodes: Tests after Imperium completes"
    echo "  * Guardian: 30-40 minutes after Custodes"
    echo "  * Custodes: Tests after Guardian"
    echo "  * Sandbox: Every 2 hours"
    echo "  * Custodes: Tests after Sandbox"
    echo ""
    echo "Check status: curl http://localhost:8000/ai-agents/status"
    echo "Check health: curl http://localhost:8000/health"
else
    echo "Failed to start final backend"
    echo "Check logs: tail -f backend_final.log"
fi
