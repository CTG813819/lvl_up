# Transfer the fixed Flutter file
Write-Host "Transferring fixed Flutter file..." -ForegroundColor Green

<<<<<<< HEAD
=======
# Navigate to the correct directory and transfer the file
cd C:\projects\lvl_up

>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
# Transfer the updated the_warp_screen.dart file
scp -i "C:\projects\lvl_up\New.pem" "lib/screens/the_warp_screen.dart" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/lvl_up/lib/screens/

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: the_warp_screen.dart transferred successfully" -ForegroundColor Green
} else {
    Write-Host "FAILED: Failed to transfer the_warp_screen.dart" -ForegroundColor Red
}

Write-Host "Flutter fix transferred successfully!" -ForegroundColor Green
Write-Host "The enhanced adversarial testing should now work correctly on port 8001" -ForegroundColor Cyan 