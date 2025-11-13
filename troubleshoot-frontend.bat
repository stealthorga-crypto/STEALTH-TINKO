@echo off
echo ========================================
echo FRONTEND TROUBLESHOOTING SCRIPT
echo ========================================
echo.

echo [1/5] Checking if frontend is running...
netstat -ano | findstr :3000 >nul
if errorlevel 1 (
    echo ❌ Frontend is NOT running on port 3000
    echo Starting frontend now...
    cd tinko-console
    start cmd /k "npm run dev"
    echo ✅ Frontend started in new window
    echo Waiting 10 seconds for it to fully start...
    timeout /t 10 /nobreak >nul
) else (
    echo ✅ Frontend is running on port 3000
)

echo.
echo [2/5] Checking if backend is running...
netstat -ano | findstr :8010 >nul
if errorlevel 1 (
    echo ❌ Backend is NOT running on port 8010
    echo You may need to start it manually with: bash start-backend.sh
) else (
    echo ✅ Backend is running on port 8010
)

echo.
echo [3/5] Testing basic HTML file...
curl -s http://localhost:3000/clicktest.html 2>nul | findstr "Simple JavaScript Test" >nul
if errorlevel 1 (
    echo ❌ Cannot access clicktest.html
) else (
    echo ✅ clicktest.html is accessible
)

echo.
echo [4/5] Testing API proxy...
curl -s http://localhost:3000/healthz 2>nul | findstr "ok" >nul
if errorlevel 1 (
    echo ❌ API proxy not working
) else (
    echo ✅ API proxy is working
)

echo.
echo [5/5] Opening test pages...
start http://localhost:3000/clicktest.html
timeout /t 2 /nobreak >nul
start http://localhost:3000/test
timeout /t 2 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================
echo TROUBLESHOOTING STEPS
echo ========================================
echo.
echo 1. First, test the SIMPLE page:
echo    http://localhost:3000/clicktest.html
echo.
echo    - Click the buttons
echo    - If they work: JavaScript is enabled ✅
echo    - If they don't work: JavaScript is blocked ❌
echo.
echo 2. Then, test the NEXT.JS page:
echo    http://localhost:3000/test
echo.
echo    - Click the "Click Count" button
echo    - If it works: React is hydrating ✅
echo    - If it doesn't: React hydration issue ❌
echo.
echo 3. If clicktest.html works but Next.js doesn't:
echo    - Press Ctrl+Shift+R to hard refresh
echo    - Clear browser cache
echo    - Check F12 Console for errors
echo.
echo 4. If clicktest.html doesn't work:
echo    - Enable JavaScript in browser settings
echo    - Disable ad blockers
echo    - Try a different browser
echo.
echo ========================================
pause
