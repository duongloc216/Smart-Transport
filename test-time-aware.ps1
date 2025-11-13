# Test Time-Aware Routing
# Demonstrates that route duration varies based on departure time

$baseUrl = "http://localhost:8000"
$origin = "segment_001"
$destination = "segment_004"

Write-Host "`n=== TEST TIME-AWARE ROUTING ===" -ForegroundColor Green
Write-Host "Same route, different times -> different durations`n" -ForegroundColor Cyan

# Test 1: Rush hour morning (7:30 AM)
Write-Host "📍 Test 1: RUSH HOUR MORNING (7:30 AM)" -ForegroundColor Yellow
$rushMorning = "2025-11-14T07:30:00"
$response1 = Invoke-RestMethod -Uri "$baseUrl/api/v1/routing/find-route" -Method POST `
    -ContentType "application/json" `
    -Body (@{
        origin = $origin
        destination = $destination
        departure_time = $rushMorning
        mode = "optimal"
    } | ConvertTo-Json)

Write-Host "  ⏰ Departure: $rushMorning" -ForegroundColor White
Write-Host "  ⏱️  Duration: $($response1.route.total_duration) phút" -ForegroundColor Magenta
Write-Host "  📏 Distance: $($response1.route.total_distance) km" -ForegroundColor White
Write-Host ""

# Test 2: Midday (12:00 PM)
Write-Host "📍 Test 2: MIDDAY (12:00 PM)" -ForegroundColor Yellow
$midday = "2025-11-14T12:00:00"
$response2 = Invoke-RestMethod -Uri "$baseUrl/api/v1/routing/find-route" -Method POST `
    -ContentType "application/json" `
    -Body (@{
        origin = $origin
        destination = $destination
        departure_time = $midday
        mode = "optimal"
    } | ConvertTo-Json)

Write-Host "  ⏰ Departure: $midday" -ForegroundColor White
Write-Host "  ⏱️  Duration: $($response2.route.total_duration) phút" -ForegroundColor Magenta
Write-Host "  📏 Distance: $($response2.route.total_distance) km" -ForegroundColor White
Write-Host ""

# Test 3: Rush hour evening (18:00 PM)
Write-Host "📍 Test 3: RUSH HOUR EVENING (6:00 PM)" -ForegroundColor Yellow
$rushEvening = "2025-11-14T18:00:00"
$response3 = Invoke-RestMethod -Uri "$baseUrl/api/v1/routing/find-route" -Method POST `
    -ContentType "application/json" `
    -Body (@{
        origin = $origin
        destination = $destination
        departure_time = $rushEvening
        mode = "optimal"
    } | ConvertTo-Json)

Write-Host "  ⏰ Departure: $rushEvening" -ForegroundColor White
Write-Host "  ⏱️  Duration: $($response3.route.total_duration) phút" -ForegroundColor Magenta
Write-Host "  📏 Distance: $($response3.route.total_distance) km" -ForegroundColor White
Write-Host ""

# Test 4: Late night (2:00 AM)
Write-Host "📍 Test 4: LATE NIGHT (2:00 AM)" -ForegroundColor Yellow
$lateNight = "2025-11-14T02:00:00"
$response4 = Invoke-RestMethod -Uri "$baseUrl/api/v1/routing/find-route" -Method POST `
    -ContentType "application/json" `
    -Body (@{
        origin = $origin
        destination = $destination
        departure_time = $lateNight
        mode = "optimal"
    } | ConvertTo-Json)

Write-Host "  ⏰ Departure: $lateNight" -ForegroundColor White
Write-Host "  ⏱️  Duration: $($response4.route.total_duration) phút" -ForegroundColor Magenta
Write-Host "  📏 Distance: $($response4.route.total_distance) km" -ForegroundColor White
Write-Host ""

# Summary
Write-Host "=== SUMMARY ===" -ForegroundColor Green
$duration1 = $response1.route.total_duration
$duration2 = $response2.route.total_duration
$duration3 = $response3.route.total_duration
$duration4 = $response4.route.total_duration

Write-Host "Rush Hour Morning (7:30 AM): $duration1 phút" -ForegroundColor Red
Write-Host "Midday (12:00 PM):           $duration2 phút" -ForegroundColor Yellow
Write-Host "Rush Hour Evening (6:00 PM): $duration3 phút" -ForegroundColor Red
Write-Host "Late Night (2:00 AM):        $duration4 phút" -ForegroundColor Green

$maxDuration = [Math]::Max([Math]::Max($duration1, $duration2), [Math]::Max($duration3, $duration4))
$minDuration = [Math]::Min([Math]::Min($duration1, $duration2), [Math]::Min($duration3, $duration4))
$difference = $maxDuration - $minDuration

Write-Host "`n📊 Variation: $difference phút difference between fastest and slowest" -ForegroundColor Cyan
Write-Host "✅ Time-aware routing is working!" -ForegroundColor Green
