@echo off
REM Update EC2 IP Address in All Files
REM This script updates the EC2 IP address in all relevant files

echo 🔄 Updating EC2 IP Address
echo ==========================

if "%1"=="" (
    echo [ERROR] Please provide the new EC2 IP address
    echo.
    echo Usage: update-ec2-ip.bat NEW_IP_ADDRESS
    echo Example: update-ec2-ip.bat 52.23.45.67
    echo.
    pause
    exit /b 1
)

set NEW_IP=%1
set OLD_IP=44.204.184.21

echo [INFO] Updating IP from %OLD_IP% to %NEW_IP%
echo.

REM Update network_config.dart
echo [INFO] Updating lib/services/network_config.dart...
powershell -Command "(Get-Content 'lib/services/network_config.dart') -replace '%OLD_IP%', '%NEW_IP%' | Set-Content 'lib/services/network_config.dart'"

REM Update main.dart
echo [INFO] Updating lib/main.dart...
powershell -Command "(Get-Content 'lib/main.dart') -replace '%OLD_IP%', '%NEW_IP%' | Set-Content 'lib/main.dart'"

REM Update loading_screen.dart
echo [INFO] Updating lib/loading_screen.dart...
powershell -Command "(Get-Content 'lib/loading_screen.dart') -replace '%OLD_IP%', '%NEW_IP%' | Set-Content 'lib/loading_screen.dart'"

REM Update android_config.dart
echo [INFO] Updating lib/config/android_config.dart...
powershell -Command "(Get-Content 'lib/config/android_config.dart') -replace '%OLD_IP%', '%NEW_IP%' | Set-Content 'lib/config/android_config.dart'"

REM Update test scripts
echo [INFO] Updating test scripts...
powershell -Command "(Get-Content 'test-ec2-connection.bat') -replace '%OLD_IP%', '%NEW_IP%' | Set-Content 'test-ec2-connection.bat'"
powershell -Command "(Get-Content 'deploy-to-ec2.bat') -replace '%OLD_IP%', '%NEW_IP%' | Set-Content 'deploy-to-ec2.bat'"

echo.
echo [SUCCESS] IP address updated in all files!
echo.
echo [INFO] New backend URL: http://%NEW_IP%:4000
echo.
echo [INFO] Next steps:
echo 1. Test the connection: test-ec2-connection.bat
echo 2. Build and install the updated app on your Android device
echo 3. The app should now connect to the correct EC2 instance
echo.

pause 