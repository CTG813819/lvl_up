# Backend Validation Test Script
$EC2_IP = "3.250.201.169"
$BASE_URL = "http://$EC2_IP:8000"

Write-Host "=== BACKEND VALIDATION TESTS ===" -ForegroundColor Cyan
Write-Host "Testing backend at: $BASE_URL" -ForegroundColor Yellow
Write-Host ""

# Test 1: Valid App Creation Data
Write-Host "=== TEST 1: Valid App Creation Data ===" -ForegroundColor Green
$validData = @{
    app_name = "TestApp"
    app_description = "A comprehensive test application for validation"
    app_category = "Productivity"
    target_platform = "Android"
    user_requirements = "User authentication, data storage, push notifications"
    technical_requirements = "React Native, Firebase, REST API"
    budget_range = "1000-5000"
    timeline = "3 months"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/create-app" -Method POST -Body $validData -ContentType "application/json" -TimeoutSec 10
    Write-Host "SUCCESS: Valid data accepted" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Invalid Data - Missing Required Fields
Write-Host "=== TEST 2: Missing Required Fields ===" -ForegroundColor Yellow
$invalidData1 = @{
    app_name = "Test"
    app_description = "Short"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/create-app" -Method POST -Body $invalidData1 -ContentType "application/json" -TimeoutSec 10
    Write-Host "SUCCESS: Invalid data accepted (unexpected)" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "EXPECTED ERROR: $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

# Test 3: Invalid Data - Too Short Fields
Write-Host "=== TEST 3: Too Short Fields ===" -ForegroundColor Yellow
$invalidData2 = @{
    app_name = "A"
    app_description = "Too short description"
    app_category = "Productivity"
    target_platform = "Android"
    user_requirements = "Short"
    technical_requirements = "Short"
    budget_range = "100-500"
    timeline = "1 week"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/create-app" -Method POST -Body $invalidData2 -ContentType "application/json" -TimeoutSec 10
    Write-Host "SUCCESS: Invalid data accepted (unexpected)" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "EXPECTED ERROR: $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

# Test 4: Invalid Data - Forbidden Characters
Write-Host "=== TEST 4: Forbidden Characters ===" -ForegroundColor Yellow
$invalidData3 = @{
    app_name = "Test<App>"
    app_description = "A test app with <script>alert('xss')</script>"
    app_category = "Productivity"
    target_platform = "Android"
    user_requirements = "User authentication, data storage"
    technical_requirements = "React Native, Firebase"
    budget_range = "1000-5000"
    timeline = "3 months"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/create-app" -Method POST -Body $invalidData3 -ContentType "application/json" -TimeoutSec 10
    Write-Host "SUCCESS: Invalid data accepted (unexpected)" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "EXPECTED ERROR: $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

# Test 5: Invalid Data - Invalid Category
Write-Host "=== TEST 5: Invalid Category ===" -ForegroundColor Yellow
$invalidData4 = @{
    app_name = "TestApp"
    app_description = "A comprehensive test application for validation"
    app_category = "InvalidCategory"
    target_platform = "Android"
    user_requirements = "User authentication, data storage, push notifications"
    technical_requirements = "React Native, Firebase, REST API"
    budget_range = "1000-5000"
    timeline = "3 months"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/create-app" -Method POST -Body $invalidData4 -ContentType "application/json" -TimeoutSec 10
    Write-Host "SUCCESS: Invalid data accepted (unexpected)" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "EXPECTED ERROR: $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

# Test 6: Test Requirements Endpoint
Write-Host "=== TEST 6: Requirements Endpoint ===" -ForegroundColor Green
$requirementsData = @{
    app_name = "TestApp"
    user_requirements = "User authentication, data storage, push notifications"
    technical_requirements = "React Native, Firebase, REST API"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/define-requirements" -Method POST -Body $requirementsData -ContentType "application/json" -TimeoutSec 10
    Write-Host "SUCCESS: Requirements endpoint working" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== ALL TESTS COMPLETED ===" -ForegroundColor Cyan 