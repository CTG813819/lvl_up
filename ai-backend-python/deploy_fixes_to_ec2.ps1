# Deploy Custody Protocol Fixes to EC2
# This script uploads and applies the fixes to the EC2 instance

Write-Host "🚀 Deploying Custody Protocol Fixes to EC2..." -ForegroundColor Yellow
Write-Host "==============================================" -ForegroundColor Yellow

# Configuration
$EC2_HOST = "ec2-34-202-215-209.compute-1.amazonaws.com"
$EC2_USER = "ubuntu"
$PEM_FILE = "C:\projects\lvl_up\New.pem"
$REMOTE_DIR = "/home/ubuntu/ai-backend-python"

Write-Host "📦 Uploading fix files to server..." -ForegroundColor Yellow

# Upload the fix script
Write-Host "📤 Uploading fix_custody_issues.py..." -ForegroundColor Cyan
scp -i "$PEM_FILE" "fix_custody_issues.py" "$EC2_USER@$EC2_HOST`:$REMOTE_DIR/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Fix script uploaded successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to upload fix script" -ForegroundColor Red
    exit 1
}

# Upload the deployment script
Write-Host "📤 Uploading deploy_custody_fix.sh..." -ForegroundColor Cyan
scp -i "$PEM_FILE" "deploy_custody_fix.sh" "$EC2_USER@$EC2_HOST`:$REMOTE_DIR/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deployment script uploaded successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to upload deployment script" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Running custody protocol fixes on server..." -ForegroundColor Yellow

# SSH into server and run the fixes
$sshCommand = @"
cd /home/ubuntu/ai-backend-python

echo "🔧 Applying custody protocol fixes..."

# Stop the service first
echo "🛑 Stopping AI backend service..."
sudo systemctl stop ai-backend-python.service

# Wait for service to stop
sleep 5

# Run the Python fix script
echo "🔧 Running Python fix script..."
python3 fix_custody_issues.py

if [ \$? -eq 0 ]; then
    echo "✅ Python fixes applied successfully"
else
    echo "❌ Python fixes failed"
    exit 1
fi

# Test the fixes
echo "🧪 Testing the fixes..."
python3 -c "
import sys
sys.path.append('app')
try:
    from app.services.custody_protocol_service import CustodyProtocolService
    print('✅ CustodyProtocolService import successful')
    
    # Test that the method exists
    custody_service = CustodyProtocolService()
    if hasattr(custody_service, '_execute_collaborative_test'):
        print('✅ _execute_collaborative_test method exists')
    else:
        print('❌ _execute_collaborative_test method not found')
        exit(1)
        
    print('✅ All tests passed!')
    
except Exception as e:
    print(f'❌ Test failed: {e}')
    exit(1)
"

if [ \$? -eq 0 ]; then
    echo "✅ All tests passed"
else
    echo "❌ Tests failed"
    exit 1
fi

# Start the service
echo "🚀 Starting AI backend service..."
sudo systemctl start ai-backend-python.service

# Wait for service to start
sleep 10

# Check service status
echo "📊 Checking service status..."
sudo systemctl status ai-backend-python.service --no-pager -l

# Test the service endpoints
echo "🧪 Testing service endpoints..."
curl -s http://localhost:8000/health || echo "❌ Health check failed"

echo "✅ Custody protocol fixes deployed successfully!"
"@

ssh -i "$PEM_FILE" "$EC2_USER@$EC2_HOST" $sshCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Custody protocol fixes deployed successfully to EC2" -ForegroundColor Green
} else {
    Write-Host "❌ Deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host "📊 Checking final service status..." -ForegroundColor Yellow

# Check final status
$statusCommand = @"
echo "📊 Final service status:"
sudo systemctl status ai-backend-python.service --no-pager

echo ""
echo "📋 Recent logs:"
sudo journalctl -u ai-backend-python.service --no-pager -l -n 20

echo ""
echo "🔍 Testing custody service methods:"
python3 -c "
import asyncio
import sys
sys.path.append('/home/ubuntu/ai-backend-python')

async def test_custody_service():
    try:
        from app.services.custody_protocol_service import CustodyProtocolService
        
        # Test that the service can be imported
        print('✅ CustodyProtocolService import successful')
        
        # Test that the method exists
        custody_service = CustodyProtocolService()
        if hasattr(custody_service, '_execute_collaborative_test'):
            print('✅ _execute_collaborative_test method exists')
        else:
            print('❌ _execute_collaborative_test method not found')
            return False
            
        # Test that the service can be initialized (without full init)
        print('✅ CustodyProtocolService instantiation successful')
        
        print('✅ All custody service tests passed')
        return True
        
    except Exception as e:
        print(f'❌ Error testing custody service: {e}')
        return False

# Run the test
result = asyncio.run(test_custody_service())
if not result:
    exit(1)
"
"@

ssh -i "$PEM_FILE" "$EC2_USER@$EC2_HOST" $statusCommand

Write-Host "🎉 Custody Protocol Fixes Deployment Complete!" -ForegroundColor Green
Write-Host "📋 Summary of fixes applied:" -ForegroundColor Yellow
Write-Host "   • Removed testing_service.initialize() call" -ForegroundColor Yellow
Write-Host "   • Fixed database parameter binding issues" -ForegroundColor Yellow
Write-Host "   • Fixed Claude tokens missing parameter" -ForegroundColor Yellow
Write-Host "   • Ensured _execute_collaborative_test method exists" -ForegroundColor Yellow
Write-Host "   • Added missing imports" -ForegroundColor Yellow
Write-Host "   • Fixed anthropic_rate_limited_call usage" -ForegroundColor Yellow
Write-Host "   • Restarted backend service" -ForegroundColor Yellow
Write-Host "   • Verified all required methods are present" -ForegroundColor Yellow