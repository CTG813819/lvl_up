#!/bin/bash

echo "🔧 Deploying Single PID Fix"
echo "=========================="

# Copy the updated comprehensive fix script
echo "📝 Copying updated comprehensive fix script..."
scp -i "C:\projects\lvl_up\New.pem" comprehensive_fix.sh ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

# Copy the Python wrapper script
echo "📝 Copying Python wrapper script..."
scp -i "C:\projects\lvl_up\New.pem" run_uvicorn_single.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

# Run the comprehensive fix
echo "🚀 Running comprehensive fix on server..."
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com "cd /home/ubuntu/ai-backend-python && chmod +x comprehensive_fix.sh && sudo ./comprehensive_fix.sh"

echo "✅ Single PID fix deployed!" 