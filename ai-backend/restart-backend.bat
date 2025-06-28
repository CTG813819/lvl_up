@echo off
echo Stopping any existing Node.js processes...
taskkill /f /im node.exe 2>nul

echo Waiting for processes to stop...
timeout /t 3 /nobreak >nul

echo Starting backend with memory management...
node --max-old-space-size=4096 --expose-gc src/index.js

pause 