@echo off
echo Fixing AI Backend Issues...
echo.

REM Set EC2 IP
set EC2_IP=34-202-215-209

echo [1/5] Installing missing dependencies...
ssh -i "New.pem" ubuntu@ec2-%EC2_IP%.compute-1.amazonaws.com "cd /home/ubuntu/ai-backend-python && source .env && /home/ubuntu/ai-backend-python/venv/bin/pip install asyncpg psycopg2-binary"

echo [2/5] Creating database tables...
ssh -i "New.pem" ubuntu@ec2-%EC2_IP%.compute-1.amazonaws.com "cd /home/ubuntu/ai-backend-python && source .env && /home/ubuntu/ai-backend-python/venv/bin/python -c 'import asyncio; from app.core.database import create_tables; asyncio.run(create_tables())'"

echo [3/5] Stopping existing backend service...
ssh -i "New.pem" ubuntu@ec2-%EC2_IP%.compute-1.amazonaws.com "sudo systemctl stop ai-backend-python.service"

echo [4/5] Starting backend service...
ssh -i "New.pem" ubuntu@ec2-%EC2_IP%.compute-1.amazonaws.com "sudo systemctl start ai-backend-python.service"

echo [5/5] Checking service status...
ssh -i "New.pem" ubuntu@ec2-%EC2_IP%.compute-1.amazonaws.com "sudo systemctl status ai-backend-python.service --no-pager"

echo.
echo Backend issues fixed! The service should now be running properly.
echo Check the logs with: ssh -i "New.pem" ubuntu@ec2-%EC2_IP%.compute-1.amazonaws.com "sudo journalctl -u ai-backend-python.service -f" 