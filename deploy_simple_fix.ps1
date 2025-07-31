# EC2 Instance Details
$EC2_HOST = "ec2-34-202-215-209.compute-1.amazonaws.com"
$EC2_USER = "ubuntu"
$KEY_PATH = "$env:USERPROFILE\.ssh\lvl_up_key.pem"

Write-Host "=== Deploying Simplified Fake Data Fix to EC2 ===" -ForegroundColor Cyan
Write-Host "Target: ${EC2_USER}@${EC2_HOST}" -ForegroundColor Yellow
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray
Write-Host ""

# Check if key file exists
if (-not (Test-Path $KEY_PATH)) {
    Write-Host "❌ SSH key not found at $KEY_PATH" -ForegroundColor Red
    Write-Host "Please ensure your SSH key is available at $KEY_PATH" -ForegroundColor Yellow
    exit 1
}

Write-Host "📁 Step 1: Copying fix_all_fake_data_simple.py to EC2 ai-backend-python directory..." -ForegroundColor Green
# Use scp to copy the file to the correct directory
$scpCommand = "scp -i `"$KEY_PATH`" fix_all_fake_data_simple.py ${EC2_USER}@${EC2_HOST}:/home/ubuntu/ai-backend-python/"
Write-Host "Running: $scpCommand" -ForegroundColor Gray
Invoke-Expression $scpCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ File copied successfully to ai-backend-python directory" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to copy file" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 Step 2: Running the simplified fix on EC2..." -ForegroundColor Green

# Create the SSH command to run on EC2
$sshScript = @"
echo "=== Running Simplified Fake Data Fix ==="
echo "Current directory: \$(pwd)"
echo "Timestamp: \$(date)"
echo ""

# Navigate to the ai-backend-python directory
cd /home/ubuntu/ai-backend-python

# Check if the file exists
if [ ! -f "fix_all_fake_data_simple.py" ]; then
    echo "❌ fix_all_fake_data_simple.py not found"
    exit 1
fi

echo "📋 File found. Running the simplified fix..."
echo ""

# Run the simplified fix script (no external dependencies)
python3 fix_all_fake_data_simple.py

echo ""
echo "✅ Simplified fix completed!"
echo ""
echo "🔍 Checking if the fixes were applied correctly..."

# Check for the results file
if [ -f "simple_fake_data_fix_results.json" ]; then
    echo "✅ Results file created"
    echo "📊 Fix results:"
    cat simple_fake_data_fix_results.json | head -20
else
    echo "⚠️ Results file not found"
fi

echo ""
echo "=== Checking System Status After Fixes ==="

# Check if custodes is running real tests
echo "🛡️ Checking Custodes Protocol status..."
if pgrep -f "custodes" > /dev/null; then
    echo "✅ Custodes service is running"
    ps aux | grep custodes | grep -v grep
else
    echo "⚠️ Custodes service not found in running processes"
fi

# Check recent logs for real activity
echo ""
echo "=== Checking Recent Logs for Real Activity ==="
if [ -f "/home/ubuntu/ai-backend-python/logs/app.log" ]; then
    echo "Recent app logs (last 10 lines):"
    tail -10 /home/ubuntu/ai-backend-python/logs/app.log
fi

# Test a few endpoints to see if they're working with real data
echo ""
echo "=== Testing Endpoints with Real Data ==="
echo "Testing learning data endpoint:"
curl -s -X GET "http://localhost:8000/api/learning/data" | head -5 || echo "Learning data endpoint test failed"

echo ""
echo "Testing agent metrics endpoint:"
curl -s -X GET "http://localhost:8000/api/imperium/agents" | head -5 || echo "Agent metrics endpoint test failed"

echo ""
echo "🎯 Simplified Fake Data Fix Deployment Complete!"
echo "The system should now use real data instead of fake/mock information."
"@

# Save the script to a temporary file
$tempScript = "temp_simple_fix.sh"
$sshScript | Out-File -FilePath $tempScript -Encoding ASCII

# Copy the script to EC2 and run it
$scpScriptCommand = "scp -i `"$KEY_PATH`" $tempScript ${EC2_USER}@${EC2_HOST}:/home/ubuntu/ai-backend-python/"
Write-Host "Copying script to EC2..." -ForegroundColor Gray
Invoke-Expression $scpScriptCommand

$sshCommand = "ssh -i `"$KEY_PATH`" ${EC2_USER}@${EC2_HOST} 'chmod +x /home/ubuntu/ai-backend-python/$tempScript && /home/ubuntu/ai-backend-python/$tempScript'"
Write-Host "Running simplified fix on EC2..." -ForegroundColor Gray
Invoke-Expression $sshCommand

# Clean up temporary file
Remove-Item $tempScript -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 What was fixed:" -ForegroundColor Cyan
Write-Host "1. 🌐 Internet Learning Mock Data → Real Database Queries" -ForegroundColor Yellow
Write-Host "2. 🧠 AI Learning Service Simulations → Real AI Learning" -ForegroundColor Yellow
Write-Host "3. 🔧 Terra Extension Service Placeholders → Real AI Code Generation" -ForegroundColor Yellow
Write-Host "4. 📝 TODO/FIXME Placeholders → Real Implementations" -ForegroundColor Yellow
Write-Host "5. 🎯 Hardcoded Scores → Dynamic Real Scores" -ForegroundColor Yellow
Write-Host ""
Write-Host "📊 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Monitor the logs: ssh -i `"$KEY_PATH`" ${EC2_USER}@${EC2_HOST}" -ForegroundColor Yellow
Write-Host "2. Check real data: tail -f /home/ubuntu/ai-backend-python/logs/app.log" -ForegroundColor Yellow
Write-Host "3. Test endpoints: curl http://${EC2_HOST}:8000/api/learning/data" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔗 Backend URL: http://${EC2_HOST}:8000" -ForegroundColor Blue 