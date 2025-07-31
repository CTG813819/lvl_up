#!/bin/bash

# Deploy Dynamic Target Generation System to EC2
echo "🚀 Deploying Dynamic Target Generation System to EC2..."

# Stop all running Docker containers
sudo docker stop $(sudo docker ps -q)
# Remove all stopped Docker containers
sudo docker rm $(sudo docker ps -a -q)

# Copy vulnerability templates
echo "📦 Copying vulnerability templates..."
scp -i "C:\projects\lvl_up\New.pem" -r vuln_templates/ ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

# Copy service files
echo "🔧 Copying service files..."
scp -i "C:\projects\lvl_up\New.pem" app/services/dynamic_target_service.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/services/
scp -i "C:\projects\lvl_up\New.pem" app/services/adaptive_target_service.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/services/
scp -i "C:\projects\lvl_up\New.pem" app/services/custody_protocol_service.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/services/

# Copy test file
echo "🧪 Copying test file..."
scp -i "C:\projects\lvl_up\New.pem" test_dynamic_targets.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

# Copy requirements
echo "📋 Copying requirements..."
scp -i "C:\projects\lvl_up\New.pem" requirements.txt ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

echo "✅ Deployment completed!"
echo "🔗 SSH to EC2: ssh -i 'C:\projects\lvl_up\New.pem' ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com"
echo "🧪 Run test: python test_dynamic_targets.py" 