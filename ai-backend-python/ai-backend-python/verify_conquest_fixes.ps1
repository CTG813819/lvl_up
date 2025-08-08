# Verification script to check Conquest agent fixes
Write-Host "Verifying Conquest agent fixes..." -ForegroundColor Green

# Set variables
$EC2_HOST = "34.202.215.209"
$EC2_USER = "ubuntu"
$BACKEND_DIR = "/home/ubuntu/ai-backend-python"
$SSH_KEY_PATH = "C:\projects\lvl_up\New.pem"

Write-Host "Checking git installation..." -ForegroundColor Yellow
# Check if git is installed
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "git --version"

Write-Host "Checking backend service status..." -ForegroundColor Yellow
# Check backend service status
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "sudo systemctl status ai-backend-python --no-pager"

Write-Host "Checking recent backend logs for errors..." -ForegroundColor Yellow
# Check for errors in recent logs
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && tail -n 20 logs/app.log | grep -E '(Error updating deployment status|Error pushing changes|AsyncGeneratorContextManager|Git not available)' || echo 'No errors found in recent logs'"

Write-Host "Testing Conquest agent endpoints..." -ForegroundColor Yellow
# Test Conquest agent endpoints
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "curl -s http://localhost:4000/api/conquest/status || echo 'Conquest endpoint test failed'"

Write-Host "Checking for Conquest agent activity..." -ForegroundColor Yellow
# Check for Conquest agent activity in logs
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && tail -n 50 logs/app.log | grep -i conquest || echo 'No Conquest agent activity found'"

Write-Host "Verification completed!" -ForegroundColor Green 