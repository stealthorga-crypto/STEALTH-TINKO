# Cross-platform PowerShell start script for Tinko Recovery Platform
param(
  [int]$PortBackend = 8010,
  [string]$NodePort = "3000"
)

$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$ApiUrl = "http://127.0.0.1:$PortBackend"

Write-Host "🚀 Starting Tinko Recovery Platform..." -ForegroundColor Green

# Optionally start Redis if Docker is available
try {
  docker ps | Out-Null
  $redis = (docker ps --format '{{.Names}}' | Select-String -Pattern '^tinko-redis$')
  if (-not $redis) {
    Write-Host "🐳 Starting Redis container..."
    docker run -d --name tinko-redis -p 6379:6379 redis:alpine | Out-Null
  }
  else {
    Write-Host "✅ Redis already running"
  }
}
catch {
  Write-Host "ℹ️  Docker not available or not running — skipping Redis (Celery optional in dev)"
}

Write-Host "▶️  Backend (FastAPI) on :$PortBackend"
$backend = Start-Process -NoNewWindow -PassThru -FilePath "C:/Python313/python.exe" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$PortBackend", "--reload"
Start-Sleep -Seconds 3

Write-Host "▶️  Frontend (Next.js) on :$NodePort"
$env:NEXT_PUBLIC_API_URL = $ApiUrl
$frontend = Start-Process -NoNewWindow -PassThru -FilePath "cmd.exe" -ArgumentList "/c", "cd tinko-console && if not exist node_modules npm install && npm run dev"

Write-Host "🌐 Backend:  $ApiUrl/docs"
Write-Host "🎨 Frontend: http://localhost:$NodePort"
Write-Host "💚 Health:   $ApiUrl/healthz"

# Wait for both processes
$backend.WaitForExit()
$frontend.WaitForExit()
