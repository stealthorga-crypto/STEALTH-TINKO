#!/bin/bash

# Quick Startup Test Script
# This script verifies the application can start without errors

echo "================================================"
echo "🧪 Testing Application Startup"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test result
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

# Test 1: Check Python version
echo "Test 1: Python Version..."
python_version=$(python --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
major=$(echo $python_version | cut -d. -f1)
minor=$(echo $python_version | cut -d. -f2)
if [ "$major" -gt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -ge 11 ]); then
    test_result 0 "Python $python_version (>= 3.11 required)"
else
    test_result 1 "Python $python_version (< 3.11)"
fi

# Test 2: Check Node version
echo "Test 2: Node.js Version..."
node_version=$(node --version 2>&1 | grep -oP '\d+' | head -1)
if [ "$node_version" -ge 18 ]; then
    test_result 0 "Node.js v$node_version (>= 18 required)"
else
    test_result 1 "Node.js v$node_version (< 18)"
fi

# Test 3: Check virtual environment
echo "Test 3: Python Virtual Environment..."
if [ -d ".venv" ]; then
    test_result 0 "Virtual environment exists (.venv)"
else
    test_result 1 "Virtual environment not found"
    echo -e "${YELLOW}  → Run: python -m venv .venv${NC}"
fi

# Test 4: Check if venv is activated
echo "Test 4: Virtual Environment Activation..."
if [[ "$VIRTUAL_ENV" != "" ]]; then
    test_result 0 "Virtual environment is activated"
else
    test_result 1 "Virtual environment not activated"
    echo -e "${YELLOW}  → Run: source .venv/Scripts/activate${NC}"
fi

# Test 5: Check Python dependencies
echo "Test 5: Python Dependencies..."
if .venv/Scripts/python.exe -c "import fastapi; import sqlalchemy; import uvicorn" 2>/dev/null; then
    test_result 0 "Core Python packages installed"
else
    test_result 1 "Python dependencies missing"
    echo -e "${YELLOW}  → Run: pip install -r requirements.txt${NC}"
fi

# Test 6: Check frontend dependencies
echo "Test 6: Frontend Dependencies..."
if [ -d "tinko-console/node_modules" ]; then
    test_result 0 "Frontend node_modules exists"
else
    test_result 1 "Frontend dependencies not installed"
    echo -e "${YELLOW}  → Run: cd tinko-console && npm install${NC}"
fi

# Test 7: Check environment file
echo "Test 7: Environment Configuration..."
if [ -f ".env" ]; then
    test_result 0 "Environment file (.env) exists"
else
    test_result 1 "Environment file (.env) not found"
    echo -e "${YELLOW}  → Run: cp .env.example .env${NC}"
fi

# Test 8: Test backend import
echo "Test 8: Backend Import Test..."
if .venv/Scripts/python.exe -c "from app.main import app" 2>&1 | grep -q "mounted_maintenance_router"; then
    test_result 0 "Backend can be imported successfully"
else
    test_result 1 "Backend import failed"
fi

# Test 9: TypeScript compilation
echo "Test 9: TypeScript Compilation..."
cd tinko-console
if npx tsc --noEmit > /dev/null 2>&1; then
    test_result 0 "TypeScript compiles without errors"
else
    test_result 1 "TypeScript compilation has errors"
    echo -e "${YELLOW}  → Run: cd tinko-console && npx tsc --noEmit${NC}"
fi
cd ..

# Test 10: Check required environment variables
echo "Test 10: Required Environment Variables..."
if [ -f ".env" ]; then
    if grep -q "DATABASE_URL" .env && grep -q "SECRET_KEY" .env && grep -q "JWT_SECRET" .env; then
        test_result 0 "Required environment variables present"
    else
        test_result 1 "Missing required environment variables"
        echo -e "${YELLOW}  → Check .env for: DATABASE_URL, SECRET_KEY, JWT_SECRET${NC}"
    fi
else
    test_result 1 "Cannot check environment variables (.env missing)"
fi

echo ""
echo "================================================"
echo "📊 Test Summary"
echo "================================================"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Ready to start the application:"
    echo "  bash start-all.sh"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "Please fix the issues above before running the application."
    echo "See SETUP_VERIFICATION.md for detailed setup instructions."
    echo ""
    exit 1
fi
