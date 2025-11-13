# ========================================
# SMART TRAFFIC SYSTEM - DOCKER TEST GUIDE
# ========================================

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " SMART TRAFFIC DOCKER TEST GUIDE" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Docker
Write-Host "[1/6] Checking Docker..." -ForegroundColor Yellow
$dockerVersion = docker --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Docker: $dockerVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ Docker not installed!" -ForegroundColor Red
    exit 1
}

$composeVersion = docker-compose --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Docker Compose: $composeVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ Docker Compose not installed!" -ForegroundColor Red
    exit 1
}

# Step 2: Navigate to project
Write-Host ""
Write-Host "[2/6] Navigating to project directory..." -ForegroundColor Yellow
$ProjectPath = "e:\CĐTT2\Smart-Transport\smart-traffic-system"
Set-Location $ProjectPath
Write-Host "   ✅ Current directory: $(Get-Location)" -ForegroundColor Green

# Step 3: Check .env file
Write-Host ""
Write-Host "[3/6] Checking environment file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   ✅ .env file exists" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Creating .env from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "   ✅ .env file created" -ForegroundColor Green
}

# Step 4: Stop existing containers
Write-Host ""
Write-Host "[4/6] Stopping existing containers..." -ForegroundColor Yellow
docker-compose down
Write-Host "   ✅ Containers stopped" -ForegroundColor Green

# Step 5: Build and start containers
Write-Host ""
Write-Host "[5/6] Building and starting containers..." -ForegroundColor Yellow
Write-Host "   ⏳ This may take 5-10 minutes for first build..." -ForegroundColor Cyan
docker-compose up --build -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Containers started successfully!" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to start containers" -ForegroundColor Red
    exit 1
}

# Step 6: Wait for services
Write-Host ""
Write-Host "[6/6] Waiting for services to be ready..." -ForegroundColor Yellow
Write-Host "   ⏳ Waiting 30 seconds for initialization..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

# Test services
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " TESTING SERVICES" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan

# Test Backend
Write-Host ""
Write-Host "Testing Backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Backend is running at http://localhost:8000" -ForegroundColor Green
        Write-Host "   📄 API Docs: http://localhost:8000/api/docs" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Backend not responding" -ForegroundColor Red
}

# Test Frontend
Write-Host ""
Write-Host "Testing Frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost" -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Frontend is running at http://localhost" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  Frontend not ready yet (may need more time)" -ForegroundColor Yellow
}

# Show container status
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " CONTAINER STATUS" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
docker-compose ps

# Show logs
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " USEFUL COMMANDS" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "View Backend Logs:" -ForegroundColor Yellow
Write-Host "   docker-compose logs backend -f" -ForegroundColor White
Write-Host ""
Write-Host "View Frontend Logs:" -ForegroundColor Yellow
Write-Host "   docker-compose logs frontend -f" -ForegroundColor White
Write-Host ""
Write-Host "View All Logs:" -ForegroundColor Yellow
Write-Host "   docker-compose logs -f" -ForegroundColor White
Write-Host ""
Write-Host "Stop All Services:" -ForegroundColor Yellow
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "Restart Services:" -ForegroundColor Yellow
Write-Host "   docker-compose restart" -ForegroundColor White
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " ACCESS POINTS" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend Dashboard:" -ForegroundColor Yellow
Write-Host "   http://localhost" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Documentation:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "====================================" -ForegroundColor Green
Write-Host " ✅ DOCKER DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
