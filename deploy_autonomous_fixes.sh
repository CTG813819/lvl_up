#!/bin/bash

# Deploy autonomous system fixes to backend
echo "🚀 Deploying autonomous system fixes to backend..."

# Copy fixed files to backend
echo "📁 Copying fixed files..."
scp -i "C:\projects\lvl_up\New.pem" ai-backend-python/app/services/sckipit_service.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/services/
scp -i "C:\projects\lvl_up\New.pem" ai-backend-python/app/services/custody_protocol_service.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/services/
scp -i "C:\projects\lvl_up\New.pem" ai-backend-python/app/services/anthropic_service.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/services/
scp -i "C:\projects\lvl_up\New.pem" ai-backend-python/app/services/token_usage_service.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/services/

echo "✅ Files copied successfully!"
echo ""
echo "🔧 Next steps:"
echo "1. SSH into the server: ssh -i 'C:\projects\lvl_up\New.pem' ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com"
echo "2. Restart the service: sudo systemctl restart ai-backend"
echo "3. Check logs: sudo journalctl -u ai-backend -f"
echo ""
echo "🎯 The system should now:"
echo "- Use autonomous evaluation without LLM dependency"
echo "- Generate varied scores based on response quality"
echo "- Have proper duration tracking"
echo "- Avoid rate limiting issues"
echo "- Function independently when tokens are unavailable" 