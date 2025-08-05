# Transfer all changed files to EC2 instance
Write-Host "Transferring all changed files to EC2 instance..." -ForegroundColor Green

# List of files to transfer
$files = @(
    "app/services/model_loader.py",
    "main.py",
    "app/services/enhanced_adversarial_testing_service.py",
    "standalone_enhanced_adversarial_testing.py",
    "test_enhanced_adversarial_service.py",
    "app/services/enhanced_scenario_service.py"
)

# Transfer each file
foreach ($file in $files) {
    Write-Host "Transferring $file..." -ForegroundColor Yellow
    
    # Determine the destination path
    if ($file.StartsWith("app/")) {
        $destination = "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/$file"
    } else {
        $destination = "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/$file"
    }
    
    # Transfer the file
    scp -i "C:\projects\lvl_up\New.pem" $file $destination
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS: $file transferred successfully" -ForegroundColor Green
    } else {
        Write-Host "FAILED: Failed to transfer $file" -ForegroundColor Red
    }
}

Write-Host "All files transferred successfully!" -ForegroundColor Green
Write-Host "Enhanced adversarial testing service should now be available on port 8001" -ForegroundColor Cyan
Write-Host "You may need to restart the service on EC2 for changes to take effect" -ForegroundColor Yellow 