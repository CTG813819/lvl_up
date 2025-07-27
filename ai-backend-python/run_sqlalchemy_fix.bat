@echo off
echo 🚀 Running SQLAlchemy Fix on EC2...

echo 📊 Checking current SQLAlchemy version...
ssh -i "C:/projects/lvl_up/New.pem" -o StrictHostKeyChecking=no ubuntu@34.202.215.209 "python3 -c 'import sqlalchemy; print(f\"Current: {sqlalchemy.__version__}\")'"

echo 🔄 Upgrading SQLAlchemy to 2.0.23...
ssh -i "C:/projects/lvl_up/New.pem" -o StrictHostKeyChecking=no ubuntu@34.202.215.209 "pip3 uninstall sqlalchemy -y --break-system-packages"
ssh -i "C:/projects/lvl_up/New.pem" -o StrictHostKeyChecking=no ubuntu@34.202.215.209 "pip3 install sqlalchemy==2.0.23 --break-system-packages"

echo 🔄 Restarting backend service...
ssh -i "C:/projects/lvl_up/New.pem" -o StrictHostKeyChecking=no ubuntu@34.202.215.209 "sudo systemctl stop ultimate_start"
timeout /t 3 /nobreak >nul
ssh -i "C:/projects/lvl_up/New.pem" -o StrictHostKeyChecking=no ubuntu@34.202.215.209 "sudo systemctl start ultimate_start"

echo ⏳ Waiting for service to stabilize...
timeout /t 10 /nobreak >nul

echo 🔍 Checking service status...
ssh -i "C:/projects/lvl_up/New.pem" -o StrictHostKeyChecking=no ubuntu@34.202.215.209 "sudo systemctl status ultimate_start --no-pager"

echo 🔍 Checking recent logs for _static_cache_key errors...
ssh -i "C:/projects/lvl_up/New.pem" -o StrictHostKeyChecking=no ubuntu@34.202.215.209 "sudo journalctl -u ultimate_start --since '2 minutes ago' --no-pager | grep -i '_static_cache_key' || echo '✅ No _static_cache_key errors found in recent logs'"

echo ✅ SQLAlchemy fix completed!
pause 