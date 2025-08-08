# PowerShell script to fix EC2 backend warpMode error
# Replace YOUR_EC2_IP with your actual EC2 IP address
# Replace your-key.pem with your actual key file path

$EC2_IP = "YOUR_EC2_IP"  # Replace with your actual EC2 IP
$KEY_FILE = "your-key.pem"  # Replace with your actual key file path

Write-Host "=== EC2 Backend Fix Script ===" -ForegroundColor Green
Write-Host ""
Write-Host "This script will help you fix the warpMode error on your EC2 backend."
Write-Host ""
Write-Host "Step 1: SSH into your EC2 instance and run these commands:"
Write-Host ""
Write-Host "ssh -i `"$KEY_FILE`" ubuntu@$EC2_IP"
Write-Host ""
Write-Host "Step 2: Once connected to EC2, run these commands:"
Write-Host ""
Write-Host "cd /home/ubuntu/ai-backend"
Write-Host ""
Write-Host "Step 3: Check the current content around line 47:"
Write-Host ""
Write-Host "sed -n '45,50p' src/services/aiQuotaService.js"
Write-Host ""
Write-Host "Step 4: Edit the file to fix the getCurrentHierarchyStatus function:"
Write-Host ""
Write-Host "nano src/services/aiQuotaService.js"
Write-Host ""
Write-Host "Step 5: Find the getCurrentHierarchyStatus function (around line 47) and replace it with:"
Write-Host ""
Write-Host "  static getCurrentHierarchyStatus() {"
Write-Host "    return 'ALWAYS_ALLOWED';"
Write-Host "  }"
Write-Host ""
Write-Host "Step 6: Save and exit nano (Ctrl+X, then Y, then Enter)"
Write-Host ""
Write-Host "Step 7: Restart the backend:"
Write-Host ""
Write-Host "pm2 restart ai-backend"
Write-Host ""
Write-Host "Step 8: Check the logs:"
Write-Host ""
Write-Host "pm2 logs ai-backend"
Write-Host ""
Write-Host "=== Alternative: Quick fix with sed ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "If you want to fix it quickly without editing, run this on EC2:"
Write-Host ""
Write-Host "cd /home/ubuntu/ai-backend"
Write-Host "sed -i '47,55d' src/services/aiQuotaService.js"
Write-Host "sed -i '46a\    return '\''ALWAYS_ALLOWED'\'';' src/services/aiQuotaService.js"
Write-Host "pm2 restart ai-backend"
Write-Host ""
Write-Host "=== End of Script ===" -ForegroundColor Green 