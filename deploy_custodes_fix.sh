#!/bin/bash

# Deploy Custodes and Timeout Fix
# This script runs the fixed version of the custodes and timeout fix

set -e

echo "🚀 Deploying Custodes and Timeout Fix..."
echo "============================================================"

# Check if we're in the right directory
if [ ! -f "fix_custodes_and_timeouts_fixed.py" ]; then
    echo "❌ Error: fix_custodes_and_timeouts_fixed.py not found in current directory"
    echo "Please run this script from the ai-backend-python directory"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed"
    exit 1
fi

# Check if backend is running
echo "🔍 Checking backend status..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend is running"
else
    echo "⚠️ Warning: Backend does not appear to be running on port 8000"
    echo "The fix script will attempt to start it if needed"
fi

# Run the fixed script
echo "🔧 Running Custodes and Timeout Fix..."
python3 fix_custodes_and_timeouts_fixed.py

# Check if the script completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Custodes and Timeout Fix completed successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Check the test results above"
    echo "2. If a service was created, you can enable it with:"
    echo "   systemctl --user enable custodes-scheduler.service"
    echo "   systemctl --user start custodes-scheduler.service"
    echo "3. Monitor the scheduler with:"
    echo "   journalctl --user -u custodes-scheduler.service -f"
    echo "4. Or run the scheduler manually with:"
    echo "   python3 custodes_scheduler.py"
else
    echo ""
    echo "❌ Custodes and Timeout Fix failed!"
    echo "Please check the error messages above and try again."
    exit 1
fi 