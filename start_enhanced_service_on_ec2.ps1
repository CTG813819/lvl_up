# Start Enhanced Adversarial Testing Service on EC2
Write-Host "Starting Enhanced Adversarial Testing Service on EC2..." -ForegroundColor Green

# SSH into the EC2 instance and start the service
$sshCommand = @"
cd /home/ubuntu/ai-backend-python

# Check if the service is already running
echo "Checking if enhanced adversarial testing service is running..."
curl -s http://localhost:8001/health || echo "Service not running"

# Test the enhanced adversarial service
echo "Testing enhanced adversarial service..."
python3 test_enhanced_adversarial_service.py

# Start the enhanced adversarial testing service in background
echo "Starting enhanced adversarial testing service on port 8001..."
nohup python3 standalone_enhanced_adversarial_testing.py > enhanced_service.log 2>&1 &
echo "Service started with PID: $!"

# Wait a moment for the service to start
sleep 5

# Test if the service is now running
echo "Testing if service is now running..."
curl -s http://localhost:8001/health

# Check the service logs
echo "Service logs:"
tail -20 enhanced_service.log

echo "Enhanced adversarial testing service should now be available on port 8001"
"@

# Execute the SSH command
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com $sshCommand

Write-Host "Enhanced adversarial testing service startup completed!" -ForegroundColor Green 