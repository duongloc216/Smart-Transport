# 🚀 Quick Start Script for Smart Traffic System
# Run this script to quickly check your setup status

Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     SMART TRAFFIC SYSTEM - QUICK START CHECKER" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check 1: Python Version
Write-Host "[1/8] Checking Python version..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.1[0-9]") {
        Write-Host "  ✅ $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $pythonVersion (Need Python 3.10+)" -ForegroundColor Yellow
        $allGood = $false
    }
} catch {
    Write-Host "  ❌ Python not found! Please install Python 3.10+" -ForegroundColor Red
    $allGood = $false
}

# Check 2: SQL Server
Write-Host "`n[2/8] Checking SQL Server..." -ForegroundColor Cyan
try {
    $sqlService = Get-Service -Name "MSSQLSERVER" -ErrorAction SilentlyContinue
    if ($sqlService) {
        if ($sqlService.Status -eq "Running") {
            Write-Host "  ✅ SQL Server is running" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  SQL Server exists but not running" -ForegroundColor Yellow
            Write-Host "     Run: Start-Service MSSQLSERVER" -ForegroundColor Gray
            $allGood = $false
        }
    } else {
        Write-Host "  ⚠️  SQL Server not found (or using Docker)" -ForegroundColor Yellow
        Write-Host "     If using Docker, ignore this warning" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ⚠️  Cannot check SQL Server status" -ForegroundColor Yellow
}

# Check 3: .env file
Write-Host "`n[3/8] Checking .env file..." -ForegroundColor Cyan
$envPath = "smart-traffic-system\backend\.env"
if (Test-Path $envPath) {
    Write-Host "  ✅ .env file exists" -ForegroundColor Green
    
    # Check for API key
    $envContent = Get-Content $envPath -Raw
    if ($envContent -match "GOOGLE_MAPS_API_KEY=AIza") {
        Write-Host "  ✅ Google Maps API key configured" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Google Maps API key not set" -ForegroundColor Yellow
        $allGood = $false
    }
} else {
    Write-Host "  ❌ .env file not found!" -ForegroundColor Red
    Write-Host "     Run: Copy-Item 'smart-traffic-system\backend\.env.example' 'smart-traffic-system\backend\.env'" -ForegroundColor Gray
    $allGood = $false
}

# Check 4: Backend dependencies
Write-Host "`n[4/8] Checking backend dependencies..." -ForegroundColor Cyan
if (Test-Path "smart-traffic-system\backend\venv") {
    Write-Host "  ✅ Virtual environment exists" -ForegroundColor Green
    
    # Check if fastapi is installed
    $pipList = & smart-traffic-system\backend\venv\Scripts\python.exe -m pip list 2>&1
    if ($pipList -match "fastapi") {
        Write-Host "  ✅ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Dependencies not installed" -ForegroundColor Yellow
        Write-Host "     Run: cd smart-traffic-system\backend; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt" -ForegroundColor Gray
        $allGood = $false
    }
} else {
    Write-Host "  ⚠️  Virtual environment not found" -ForegroundColor Yellow
    Write-Host "     Run: cd smart-traffic-system\backend; python -m venv venv" -ForegroundColor Gray
    $allGood = $false
}

# Check 5: Database connection
Write-Host "`n[5/8] Checking database..." -ForegroundColor Cyan
if (Test-Path "smart-traffic-system\backend\test_db.py") {
    Write-Host "  ℹ️  Run 'python test_db.py' to test database connection" -ForegroundColor Cyan
} else {
    Write-Host "  ℹ️  Test script available" -ForegroundColor Cyan
}

# Check 6: Road segments data
Write-Host "`n[6/8] Checking road segments data..." -ForegroundColor Cyan
if (Test-Path "smart-traffic-system\ml-pipeline\data\road_segments.json") {
    $segments = Get-Content "smart-traffic-system\ml-pipeline\data\road_segments.json" | ConvertFrom-Json
    Write-Host "  ✅ Found $($segments.Count) road segments configured" -ForegroundColor Green
} else {
    Write-Host "  ❌ road_segments.json not found!" -ForegroundColor Red
    $allGood = $false
}

# Check 7: ML dependencies
Write-Host "`n[7/8] Checking ML dependencies..." -ForegroundColor Cyan
if (Test-Path "smart-traffic-system\backend\venv") {
    $pipList = & smart-traffic-system\backend\venv\Scripts\python.exe -m pip list 2>&1
    
    $hastensorflow = $pipList -match "tensorflow"
    $hasxgboost = $pipList -match "xgboost"
    
    if ($hastenserflow -and $hasxgboost) {
        Write-Host "  ✅ ML libraries installed (TensorFlow, XGBoost)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Some ML libraries missing" -ForegroundColor Yellow
        Write-Host "     Run: cd smart-traffic-system\ml-pipeline; pip install -r requirements.txt" -ForegroundColor Gray
    }
}

# Check 8: Documentation
Write-Host "`n[8/8] Checking documentation..." -ForegroundColor Cyan
$docs = @("ROADMAP.md", "SETUP_GUIDE.md", "PROGRESS.md", "README.md")
$foundDocs = 0
foreach ($doc in $docs) {
    if (Test-Path $doc) {
        $foundDocs++
    }
}
Write-Host "  ✅ Found $foundDocs/4 documentation files" -ForegroundColor Green

# Summary
Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "                          SUMMARY" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan

if ($allGood) {
    Write-Host "`n  🎉 GREAT! Your environment is ready!" -ForegroundColor Green
    Write-Host "`n  Next steps:" -ForegroundColor Cyan
    Write-Host "    1. Run database test: cd smart-traffic-system\backend; python test_db.py" -ForegroundColor White
    Write-Host "    2. Start backend: python main.py" -ForegroundColor White
    Write-Host "    3. Visit: http://localhost:8000/api/docs" -ForegroundColor White
    Write-Host "    4. Start data collection: cd ..\ml-pipeline\scripts; python collect_google_traffic.py" -ForegroundColor White
} else {
    Write-Host "`n  ⚠️  Some issues found. Please fix them first." -ForegroundColor Yellow
    Write-Host "`n  📖 See SETUP_GUIDE.md for detailed instructions" -ForegroundColor Cyan
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to see next steps
$response = Read-Host "`nDo you want to see detailed next steps? (yes/no)"
if ($response -eq "yes" -or $response -eq "y") {
    Write-Host "`n" -NoNewline
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "                    DETAILED NEXT STEPS" -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "🔧 STEP 1: Setup SQL Server" -ForegroundColor Green
    Write-Host "   Option A - Docker (Recommended):" -ForegroundColor Cyan
    Write-Host "     docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=YourStrong@Passw0rd' -p 1433:1433 --name sql-server -d mcr.microsoft.com/mssql/server:2019-latest" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   Option B - Install SQL Server Express:" -ForegroundColor Cyan
    Write-Host "     https://www.microsoft.com/en-us/sql-server/sql-server-downloads" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "📊 STEP 2: Create Database" -ForegroundColor Green
    Write-Host "   sqlcmd -S localhost -U sa -P 'YourStrong@Passw0rd' -i 'smart-traffic-system\database\schemas\create_all.sql'" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "🗺️ STEP 3: Setup Google Maps API" -ForegroundColor Green
    Write-Host "   1. Go to: https://console.cloud.google.com/" -ForegroundColor Gray
    Write-Host "   2. Create project: 'Smart Traffic System'" -ForegroundColor Gray
    Write-Host "   3. Enable APIs: Distance Matrix API, Roads API" -ForegroundColor Gray
    Write-Host "   4. Create API Key and add to .env file" -ForegroundColor Gray
    Write-Host "   5. Enable Billing (you get `$200 free credit/month)" -ForegroundColor Gray
    Write-Host "   See: smart-traffic-system\ml-pipeline\scripts\GOOGLE_MAPS_SETUP.md" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "🌱 STEP 4: Seed Road Segments" -ForegroundColor Green
    Write-Host "   cd smart-traffic-system\ml-pipeline\scripts" -ForegroundColor Gray
    Write-Host "   python seed_road_segments.py" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "📡 STEP 5: Start Data Collection (Run 24/7 for 7 days)" -ForegroundColor Green
    Write-Host "   python collect_google_traffic.py" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "🚀 STEP 6: Start Backend" -ForegroundColor Green
    Write-Host "   cd ..\..\backend" -ForegroundColor Gray
    Write-Host "   python main.py" -ForegroundColor Gray
    Write-Host "   Visit: http://localhost:8000/api/docs" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "💡 Tip: Read ROADMAP.md for the complete 11-step development plan" -ForegroundColor Yellow
Write-Host ""
