# Auth0 Integration Installation Script (Windows PowerShell)

Write-Host "🔐 Auth0 Passwordless OTP Integration Setup" -ForegroundColor Cyan
Write-Host "==========================================="
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "AUTH0_INTEGRATION_README.md")) {
  Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
  exit 1
}

Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
Write-Host ""

# Backend dependencies
Write-Host "1️⃣  Installing Python dependencies..." -ForegroundColor Green
pip install -r requirements.auth0.txt
Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
Write-Host ""

# Frontend dependencies
Write-Host "2️⃣  Installing Node.js dependencies..." -ForegroundColor Green
Set-Location tinko-console
npm install jose ioredis
Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
Write-Host ""

Set-Location ..

# Check for environment files
Write-Host "3️⃣  Checking environment configuration..." -ForegroundColor Green
Write-Host ""

if (-not (Test-Path "tinko-console\.env.local")) {
  Write-Host "⚠️  Warning: tinko-console\.env.local not found" -ForegroundColor Yellow
  Write-Host "📝 Creating from example..." -ForegroundColor Yellow
  Copy-Item "tinko-console\.env.auth0.example" "tinko-console\.env.local"
  Write-Host "✅ Created .env.local - YOU MUST EDIT THIS FILE!" -ForegroundColor Green
  Write-Host ""
}

if (-not (Test-Path ".env")) {
  Write-Host "⚠️  Warning: Backend .env not found" -ForegroundColor Yellow
  Write-Host "📝 Creating from example..." -ForegroundColor Yellow
  Copy-Item ".env.auth0.backend.example" ".env"
  Write-Host "✅ Created .env - YOU MUST EDIT THIS FILE!" -ForegroundColor Green
  Write-Host ""
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 🔑 Configure Auth0:" -ForegroundColor Cyan
Write-Host "   - Visit: https://auth0.com/signup"
Write-Host "   - Create an application"
Write-Host "   - Enable Passwordless (Email or SMS)"
Write-Host "   - Note your Domain, Client ID, and Client Secret"
Write-Host ""
Write-Host "2. ✏️  Edit Configuration Files:" -ForegroundColor Cyan
Write-Host "   Frontend: tinko-console\.env.local"
Write-Host "   Backend:  .env"
Write-Host ""
Write-Host "   Update these values:"
Write-Host "   - AUTH0_DOMAIN"
Write-Host "   - AUTH0_CLIENT_ID"
Write-Host "   - AUTH0_CLIENT_SECRET"
Write-Host "   - SESSION_SECRET (generate with PowerShell command below)"
Write-Host ""
Write-Host "   Generate SESSION_SECRET:" -ForegroundColor Yellow
Write-Host "   -join ((1..32) | ForEach-Object { '{0:X2}' -f (Get-Random -Max 256) })"
Write-Host ""
Write-Host "3. 🚀 Start the Application:" -ForegroundColor Cyan
Write-Host "   Backend:  uvicorn app.main_auth0:app --host 127.0.0.1 --port 8010 --reload"
Write-Host "   Frontend: cd tinko-console; npm run dev"
Write-Host ""
Write-Host "4. 🧪 Test:" -ForegroundColor Cyan
Write-Host "   - Signup: http://localhost:3000/auth0/signup"
Write-Host "   - Dashboard: http://localhost:3000/auth0/dashboard"
Write-Host "   - API: http://127.0.0.1:8010/docs"
Write-Host ""
Write-Host "📖 Full Documentation: AUTH0_INTEGRATION_README.md" -ForegroundColor Cyan
Write-Host ""
