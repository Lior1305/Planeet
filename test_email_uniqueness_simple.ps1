# Test Email Uniqueness in Users Service
# This script tests the new email uniqueness feature

Write-Host "Testing Email Uniqueness Feature" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

$baseUrl = "http://localhost:8080/users"

# Test 1: Check if email is available (should return true)
Write-Host "`nTest 1: Checking email availability for 'test@example.com'" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/check-email?email=test@example.com" -Method Get
    Write-Host "Email availability check: $response" -ForegroundColor Green
} catch {
    Write-Host "Email availability check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Create first user with unique email
Write-Host "`nTest 2: Creating first user with email 'test@example.com'" -ForegroundColor Yellow
$user1 = @{
    username = "testuser1"
    email = "test@example.com"
    password = "password123"
    cellphoneNumber = "1234567890"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $baseUrl -Method Post -Body $user1 -ContentType "application/json"
    Write-Host "First user created successfully: $($response.username) with ID: $($response.id)" -ForegroundColor Green
    $userId1 = $response.id
} catch {
    Write-Host "First user creation failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: Try to create second user with same email (should fail)
Write-Host "`nTest 3: Trying to create second user with same email 'test@example.com'" -ForegroundColor Yellow
$user2 = @{
    username = "testuser2"
    email = "test@example.com"  # Same email!
    password = "password456"
    cellphoneNumber = "0987654321"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $baseUrl -Method Post -Body $user2 -ContentType "application/json"
    Write-Host "Second user creation should have failed but succeeded!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 409) {
        Write-Host "Second user creation correctly failed with 409 Conflict (email already exists)" -ForegroundColor Green
    } else {
        Write-Host "Second user creation failed with unexpected status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

# Test 4: Check if email is now unavailable (should return false)
Write-Host "`nTest 4: Checking email availability for 'test@example.com' (should be false now)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/check-email?email=test@example.com" -Method Get
    Write-Host "Email availability check: $response (false = email is taken)" -ForegroundColor Green
} catch {
    Write-Host "Email availability check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Create user with different email (should succeed)
Write-Host "`nTest 5: Creating user with different email 'another@example.com'" -ForegroundColor Yellow
$user3 = @{
    username = "testuser3"
    email = "another@example.com"
    password = "password789"
    cellphoneNumber = "5555555555"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $baseUrl -Method Post -Body $user3 -ContentType "application/json"
    Write-Host "Third user created successfully: $($response.username) with ID: $($response.id)" -ForegroundColor Green
    $userId3 = $response.id
} catch {
    Write-Host "Third user creation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Try to update first user's email to existing email (should fail)
Write-Host "`nTest 6: Trying to update first user's email to 'another@example.com' (should fail)" -ForegroundColor Yellow
$updateUser = @{
    username = "testuser1"
    email = "another@example.com"  # Email already exists!
    password = "password123"
    cellphoneNumber = "1234567890"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/$userId1" -Method Put -Body $updateUser -ContentType "application/json"
    Write-Host "User update should have failed but succeeded!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 409) {
        Write-Host "User update correctly failed with 409 Conflict (email already exists)" -ForegroundColor Green
    } else {
        Write-Host "User update failed with unexpected status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

# Test 7: Patch update with existing email (should fail)
Write-Host "`nTest 7: Trying to patch update with existing email 'another@example.com' (should fail)" -ForegroundColor Yellow
$patchUpdate = @{
    email = "another@example.com"  # Email already exists!
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/$userId1" -Method Patch -Body $patchUpdate -ContentType "application/json"
    Write-Host "User patch should have failed but succeeded!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 409) {
        Write-Host "User patch correctly failed with 409 Conflict (email already exists)" -ForegroundColor Green
    } else {
        Write-Host "User patch failed with unexpected status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

# Test 8: Clean up - Delete test users
Write-Host "`nTest 8: Cleaning up test users" -ForegroundColor Yellow
try {
    if ($userId1) {
        Invoke-RestMethod -Uri "$baseUrl/$userId1" -Method Delete
        Write-Host "Deleted user 1" -ForegroundColor Green
    }
    if ($userId3) {
        Invoke-RestMethod -Uri "$baseUrl/$userId3" -Method Delete
        Write-Host "Deleted user 3" -ForegroundColor Green
    }
} catch {
    Write-Host "Cleanup failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`nEmail Uniqueness Testing Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
