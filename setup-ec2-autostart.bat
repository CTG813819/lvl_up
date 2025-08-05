@echo off
echo 🔧 Setting up EC2 Auto-Start
echo ===========================

set EC2_IP=34.202.215.209
set KEY_FILE=New.pem

echo [INFO] Setting up PM2 auto-start on EC2...

REM Create a temporary script file for the EC2 commands
echo #!/bin/bash > ec2-setup.sh
echo cd /home/ubuntu/ai-learning-backend >> ec2-setup.sh
echo pm2 save >> ec2-setup.sh
echo sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u ubuntu --hp /home/ubuntu >> ec2-setup.sh
echo echo "Auto-start setup completed" >> ec2-setup.sh

echo [INFO] Uploading setup script to EC2...
scp -i "%KEY_FILE%" ec2-setup.sh ubuntu@%EC2_IP%:~/

echo [INFO] Running setup script on EC2...
ssh -i "%KEY_FILE%" ubuntu@%EC2_IP% "chmod +x ~/ec2-setup.sh && ~/ec2-setup.sh"

echo [INFO] Cleaning up...
del ec2-setup.sh

echo.
echo ✅ EC2 auto-start setup completed!
echo.
echo 🔍 To test auto-start, you can reboot the EC2 instance:
echo    ssh -i %KEY_FILE% ubuntu@%EC2_IP% "sudo reboot"
echo.
echo 📋 To check if service is running after reboot:
echo    ssh -i %KEY_FILE% ubuntu@%EC2_IP% "pm2 status"
echo.

pause 