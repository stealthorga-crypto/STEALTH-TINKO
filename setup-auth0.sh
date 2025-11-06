#!/usr/bin/env bash
# Auth0 Integration Installation Script
set -euo pipefail

echo "🔐 Auth0 Passwordless OTP Integration Setup"
echo "==========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "AUTH0_INTEGRATION_README.md" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📦 Installing dependencies..."
echo ""

# Backend dependencies
echo "1️⃣  Installing Python dependencies..."
pip install -r requirements.auth0.txt
echo "✅ Backend dependencies installed"
echo ""

# Frontend dependencies
echo "2️⃣  Installing Node.js dependencies..."
cd tinko-console
npm install jose ioredis
echo "✅ Frontend dependencies installed"
echo ""

cd ..

# Check for environment files
echo "3️⃣  Checking environment configuration..."
echo ""

if [ ! -f "tinko-console/.env.local" ]; then
    echo "⚠️  Warning: tinko-console/.env.local not found"
    echo "📝 Creating from example..."
    cp tinko-console/.env.auth0.example tinko-console/.env.local
    echo "✅ Created .env.local - YOU MUST EDIT THIS FILE!"
    echo ""
fi

if [ ! -f ".env" ]; then
    echo "⚠️  Warning: Backend .env not found"
    echo "📝 Creating from example..."
    cp .env.auth0.backend.example .env
    echo "✅ Created .env - YOU MUST EDIT THIS FILE!"
    echo ""
fi

echo "==========================================="
echo "✅ Installation Complete!"
echo "==========================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. 🔑 Configure Auth0:"
echo "   - Visit: https://auth0.com/signup"
echo "   - Create an application"
echo "   - Enable Passwordless (Email or SMS)"
echo "   - Note your Domain, Client ID, and Client Secret"
echo ""
echo "2. ✏️  Edit Configuration Files:"
echo "   Frontend: tinko-console/.env.local"
echo "   Backend:  .env"
echo ""
echo "   Update these values:"
echo "   - AUTH0_DOMAIN"
echo "   - AUTH0_CLIENT_ID"
echo "   - AUTH0_CLIENT_SECRET"
echo "   - SESSION_SECRET (generate with: openssl rand -hex 32)"
echo ""
echo "3. 🚀 Start the Application:"
echo "   Backend:  uvicorn app.main_auth0:app --host 127.0.0.1 --port 8010 --reload"
echo "   Frontend: cd tinko-console && npm run dev"
echo ""
echo "4. 🧪 Test:"
echo "   - Signup: http://localhost:3000/auth0/signup"
echo "   - Dashboard: http://localhost:3000/auth0/dashboard"
echo "   - API: http://127.0.0.1:8010/docs"
echo ""
echo "📖 Full Documentation: AUTH0_INTEGRATION_README.md"
echo ""
