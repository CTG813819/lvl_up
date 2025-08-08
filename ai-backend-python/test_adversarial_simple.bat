@echo off
echo Testing Adversarial Database Integration
echo.

set EC2_IP=34.202.215.209

echo 1. Check current imperium metrics:
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8000/api/agent-metrics/imperium | grep -o '\"xp\":[0-9]*'"
echo.

echo 2. Run adversarial test:
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s -X POST http://localhost:8001/generate-and-execute -H 'Content-Type: application/json' -d '{\"ai_types\":[\"imperium\"],\"target_domain\":\"system_level\",\"complexity\":\"basic\",\"reward_level\":\"standard\",\"adaptive\":false,\"target_weaknesses\":[]}' > /dev/null"
echo.

echo 3. Check updated imperium metrics:
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8000/api/agent-metrics/imperium | grep -o '\"xp\":[0-9]*'"
echo.

echo 4. Check recent scenarios:
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8001/recent-scenarios | grep -o '\"recent_scenarios\":\[[^]]*\]' | head -c 100"
echo. 