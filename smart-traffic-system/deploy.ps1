# Smart Traffic System - Complete Deployment Script
# Run this script to deploy the entire system

Write-Host "🚀 Smart Traffic System - Deployment Script" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
Write-Host "✓ Checking Docker installation..." -ForegroundColor Yellow
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker found" -ForegroundColor Green

# Check if docker-compose is available
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ docker-compose is not installed." -ForegroundColor Red
    exit 1
}
Write-Host "✓ docker-compose found" -ForegroundColor Green

# Navigate to project directory
Write-Host ""
Write-Host "📁 Navigating to project directory..." -ForegroundColor Yellow
cd smart-traffic-system

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env created. Please edit it with your settings." -ForegroundColor Green
    Write-Host ""
    Write-Host "Press Enter after editing .env to continue..."
    Read-Host
}

# Pull latest code (optional)
$pullCode = Read-Host "Do you want to pull latest code from git? (y/n)"
if ($pullCode -eq "y") {
    Write-Host "📥 Pulling latest code..." -ForegroundColor Yellow
    git pull origin main
}

# Build containers
Write-Host ""
Write-Host "🔨 Building Docker containers..." -ForegroundColor Yellow
docker-compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Build successful" -ForegroundColor Green

# Start services
Write-Host ""
Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start services!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Services started" -ForegroundColor Green

# Wait for services to be ready
Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service health
Write-Host ""
Write-Host "🏥 Checking service health..." -ForegroundColor Yellow

# Check Backend
$backendHealth = try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    $response.StatusCode -eq 200
} catch {
    $false
}

if ($backendHealth) {
    Write-Host "✓ Backend is healthy" -ForegroundColor Green
} else {
    Write-Host "⚠️  Backend health check failed" -ForegroundColor Yellow
}

# Check Frontend
$frontendHealth = try {
    $response = Invoke-WebRequest -Uri "http://localhost/" -UseBasicParsing
    $response.StatusCode -eq 200
} catch {
    $false
}

if ($frontendHealth) {
    Write-Host "✓ Frontend is healthy" -ForegroundColor Green
} else {
    Write-Host "⚠️  Frontend health check failed" -ForegroundColor Yellow
}

# Display service URLs
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Access URLs:" -ForegroundColor Cyan
Write-Host "   Frontend:  http://localhost" -ForegroundColor White
Write-Host "   Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:  http://localhost:8000/api/docs" -ForegroundColor White
Write-Host ""
Write-Host "📊 View logs:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f" -ForegroundColor White
Write-Host ""
Write-Host "🛑 Stop services:" -ForegroundColor Cyan
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
