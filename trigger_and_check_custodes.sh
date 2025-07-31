#!/bin/bash

# Path to your PEM file
PEM_PATH="C:/projects/lvl_up/New.pem"
# EC2 user and host
EC2_USER="ubuntu"
EC2_HOST="ec2-34-202-215-209.compute-1.amazonaws.com"
# Backend directory on EC2
BACKEND_DIR="/home/ubuntu/ai-backend-python"
# Backend URL (assumes backend is running on localhost:8000 on EC2)
BACKEND_URL="http://localhost:8000"

# SSH and run commands
ssh -i "$PEM_PATH" $EC2_USER@$EC2_HOST << EOF
cd $BACKEND_DIR
echo "Forcing custody tests for all AIs..."
for ai in imperium guardian sandbox conquest; do
  echo "Triggering test for \$ai"
  curl -X POST "$BACKEND_URL/api/custody/test/\$ai/force"
  sleep 2
done
echo "Fetching /api/custody data..."
curl "$BACKEND_URL/api/custody" | python3 -m json.tool
EOF 