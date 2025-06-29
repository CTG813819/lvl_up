# Fix GitHub Secrets Script
Write-Host "=== FIX GITHUB SECRETS ===" -ForegroundColor Yellow
Write-Host ""

Write-Host "1. GO TO GITHUB SECRETS:" -ForegroundColor Cyan
Write-Host "   https://github.com/CTG813819/Lvl_UP/settings/secrets/actions" -ForegroundColor White
Write-Host ""

Write-Host "2. UPDATE AWS_SSH_PRIVATE_KEY SECRET:" -ForegroundColor Cyan
Write-Host "   - Click 'Update' on AWS_SSH_PRIVATE_KEY" -ForegroundColor White
Write-Host "   - Copy and paste this ENTIRE block (including BEGIN and END lines):" -ForegroundColor White
Write-Host ""

# Read and display the private key
$privateKey = Get-Content "C:\Users\Canice\.ssh\github_actions_deploy" -Raw
Write-Host $privateKey -ForegroundColor Green
Write-Host ""

Write-Host "3. VERIFY OTHER SECRETS:" -ForegroundColor Cyan
Write-Host "   AWS_HOST: 44.204.184.21" -ForegroundColor White
Write-Host "   AWS_USER: ubuntu" -ForegroundColor White
Write-Host ""

Write-Host "4. AFTER UPDATING SECRETS:" -ForegroundColor Cyan
Write-Host "   - Go to Actions tab" -ForegroundColor White
Write-Host "   - Re-run the failed workflow" -ForegroundColor White
Write-Host "   - Or push a new commit to trigger deployment" -ForegroundColor White
Write-Host ""

Write-Host "5. TEST COMMAND:" -ForegroundColor Cyan
Write-Host "   git commit --allow-empty -m 'Fix secrets and retry deployment' && git push" -ForegroundColor White
Write-Host ""

Write-Host "=== IMPORTANT NOTES ===" -ForegroundColor Yellow
Write-Host "- Make sure to copy the ENTIRE private key including BEGIN and END lines" -ForegroundColor Red
Write-Host "- The key should be exactly as shown above (no extra spaces or characters)" -ForegroundColor Red
Write-Host "- After updating, wait 1-2 minutes for the workflow to start" -ForegroundColor Green 