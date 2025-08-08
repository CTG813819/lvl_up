@echo off
REM Check EC2 Status and Find Correct IP
REM This script helps identify the correct EC2 IP address

echo 🔍 Checking EC2 Status
echo =====================

echo [INFO] The EC2 instance at 44.204.184.21 is not reachable.
echo.
echo [INFO] Possible reasons:
echo 1. EC2 instance is stopped or terminated
echo 2. IP address has changed (EC2 instances get new IPs when restarted)
echo 3. Security group is blocking connections
echo 4. Instance is in a different region
echo.

echo [INFO] To fix this, you need to:
echo.
echo 1. Check AWS Console:
echo    - Go to AWS Console > EC2 > Instances
echo    - Look for your LVL UP instance
echo    - Check if it's running (green status)
echo    - Note the current Public IP address
echo.

echo 2. If instance is stopped:
echo    - Right-click > Start instance
echo    - Wait for it to start (may take 1-2 minutes)
echo    - Note the new Public IP address
echo.

echo 3. If instance is running but IP changed:
echo    - Copy the new Public IP address
echo    - Update the app configuration with the new IP
echo.

echo 4. Check Security Group:
echo    - Click on the instance > Security tab
echo    - Make sure port 4000 is open (inbound rule)
echo    - Add rule: Type=Custom TCP, Port=4000, Source=0.0.0.0/0
echo.

echo [INFO] Once you have the correct IP, update these files:
echo - lib/services/network_config.dart
echo - lib/main.dart
echo - lib/loading_screen.dart
echo - lib/config/android_config.dart
echo.

echo [INFO] Or run this command to update all files at once:
echo set NEW_IP=your_new_ec2_ip
echo powershell -Command "(Get-Content *.dart) -replace '44.204.184.21', '%NEW_IP%' | Set-Content *.dart"
echo.

pause 