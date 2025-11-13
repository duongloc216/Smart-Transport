# 🔧 RETEST AFTER FIXES
# Run this after restarting backend

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " RETEST ALL ENDPOINTS - AFTER BUG FIXES" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$passed = 0
$failed = 0

# Test 1: Health Check
Write-Host "[TEST 1/6] Health Check..." -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest http://localhost:8000/health -ErrorAction Stop
    Write-Host "   ✅ PASS" -ForegroundColor Green
    $passed++
} catch {
    Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

Start-Sleep -Seconds 1

# Test 2: Get Current Traffic
Write-Host ""
Write-Host "[TEST 2/6] Get Current Traffic..." -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/current/segment_001" -ErrorAction Stop
    $content = $r.Content | ConvertFrom-Json
    if ($content.speed -and $content.intensity) {
        Write-Host "   ✅ PASS - Speed: $($content.speed) km/h, Intensity: $($content.intensity)" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "   ❌ FAIL - Missing data" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

Start-Sleep -Seconds 1

# Test 3: Get Traffic History
Write-Host ""
Write-Host "[TEST 3/6] Get Traffic History..." -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/history/segment_001?limit=10" -ErrorAction Stop
    $content = $r.Content | ConvertFrom-Json
    if ($content.total_records -gt 0) {
        Write-Host "   ✅ PASS - $($content.total_records) records returned" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "   ❌ FAIL - No records" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

Start-Sleep -Seconds 1

# Test 4: ML Prediction
Write-Host ""
Write-Host "[TEST 4/6] ML Prediction..." -ForegroundColor Yellow
try {
    $body = @{
        road_segment_id = "segment_001"
        prediction_horizon = 15
        model_type = "ensemble"
    } | ConvertTo-Json

    $r = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/predict" -Method POST -Body $body -ContentType "application/json" -ErrorAction Stop
    $content = $r.Content | ConvertFrom-Json
    if ($content.predictions) {
        Write-Host "   ✅ PASS - Predictions: $($content.predictions.Count) timesteps" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "   ❌ FAIL - No predictions" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

Start-Sleep -Seconds 1

# Test 5: Smart Routing
Write-Host ""
Write-Host "[TEST 5/6] Smart Routing..." -ForegroundColor Yellow
try {
    $body = @{
        origin = "segment_001"
        destination = "segment_010"
    } | ConvertTo-Json

    $r = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/routing/find-route" -Method POST -Body $body -ContentType "application/json" -ErrorAction Stop
    $content = $r.Content | ConvertFrom-Json
    if ($content.route -and $content.route.total_distance) {
        Write-Host "   ✅ PASS - Route: $($content.route.total_distance) km, $($content.route.total_duration) min" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "   ❌ FAIL - No route found" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

Start-Sleep -Seconds 1

# Test 6: Models Info
Write-Host ""
Write-Host "[TEST 6/6] Models Info..." -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/models/info" -ErrorAction Stop
    $content = $r.Content | ConvertFrom-Json
    if ($content.models) {
        Write-Host "   ✅ PASS - $($content.models.Count) models loaded" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "   ❌ FAIL - No models" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " TEST SUMMARY" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Passed: $passed / 6" -ForegroundColor Green
Write-Host "❌ Failed: $failed / 6" -ForegroundColor Red
Write-Host ""

if ($failed -eq 0) {
    Write-Host "🎉 ALL TESTS PASSED! System is ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Test Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "  2. Or run full test: .\test-manual.ps1" -ForegroundColor Cyan
    Write-Host "  3. Or deploy with Docker: .\test-docker.ps1" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  Some tests failed. Check errors above." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Make sure backend is running" -ForegroundColor Cyan
    Write-Host "  2. Check database connection" -ForegroundColor Cyan
    Write-Host "  3. View BUG_FIXES_20251112.md for details" -ForegroundColor Cyan
}

Write-Host ""
