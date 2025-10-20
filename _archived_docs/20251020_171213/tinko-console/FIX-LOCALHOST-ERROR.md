# 🚨 LOCALHOST CONNECTION REFUSED - COMPLETE FIX GUIDE

## The Problem

You're seeing "ERR_CONNECTION_REFUSED" because **the development server is NOT running**.

---

## ✅ SOLUTION: Try These 3 Methods (IN ORDER)

### 🔥 METHOD 1: Use the Batch File (start-server.bat)

1. **Open File Explorer** (Windows Key + E)
2. **Copy this path exactly:**
   ```
   C:\Users\srina\OneDrive\Documents\Downloads\Stealth-Reecovery-20251010T154256Z-1-001\Stealth-Reecovery\tinko-console
   ```
3. **Paste it in File Explorer's address bar** (at the top)
4. **Press Enter**
5. **Find `start-server.bat`** (should have a gear icon)
6. **Right-click** `start-server.bat` → **Run as administrator**
7. **A black command window will open** - DO NOT CLOSE IT!
8. **Wait for this message:**
   ```
   ✓ Ready in X.Xs
   - Local:        http://localhost:3000
   ```
9. **Now open your browser** → http://localhost:3000

---

### 🔥 METHOD 2: Use PowerShell Script (EASIER)

1. **Open File Explorer** (Windows Key + E)
2. **Navigate to:**
   ```
   C:\Users\srina\OneDrive\Documents\Downloads\Stealth-Reecovery-20251010T154256Z-1-001\Stealth-Reecovery\tinko-console
   ```
3. **Find `start-server.ps1`**
4. **Right-click** `start-server.ps1` → **Run with PowerShell**
5. If you see a security warning, type **`Y`** and press Enter
6. **Wait for "✓ Ready"**
7. **Open browser** → http://localhost:3000

---

### 🔥 METHOD 3: Use VS Code Terminal (MOST RELIABLE)

1. **In VS Code, click Terminal menu** → **New Terminal** (or press Ctrl + `)
2. **Make sure you're in tinko-console directory** - you should see:
   ```
   .../Stealth-Reecovery/tinko-console
   ```
3. **Type exactly:**
   ```bash
   npm run dev
   ```
4. **Press Enter**
5. **Wait for:**
   ```
   ✓ Ready in X.Xs
   ```
6. **Open browser** → http://localhost:3000

---

## 🔍 How to Know If It's Working

### ✅ SUCCESS - You'll see:

```
▲ Next.js 15.5.4 (Turbopack)
- Local:        http://localhost:3000
- Network:      http://192.168.56.1:3000

✓ Starting...
✓ Ready in 3.9s
```

### ❌ FAILURE - You'll see errors or nothing happens

---

## ⚠️ CRITICAL RULES

1. **DO NOT CLOSE** the command/terminal window after starting
2. **The window MUST stay open** for the server to run
3. If you close it, the server stops and you get "ERR_CONNECTION_REFUSED"
4. **Only open localhost:3000 AFTER** you see "✓ Ready"

---

## 🐛 TROUBLESHOOTING

### Problem: "npm: command not found"

**Solution:** Node.js isn't installed or not in PATH

1. Download Node.js from: https://nodejs.org
2. Install it
3. Restart computer
4. Try again

### Problem: "package.json not found"

**Solution:** You're in the wrong directory

1. Make sure you're in `tinko-console` folder
2. Check the terminal shows: `.../tinko-console`

### Problem: "Port 3000 already in use"

**Solution:** Another server is running on port 3000

1. Close any other command windows
2. Open Task Manager (Ctrl + Shift + Esc)
3. Look for "node.exe" processes
4. Right-click → End Task
5. Try starting the server again

### Problem: Terminal closes immediately

**Solution:** There's an error in package.json or dependencies

1. Open VS Code Terminal
2. Type: `npm install`
3. Wait for it to complete
4. Then type: `npm run dev`

---

## 📋 STEP-BY-STEP CHECKLIST

- [ ] I opened File Explorer
- [ ] I navigated to tinko-console folder
- [ ] I double-clicked start-server.bat OR start-server.ps1
- [ ] A command window opened (did NOT close immediately)
- [ ] I waited for "✓ Ready" message
- [ ] I kept the command window OPEN
- [ ] I opened browser
- [ ] I typed: http://localhost:3000
- [ ] I can see the Tinko website

---

## 🎯 QUICK TEST

Try this to verify Node.js is working:

1. Open Command Prompt (Windows Key + R → type `cmd` → Enter)
2. Type: `node --version`
3. Press Enter
4. You should see something like: `v20.x.x`
5. Type: `npm --version`
6. You should see something like: `10.x.x`

If you DON'T see version numbers, Node.js isn't installed properly.

---

## 💡 WHAT YOU SHOULD SEE

Once the server starts and you open localhost:3000, you'll see:

**Landing Page:**

- White background
- "Welcome to Tinko" heading (blue text)
- 3 blue buttons: Sign up, Sign in, Continue as Guest
- Clean, simple design

**Dashboard (localhost:3000/dashboard):**

- 4 KPI cards showing metrics
- Recovery health section
- Next steps list
- White background with blue accents

---

## 🆘 STILL NOT WORKING?

If none of these work, tell me:

1. Which method did you try?
2. What did you see in the command window?
3. Did you see any error messages?
4. Did the command window close immediately or stay open?
5. What happens when you type `node --version` in Command Prompt?

---

**TIP:** The easiest way is METHOD 3 (VS Code Terminal) - it's the most reliable!
