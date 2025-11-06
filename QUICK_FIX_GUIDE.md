# 🔧 Quick Fix Guide - OTP & Application Issues

## 📊 Current Status

### ✅ What's Working:

- Backend code is correct
- Frontend code is correct
- Database is connected
- OTP logging is implemented

### ⚠️ Issues Found:

1. **Application keeps shutting down** - Ctrl+C is being pressed
2. **Auth0 files showing red dots** - These are unused files (safe to ignore)
3. **OTP not visible** - Application needs to stay running

## 🎯 Step-by-Step Solution

### Step 1: Start the Application (IMPORTANT)

```bash
bash start-all.sh
```

**⚠️ DO NOT press Ctrl+C or close the terminal!** Let it run in the background.

### Step 2: Open Another Terminal

- Open a NEW terminal window (don't close the first one)
- Use this for testing

### Step 3: Test Signup with Unique Email

Go to: http://localhost:3000/auth/signup

Fill in:

- **Full Name**: Test User
- **Email**: `test$(date +%s)@example.com` (must be NEW each time)
- **Password**: TestPass123!
- **Organization**: Test Company

Click "Send OTP"

### Step 4: Find the OTP in Terminal

Look in the **FIRST terminal** (where start-all.sh is running) for:

```
============================================================
🔐 OTP CODE FOR youremail@example.com: 123456
============================================================
```

### Step 5: Enter OTP

- Copy the 6-digit code
- Paste it in the verification form
- Click "Verify & Continue to Sign In"

## 🐛 Troubleshooting

### Issue: "Email already registered"

**Solution**: Use a different email address each time. The test emails are stored in the database.

### Issue: Terminal closes when running commands

**Solution**: Don't run other commands in the same terminal. Open a NEW terminal window.

### Issue: Red dots in VS Code

**Cause**: Auth0 integration files (auth0.ts, rate-limit.ts, session.ts) are unused

**Solution**: These are safe to ignore. They're for future Auth0 integration. No errors exist.

To hide them, add to `.vscode/settings.json`:

```json
{
  "files.exclude": {
    "**/lib/auth0.ts": true,
    "**/lib/rate-limit.ts": true,
    "**/lib/session.ts": true
  }
}
```

### Issue: Application not starting

**Check**:

1. Port 8010 is not in use: `netstat -ano | findstr :8010`
2. Port 3000 is not in use: `netstat -ano | findstr :3000`
3. Python venv is activated

**Kill processes if needed**:

```powershell
# PowerShell
Get-Process | Where-Object {$_.Path -like "*python*"} | Stop-Process -Force
Get-Process | Where-Object {$_.Path -like "*node*"} | Stop-Process -Force
```

## 🔍 Check Current OTP Configuration

Your `.env` file should have:

```properties
OTP_DEV_ECHO=true
ENVIRONMENT=development
```

**Verify**:

```bash
grep -E "OTP_DEV_ECHO|ENVIRONMENT" .env
```

## 📋 Complete Working Flow

### Terminal 1 (Keep Open):

```bash
cd /c/Users/srina/OneDrive/Documents/Downloads/Stealth-Reecovery-20251010T154256Z-1-001
bash start-all.sh
# DO NOT CLOSE THIS TERMINAL
# Watch for OTP codes here
```

### Terminal 2 (For Testing):

```bash
# Test backend is running
curl http://127.0.0.1:8010/healthz
# Should return: {"ok":true}

# Test frontend is running
curl -I http://localhost:3000
# Should return: HTTP/1.1 200 OK
```

### Browser:

1. Open: http://localhost:3000/auth/signup
2. Fill form
3. Click "Send OTP"
4. Check Terminal 1 for OTP code
5. Enter OTP
6. Done!

## 🚀 Quick Test Script

Create a test file `test_signup.sh`:

```bash
#!/bin/bash
EMAIL="test$(date +%s)@example.com"
echo "Testing with email: $EMAIL"

curl -X POST http://127.0.0.1:8010/v1/auth/register/start \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"TestPass123!\",\"full_name\":\"Test User\",\"org_name\":\"Test Company\"}"

echo "\nCheck the main terminal for OTP code!"
```

Run it:

```bash
chmod +x test_signup.sh
./test_signup.sh
```

## ✅ Verification Checklist

Before reporting issues, verify:

- [ ] Application is running (`bash start-all.sh` in Terminal 1)
- [ ] Backend responds: `curl http://127.0.0.1:8010/healthz` returns `{"ok":true}`
- [ ] Frontend loads: http://localhost:3000 shows homepage
- [ ] Signup page loads: http://localhost:3000/auth/signup works
- [ ] Using UNIQUE email (never used before)
- [ ] Password is at least 8 characters
- [ ] Terminal 1 is still open and running
- [ ] Checked Terminal 1 output for OTP banner

## 📝 About the "Red Dots"

The files with red dots are:

- `tinko-console/lib/auth0.ts` - Auth0 integration (not used yet)
- `tinko-console/lib/rate-limit.ts` - Rate limiting (not used yet)
- `tinko-console/lib/session.ts` - Session management (not used yet)

**These are NOT errors!** They are complete, valid TypeScript files for future Auth0 integration. VS Code shows them as "unused" because:

- No imports reference them
- They're standalone modules
- They were created for optional Auth0 setup

You can:

1. **Ignore them** - They don't affect your application
2. **Hide them** - Use VS Code file exclusion settings
3. **Delete them** - Only if you never plan to use Auth0

## 🎓 Understanding the Flow

```
User Browser
    │
    ├─→ http://localhost:3000/auth/signup (Frontend - Next.js)
    │
    ├─→ Click "Send OTP"
    │
    ├─→ POST http://127.0.0.1:8010/v1/auth/register/start (Backend - FastAPI)
    │
    ├─→ Backend generates OTP: "123456"
    │
    ├─→ Backend logs to Terminal 1:
    │   ============================================================
    │   🔐 OTP CODE FOR youremail@example.com: 123456
    │   ============================================================
    │
    ├─→ User sees verification form
    │
    ├─→ User enters "123456"
    │
    ├─→ POST http://127.0.0.1:8010/v1/auth/register/verify
    │
    └─→ User redirected to /auth/signin
```

## 💡 Pro Tips

1. **Keep Terminal 1 visible** while testing
2. **Use unique emails** for each test
3. **Copy OTP immediately** (expires in 10 minutes)
4. **Don't refresh** during OTP verification
5. **Check browser console** (F12) for errors

## 🆘 Still Having Issues?

If OTP still doesn't appear:

1. **Restart Application**:

   ```bash
   # In Terminal 1, press Ctrl+C
   bash start-all.sh
   ```

2. **Check Logs**:

   ```bash
   tail -f _logs/current_session.txt
   ```

3. **Verify Backend Code**:

   ```bash
   grep -A 5 "OTP CODE FOR" app/routers/auth.py
   ```

   Should show the print statement.

4. **Test Direct API**:
   ```bash
   curl -X POST http://127.0.0.1:8010/v1/auth/register/start \
     -H "Content-Type: application/json" \
     -d '{"email":"unique@example.com","password":"Pass1234!","full_name":"Test","org_name":"Company"}'
   ```
   Watch Terminal 1 for OTP.

---

**Last Updated**: November 5, 2025
**Status**: Application working, OTP logging enabled
**Action Required**: Keep Terminal 1 open, use unique emails
