# Setup Verification Guide

This guide helps verify that the application is set up correctly after cloning from GitHub.

## Prerequisites Checklist

Before running the application, ensure you have:

### Required Software
- [ ] **Python 3.11+** installed
  ```bash
  python --version
  # Should show Python 3.11 or higher
  ```

- [ ] **Node.js 18+** installed
  ```bash
  node --version
  # Should show v18.0.0 or higher
  ```

- [ ] **npm** installed
  ```bash
  npm --version
  ```

## Quick Setup

Run the automated test script to verify your setup:

```bash
bash test-startup.sh
```

This will check all prerequisites and dependencies.

## Manual Setup Steps

### 1. Create Python Virtual Environment
```bash
python -m venv .venv

# Activate (Windows Git Bash)
source .venv/Scripts/activate

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source .venv/bin/activate
```

### 2. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd tinko-console
npm install
cd ..
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` and set at minimum:
- `DATABASE_URL` - Your PostgreSQL database URL
- `SECRET_KEY` - Random secret string (min 32 characters)
- `JWT_SECRET` - Random secret string for JWT signing

## Verification Steps

### Backend Verification
```bash
# Test Python imports
.venv/Scripts/python.exe -c "from app.main import app; print('✅ Backend OK')"

# Start backend
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

In another terminal:
```bash
# Test health endpoint
curl http://127.0.0.1:8010/healthz
# Expected: {"ok":true}
```

### Frontend Verification
```bash
cd tinko-console

# Type check
npx tsc --noEmit
# Should complete with no errors

# Start frontend
npm run dev
```

Visit: http://localhost:3000

## Common Issues

### "ModuleNotFoundError"
**Solution**: Install Python dependencies
```bash
pip install -r requirements.txt
```

### "Cannot find module 'next'"
**Solution**: Install frontend dependencies
```bash
cd tinko-console && npm install
```

### "DATABASE_URL not set"
**Solution**: Create `.env` file
```bash
cp .env.example .env
# Edit .env with your database URL
```

### Port Already in Use
**Windows**:
```bash
netstat -ano | findstr :8010
taskkill /PID <PID> /F
```

**Linux/Mac**:
```bash
lsof -ti:8010 | xargs kill -9
```

## Success Checklist

After setup, verify:

- [ ] Backend starts without errors
- [ ] `http://127.0.0.1:8010/healthz` returns `{"ok":true}`
- [ ] `http://127.0.0.1:8010/docs` shows Swagger UI
- [ ] Frontend starts without errors
- [ ] `http://localhost:3000` loads homepage
- [ ] `http://localhost:3000/auth/signup` shows signup form

## Testing OTP Flow

1. Go to http://localhost:3000/auth/signup
2. Fill the form and click "Send OTP"
3. Check backend terminal for OTP code (banner format)
4. Enter OTP and verify

See [OTP_TESTING_GUIDE.md](./OTP_TESTING_GUIDE.md) for detailed testing instructions.

## Need Help?

Run the diagnostic script:
```bash
bash test-startup.sh
```

This will identify any setup issues.
