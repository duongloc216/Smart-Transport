# ========================================
# SMART TRAFFIC SYSTEM - MANUAL TEST GUIDE
# ========================================

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " SMART TRAFFIC MANUAL TEST GUIDE" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "IMPORTANT: Follow these steps in order!" -ForegroundColor Yellow
Write-Host ""

# ========================================
# STEP 1: Start Backend
# ========================================
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " STEP 1: Start Backend Server" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Open a NEW PowerShell terminal (Ctrl + Shift + ``)" -ForegroundColor Yellow
Write-Host "2. Run these commands:" -ForegroundColor Yellow
Write-Host ""
Write-Host '   cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\backend"' -ForegroundColor Cyan
Write-Host '   python main.py' -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Wait for this message:" -ForegroundColor Yellow
Write-Host '   ✅ ML models loaded successfully!' -ForegroundColor Green
Write-Host '   INFO:     Uvicorn running on http://0.0.0.0:8000' -ForegroundColor Green
Write-Host ""
Write-Host "Press ENTER when backend is running..." -ForegroundColor Magenta
$null = Read-Host

# ========================================
# STEP 2: Test Backend API
# ========================================
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " STEP 2: Testing Backend API" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "[TEST 1/8] Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction Stop
    $content = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Status: $($content.status)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ FAILED: Backend not responding!" -ForegroundColor Red
    Write-Host "   Make sure backend is running in another terminal" -ForegroundColor Yellow
    exit 1
}

Start-Sleep -Seconds 1

# Test 2: Get All Traffic
Write-Host ""
Write-Host "[TEST 2/8] Get All Traffic Data..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/realtime/all" -ErrorAction Stop
    $content = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Total Segments: $($content.total)" -ForegroundColor Green
    Write-Host "   First segment: $($content.data[0].road_segment_id) - $($content.data[0].road_name)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 1

# Test 3: Get Single Segment
Write-Host ""
Write-Host "[TEST 3/8] Get Single Segment Traffic..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/current/segment_001" -ErrorAction Stop
    $content = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Segment: $($content.road_segment_id)" -ForegroundColor Green
    Write-Host "   Speed: $($content.speed) km/h" -ForegroundColor Cyan
    Write-Host "   Intensity: $($content.intensity) vehicles/hour" -ForegroundColor Cyan
    Write-Host "   Status: $($content.congestion_status)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 1

# Test 4: Get History
Write-Host ""
Write-Host "[TEST 4/8] Get Traffic History..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/history/segment_001?limit=5" -ErrorAction Stop
    $content = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ History Records: $($content.total)" -ForegroundColor Green
    Write-Host "   Latest: $($content.data[0].timestamp) - Speed: $($content.data[0].speed) km/h" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 1

# Test 5: ML Prediction
Write-Host ""
Write-Host "[TEST 5/8] ML Traffic Prediction..." -ForegroundColor Yellow
try {
    $body = @{
        road_segment_id = "segment_001"
        prediction_horizon = 15
        model_type = "ensemble"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/predict" -Method POST -Body $body -ContentType "application/json" -ErrorAction Stop
    $content = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Model Used: $($content.model_used)" -ForegroundColor Green
    Write-Host "   Predictions: $($content.predictions.Count) timesteps" -ForegroundColor Cyan
    Write-Host "   Next 15min - Speed: $($content.predictions[0].predicted_speed) km/h, Congestion: $([math]::Round($content.predictions[0].congestion_probability * 100))%" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 1

# Test 6: Smart Routing
Write-Host ""
Write-Host "[TEST 6/8] Smart Route Finding..." -ForegroundColor Yellow
try {
    $routeBody = @{
        origin = "segment_001"
        destination = "segment_010"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/routing/find-route" -Method POST -Body $routeBody -ContentType "application/json" -ErrorAction Stop
    $content = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Route Found!" -ForegroundColor Green
    Write-Host "   Total Distance: $($content.route.total_distance) km" -ForegroundColor Cyan
    Write-Host "   Total Duration: $($content.route.total_duration) minutes" -ForegroundColor Cyan
    Write-Host "   Segments in route: $($content.route.segments.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 1

# Test 7: ML Models Info
Write-Host ""
Write-Host "[TEST 7/8] ML Models Information..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/models/info" -ErrorAction Stop
    $content = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Models Loaded: $($content.models_loaded)" -ForegroundColor Green
    Write-Host "   Total Models: $($content.total_models)" -ForegroundColor Cyan
    foreach ($model in $content.models) {
        Write-Host "      - $($model.name): $($model.size_kb) KB" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 1

# Test 8: Open API Documentation
Write-Host ""
Write-Host "[TEST 8/8] Opening API Documentation..." -ForegroundColor Yellow
try {
    Start-Process "http://localhost:8000/api/docs"
    Write-Host "   ✅ API Docs opened in browser" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Please manually open: http://localhost:8000/api/docs" -ForegroundColor Yellow
}

# ========================================
# SUMMARY
# ========================================
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " TEST SUMMARY" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Backend API Tests Completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Check API Documentation: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host "2. Try endpoints manually in Swagger UI" -ForegroundColor Cyan
Write-Host "3. Test Frontend (if built): http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Additional Tests You Can Run:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Get traffic for segment_002:" -ForegroundColor Cyan
Write-Host '  Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/current/segment_002"' -ForegroundColor White
Write-Host ""
Write-Host "Predict for 30 minutes:" -ForegroundColor Cyan
Write-Host '  $body = @{ road_segment_id = "segment_001"; prediction_horizon = 30; model_type = "ensemble" } | ConvertTo-Json' -ForegroundColor White
Write-Host '  Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/predict" -Method POST -Body $body -ContentType "application/json"' -ForegroundColor White
Write-Host ""
Write-Host "Find route from segment_002 to segment_008:" -ForegroundColor Cyan
Write-Host '  $body = @{ origin = "segment_002"; destination = "segment_008" } | ConvertTo-Json' -ForegroundColor White
Write-Host '  Invoke-WebRequest -Uri "http://localhost:8000/api/v1/routing/find-route" -Method POST -Body $body -ContentType "application/json"' -ForegroundColor White
Write-Host ""
Write-Host "====================================" -ForegroundColor Green
Write-Host " 🎉 TESTING COMPLETE!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
