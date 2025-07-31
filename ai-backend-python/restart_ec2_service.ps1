# Restart Enhanced Adversarial Testing Service on EC2
Write-Host "Restarting Enhanced Adversarial Testing Service on EC2..." -ForegroundColor Green

# SSH into the EC2 instance and restart the service
$sshCommand = @"
cd /home/ubuntu/ai-backend-python

# Test the enhanced adversarial service
echo "Testing enhanced adversarial service..."
python3 test_enhanced_adversarial_service.py

# Restart the main backend service
echo "Restarting main backend service..."
sudo systemctl restart ai-backend-python

# Check if the service is running
echo "Checking service status..."
sudo systemctl status ai-backend-python --no-pager

# Test the enhanced adversarial service endpoint
echo "Testing enhanced adversarial service endpoint..."
curl -s http://localhost:8001/ | head -20

echo "Enhanced adversarial testing service should now be available on port 8001"
"@

# Execute the SSH command
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com $sshCommand

Write-Host "Enhanced adversarial testing service restart completed!" -ForegroundColor Green 