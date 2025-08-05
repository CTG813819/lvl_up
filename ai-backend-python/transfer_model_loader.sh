#!/bin/bash

# Transfer model_loader.py to EC2 instance
echo "🚀 Transferring model_loader.py to EC2 instance..."

# Transfer the model_loader.py file
scp -i "C:\projects\lvl_up\New.pem" "app/services/model_loader.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/services/

if [ $? -eq 0 ]; then
    echo "✅ model_loader.py transferred successfully"
else
    echo "❌ Failed to transfer model_loader.py"
    exit 1
fi

# Also transfer the test script
scp -i "C:\projects\lvl_up\New.pem" "test_enhanced_adversarial_service.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

if [ $? -eq 0 ]; then
    echo "✅ test_enhanced_adversarial_service.py transferred successfully"
else
    echo "❌ Failed to transfer test script"
    exit 1
fi

echo "🎉 All files transferred successfully!"
echo "🌐 Enhanced adversarial testing service should now be available on port 8001" 