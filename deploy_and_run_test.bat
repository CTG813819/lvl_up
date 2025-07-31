@echo off
echo 🚀 Deploying and running EC2 backend test...

echo 📁 Copying test script to EC2...
scp -i "C:\projects\lvl_up\New.pem" ec2_backend_test.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend/

echo 🔧 Installing dependencies on EC2...
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com "cd /home/ubuntu/ai-backend && pip3 install aiohttp websockets"

echo 🧪 Running comprehensive backend test...
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com "cd /home/ubuntu/ai-backend && python3 ec2_backend_test.py"

echo 📥 Downloading test results...
scp -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend/ec2_backend_test_results_*.json ./

echo ✅ Test deployment and execution completed!
pause 