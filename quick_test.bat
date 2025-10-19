@echo off
echo ========================================
echo TINKO RECOVERY - QUICK TEST SCRIPT
echo ========================================
echo.

echo Starting Backend Server...
start "Tinko Backend" cmd /k "cd /d C:\Users\srina\OneDrive\Documents\Downloads\Stealth-Reecovery-20251010T154256Z-1-001\Stealth-Reecovery && C:\Python313\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo Waiting for backend to start...
timeout /t 10 /nobreak > nul

echo.
echo Starting Frontend Server...
start "Tinko Frontend" cmd /k "cd /d C:\Users\srina\OneDrive\Documents\Downloads\Stealth-Reecovery-20251010T154256Z-1-001\Stealth-Reecovery\tinko-console && npm run dev"

echo Waiting for frontend to start...
timeout /t 15 /nobreak > nul

echo.
echo ========================================
echo SERVERS STARTED!
echo ========================================
echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:3000
echo.
echo Testing endpoints...
timeout /t 3 /nobreak > nul

echo.
echo 1. Testing Health Endpoint...
curl -s http://127.0.0.1:8000/healthz
echo.

echo.
echo 2. Testing Readiness Endpoint...
curl -s http://127.0.0.1:8000/readyz
echo.

echo.
echo ========================================
echo QUICK TESTS COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Open browser to http://localhost:3000
echo 2. Sign in with any email/password
echo 3. Navigate through all menu options
echo 4. Test payer recovery flow
echo.
echo Press any key to run comprehensive tests...
pause > nul

cd /d C:\Users\srina\OneDrive\Documents\Downloads\Stealth-Reecovery-20251010T154256Z-1-001\Stealth-Reecovery
C:\Python313\python.exe test_all_endpoints.py

echo.
echo Press any key to exit...
pause > nul
