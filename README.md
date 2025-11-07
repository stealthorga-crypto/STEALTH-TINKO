# Tinko Recovery Platform

A comprehensive recovery and authentication platform built with FastAPI (backend) and Next.js (frontend).

## � Table of Contents

- [Quick Start](#-quick-start)
- [Testing the Application](#-testing-the-application)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Development](#-development)
- [Testing & Verification](#-testing--verification)
- [OTP Authentication Flow](#-otp-authentication-flow)
- [Troubleshooting](#-troubleshooting)
- [API Documentation](#-api-documentation)

---

## �🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **npm** or **yarn**
- **PostgreSQL** database (we recommend [Neon](https://neon.tech))

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/stealthorga-crypto/STEALTH-TINKO.git
   cd STEALTH-TINKO
   ```

2. **Set up Python environment**

   ```bash
   python -m venv .venv

   # Windows (Git Bash)
   source .venv/Scripts/activate

   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1

   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install Python dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**

   ```bash
   cd tinko-console
   npm install
   cd ..
   ```

5. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

   **Required variables:**

   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: Random secret for encryption
   - `JWT_SECRET`: Secret for JWT tokens

6. **Run the application**

   ```bash
   bash start-all.sh
   ```

   The application will start:

   - **Backend**: http://127.0.0.1:8010
   - **Frontend**: http://localhost:3000
   - **API Docs**: http://127.0.0.1:8010/docs

---

## 🧪 Testing the Application

### Quick Test Links

Once the application is running, click these links to test:

#### Frontend (User Interface)
1. **Homepage**: http://localhost:3000
2. **Signup & OTP Test**: http://localhost:3000/auth/signup ⭐
3. **Login**: http://localhost:3000/auth/login

#### Backend (API)
1. **API Documentation (Swagger)**: http://127.0.0.1:8010/docs ⭐
2. **Health Check**: http://127.0.0.1:8010/healthz
3. **Alternative API Docs (ReDoc)**: http://127.0.0.1:8010/redoc

### Testing OTP Flow (Step-by-Step)

**Important**: Keep the terminal with `start-all.sh` VISIBLE to see the OTP code!

1. **Open Signup Page**: http://localhost:3000/auth/signup

2. **Fill the Form**:
   - Full Name: `Test User`
   - Email: `test@example.com` (use unique email each time)
   - Password: `TestPass123!` (min 8 characters)
   - Organization: `Test Company`

3. **Send OTP**:
   - Click "Send OTP" button
   - Look at your terminal - you'll see:
     ```
     ============================================================
     🔐 OTP CODE FOR test@example.com: 123456
     ============================================================
     ```

4. **Verify OTP**:
   - Enter the 6-digit OTP code
   - Click "Verify & Sign Up"
   - You should see success message

5. **Login**:
   - Go to: http://localhost:3000/auth/login
   - Enter your email and password
   - Click "Login"
   - You'll receive a JWT token

### Automated Testing

Run the verification script to check your setup:

```bash
bash test-startup.sh
```

This checks:
- ✅ Python version (>= 3.11)
- ✅ Node.js version (>= 18)
- ✅ Virtual environment exists
- ✅ Dependencies installed
- ✅ Environment file exists
- ✅ Backend imports successfully
- ✅ TypeScript compiles without errors

---

## 📋 Features

- **User Authentication**: Email + Password with OTP verification
- **Session Management**: Secure HttpOnly cookies with JWT
- **Rate Limiting**: Protection against brute force attacks
- **Recovery System**: Comprehensive recovery workflows
- **Analytics Dashboard**: Track and monitor activities
- **Responsive UI**: Modern Next.js frontend with Tailwind CSS

## 🛠️ Development

### Backend (FastAPI)

```bash
# Run backend only
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload

# Run tests
pytest

# Check code quality
black app/
flake8 app/
```

### Frontend (Next.js)

```bash
cd tinko-console

# Run dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type check
npx tsc --noEmit

# Lint
npm run lint
```

## 📁 Project Structure

```
.
├── app/                      # Backend application
│   ├── routers/             # API routes
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth_schemas.py      # Authentication schemas
│   ├── main.py              # FastAPI application
│   └── services/            # Business logic
│
├── tinko-console/           # Frontend application
│   ├── app/                 # Next.js app directory
│   │   ├── auth/           # Authentication pages
│   │   ├── api/            # API routes
│   │   └── dashboard/      # Dashboard pages
│   ├── lib/                # Utility functions
│   │   ├── api.ts          # API client
│   │   ├── auth0.ts        # Auth0 helpers
│   │   ├── session.ts      # Session management
│   │   └── rate-limit.ts   # Rate limiting
│   └── components/         # React components
│
├── migrations/              # Database migrations
├── tests/                   # Backend tests
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
├── start-all.sh           # Startup script
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available configuration options.

**Essential variables:**

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Application secret key
- `JWT_SECRET`: JWT signing secret
- `NEXT_PUBLIC_API_URL`: Backend API URL for frontend

**Optional variables:**

- `OTP_DEV_ECHO=true`: Display OTP in terminal (development only)
- `SMTP_HOST`: Email server host
- `SMTP_PORT`: Email server port
- `AUTH0_*`: Auth0 configuration (if using Auth0)

### Database Setup

1. Create a PostgreSQL database (we recommend [Neon](https://neon.tech))
2. Set `DATABASE_URL` in `.env`
3. Run migrations:
   ```bash
   # Migrations run automatically on startup
   # Or manually with Alembic:
   alembic upgrade head
   ```

## 🧪 Testing

### Run Startup Tests

```bash
bash test-startup.sh
```

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Frontend Tests

```bash
cd tinko-console

# Type check
npx tsc --noEmit

# Lint
npm run lint
```

---

## 📚 API Documentation

Once the backend is running, access the interactive API documentation at:

- **Swagger UI**: http://127.0.0.1:8010/docs
- **ReDoc**: http://127.0.0.1:8010/redoc

### Testing API Endpoints

1. Open Swagger UI: http://127.0.0.1:8010/docs
2. Find any endpoint (e.g., `POST /v1/auth/register/start`)
3. Click "Try it out"
4. Fill in the request body:
   ```json
   {
     "email": "api-test@example.com",
     "password": "TestPass123!",
     "full_name": "API Test User",
     "org_name": "API Test Org"
   }
   ```
5. Click "Execute"
6. Check the response (should be 200 OK)
7. Check terminal for OTP code

---

## 🔐 OTP Authentication Flow

### How It Works

1. **Registration (Step 1: Send OTP)**
   - User submits email, password, and details
   - System creates inactive user account
   - System generates 6-digit OTP code
   - OTP sent via email OR displayed in terminal (if `OTP_DEV_ECHO=true`)
   - OTP expires in 10 minutes

2. **Verification (Step 2: Verify OTP)**
   - User enters the 6-digit OTP code
   - System verifies OTP is correct and not expired
   - Account is activated
   - User can now login

3. **Login**
   - User submits email and password
   - System validates credentials
   - Returns JWT access token
   - Token expires in 30 minutes

4. **Authenticated Requests**
   - Include token in `Authorization: Bearer <token>` header
   - All protected endpoints require valid JWT token

### OTP Display in Development

When `OTP_DEV_ECHO=true` in `.env`, the OTP appears in the terminal with a prominent banner:

```
============================================================
🔐 OTP CODE FOR user@example.com: 123456
============================================================
```

**Important**: Keep the terminal visible when testing!

### API Endpoints

- `POST /v1/auth/register/start` - Start registration, send OTP
- `POST /v1/auth/register/verify` - Verify OTP and activate account
- `POST /v1/auth/login` - Login with email/password, get JWT token

---

## 🐛 Troubleshooting

### Common Issues

1. **"ModuleNotFoundError"**

   - Solution: Activate virtual environment and install dependencies

   ```bash
   source .venv/Scripts/activate  # Windows Git Bash
   pip install -r requirements.txt
   ```

2. **"Port already in use"**

   - Solution: Kill existing process or change port

   ```bash
   # Windows
   netstat -ano | findstr :8010
   taskkill /PID <PID> /F

   # Linux/Mac
   lsof -ti:8010 | xargs kill -9
   ```

3. **"Cannot connect to database"**

   - Solution: Verify `DATABASE_URL` in `.env`
   - Ensure database server is running and accessible

4. **Frontend build errors**
   - Solution: Delete `.next` folder and rebuild
   ```bash
   cd tinko-console
   rm -rf .next node_modules
   npm install
   npm run dev
   ```

5. **OTP not appearing in terminal**
   - Verify `OTP_DEV_ECHO=true` in `.env`
   - Check that terminal with `start-all.sh` is still running
   - Look for the banner format in terminal output

6. **"TypeScript compilation errors"**
   - Solution: All errors have been fixed. If you see any:
   ```bash
   cd tinko-console
   npm install jose  # Ensure jose package is installed
   npx tsc --noEmit  # Should pass with no errors
   ```

---

## 📝 Documentation

---

## 📝 Documentation

### Quick Reference

- **Application Status**: ✅ Verified and working
- **Last Updated**: November 7, 2025
- **Repository**: https://github.com/stealthorga-crypto/STEALTH-TINKO
- **Branch**: ci/fix-import-path

### Recent Improvements

- ✅ All TypeScript errors fixed
- ✅ OTP display with prominent banner in development
- ✅ Improved signup form with loading states and validation
- ✅ Better error handling throughout authentication flow
- ✅ Comprehensive testing documentation
- ✅ Automated verification script

### Key Files

- `.env.example` - Environment variables template (copy to `.env`)
- `requirements.txt` - Python dependencies
- `tinko-console/package.json` - Frontend dependencies
- `start-all.sh` - Application startup script
- `test-startup.sh` - Automated verification script

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 🔗 Links

- **Repository**: https://github.com/stealthorga-crypto/STEALTH-TINKO
- **Issues**: https://github.com/stealthorga-crypto/STEALTH-TINKO/issues

## 👥 Support

If you encounter any issues:

1. Run automated diagnostic: `bash test-startup.sh`
2. Review the [Troubleshooting](#-troubleshooting) section
3. Check that all environment variables are set in `.env`
4. Verify ports 8010 and 3000 are not in use
5. Open an issue with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Python version, Node version)
   - Output from `bash test-startup.sh`

### Common Setup Verification

```bash
# Check Python version
python --version  # Should be 3.11+

# Check Node version  
node --version  # Should be 18+

# Check if virtual environment is activated
which python  # Should point to .venv/Scripts/python

# Run full verification
bash test-startup.sh

# Test imports
python -c "from app.main import app; print('✅ Backend OK')"

# Test TypeScript
cd tinko-console && npx tsc --noEmit
```

---

**Happy coding! 🚀**

**Status**: ✅ Application verified and ready for deployment
