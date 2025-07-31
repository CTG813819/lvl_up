Write-Host "🚀 Deploying and running EC2 backend test..." -ForegroundColor Green

Write-Host "📁 Copying test script to EC2..." -ForegroundColor Yellow
scp -i "C:\projects\lvl_up\New.pem" ec2_backend_test.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend/

Write-Host "🔧 Installing dependencies on EC2..." -ForegroundColor Yellow
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com "cd /home/ubuntu/ai-backend && pip3 install aiohttp websockets"

Write-Host "🧪 Running comprehensive backend test..." -ForegroundColor Yellow
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com "cd /home/ubuntu/ai-backend && python3 ec2_backend_test.py"

Write-Host "📥 Downloading test results..." -ForegroundColor Yellow
scp -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend/ec2_backend_test_results_*.json ./

Write-Host "✅ Test deployment and execution completed!" -ForegroundColor Green
Read-Host "Press Enter to continue" 