#!/bin/bash

# Transfer all files created and modified during this chat session
# Enhanced Adversarial Testing System files

echo "Transferring enhanced adversarial testing files..."

# Main service file (already transferred, but including for completeness)
scp -i "C:\projects\lvl_up\New.pem" "app/services/enhanced_adversarial_testing_service.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/services/

# Test and fix scripts
scp -i "C:\projects\lvl_up\New.pem" "test_adversarial_ai_responses.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" "fix_adversarial_ai_responses.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" "simple_adversarial_test.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

# Test reports and results
scp -i "C:\projects\lvl_up\New.pem" "simple_adversarial_test_report_20250727_172408.json" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

# Additional test files
scp -i "C:\projects\lvl_up\New.pem" "fix_challenge_methods.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" "test_sckipit_service.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" "standalone_enhanced_adversarial_testing.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" "simple_test_service.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" "debug_enhanced_service.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

# Deployment and startup scripts
scp -i "C:\projects\lvl_up\New.pem" "start_enhanced_adversarial_testing.sh" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" "enhanced-adversarial-testing.service" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" "test_enhanced_adversarial_testing.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" "deploy_enhanced_adversarial_testing.sh" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" "start_enhanced_adversarial_testing_service.bat" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" "start_enhanced_adversarial_testing.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" "start_enhanced_adversarial_testing_service.sh" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

# Documentation files
scp -i "C:\projects\lvl_up\New.pem" "ENHANCED_ADVERSARIAL_TESTING_SYSTEM.md" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" "DEPLOYMENT_SUMMARY.md" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

echo "All files transferred successfully!" 