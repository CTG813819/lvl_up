# Simple PowerShell script to deploy Conquest agent fixes
Write-Host "Fixing Conquest agent issues..." -ForegroundColor Green

# Set variables
$EC2_HOST = "34.202.215.209"
$EC2_USER = "ubuntu"
$BACKEND_DIR = "/home/ubuntu/ai-backend-python"
$SSH_KEY_PATH = "C:\projects\lvl_up\New.pem"

Write-Host "Deploying updated backend code..." -ForegroundColor Yellow
# Deploy the updated files
scp -i $SSH_KEY_PATH ai-backend-python/app/services/ai_agent_service.py ${EC2_USER}@${EC2_HOST}:${BACKEND_DIR}/app/services/
scp -i $SSH_KEY_PATH ai-backend-python/app/services/conquest_ai_service.py ${EC2_USER}@${EC2_HOST}:${BACKEND_DIR}/app/services/

Write-Host "Installing git on EC2..." -ForegroundColor Yellow
# Install git
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "sudo apt update && sudo apt install -y git && git config --global user.name 'AI Backend' && git config --global user.email 'ai-backend@example.com'"

Write-Host "Restarting backend services..." -ForegroundColor Yellow
# Restart backend
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && sudo systemctl restart ai-backend-python"

Write-Host "Checking backend logs..." -ForegroundColor Yellow
# Check logs
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && tail -n 10 logs/app.log | grep -E '(Error updating deployment status|Error pushing changes|AsyncGeneratorContextManager)' || echo 'No errors found'"

Write-Host "Fix completed!" -ForegroundColor Green 