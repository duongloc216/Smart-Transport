# Start Backend Server
$BackendPath = "e:\CĐTT2\Smart-Transport\smart-traffic-system\backend"
Set-Location $BackendPath
Write-Host "🚀 Starting Smart Traffic Backend..." -ForegroundColor Green
Write-Host "📁 Working Directory: $BackendPath" -ForegroundColor Cyan
python main.py
