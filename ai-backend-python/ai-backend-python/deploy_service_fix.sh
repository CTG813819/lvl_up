#!/bin/bash
# Deploy Service Fix Script

echo "🚀 Deploying service conflict fix to EC2..."

# Copy the fix script to EC2
echo "📤 Copying fix script to EC2..."
scp -i ~/.ssh/your-key.pem ai-backend-python/fix_service_conflicts.py ubuntu@your-ec2-ip:~/ai-backend-python/

# Run the fix on EC2
echo "🔧 Running fix on EC2..."
ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip << 'EOF'
cd ~/ai-backend-python
python3 fix_service_conflicts.py
EOF

echo "✅ Service fix deployed!"
echo "📊 You can now monitor the service with: ssh ubuntu@your-ec2-ip 'cd ~/ai-backend-python && ./monitor_service.sh'" 