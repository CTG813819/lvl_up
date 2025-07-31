# Transfer model_loader.py to EC2 instance
Write-Host "🚀 Transferring model_loader.py to EC2 instance..." -ForegroundColor Green

# Transfer the model_loader.py file
scp -i "C:\projects\lvl_up\New.pem" "app/services/model_loader.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/services/

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ model_loader.py transferred successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to transfer model_loader.py" -ForegroundColor Red
    exit 1
}

# Also transfer the test script
scp -i "C:\projects\lvl_up\New.pem" "test_enhanced_adversarial_service.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ test_enhanced_adversarial_service.py transferred successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to transfer test script" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 All files transferred successfully!" -ForegroundColor Green
Write-Host "🌐 Enhanced adversarial testing service should now be available on port 8001" -ForegroundColor Cyan 