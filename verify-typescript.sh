#!/bin/bash
# TypeScript and Lint Verification Script

echo "================================================"
echo "🔍 TypeScript & ESLint Verification"
echo "================================================"
echo ""

cd tinko-console || exit 1

echo "📦 Installing dependencies..."
npm install --silent

echo ""
echo "✅ Running TypeScript type check..."
if npx tsc --noEmit; then
  echo "✓ TypeScript: PASS - No compilation errors"
else
  echo "✗ TypeScript: FAIL - Compilation errors found"
  exit 1
fi

echo ""
echo "✅ Running ESLint..."
if npx eslint . --max-warnings 0; then
  echo "✓ ESLint: PASS - No lint errors"
else
  echo "✗ ESLint: FAIL - Lint errors found"
  exit 1
fi

echo ""
echo "✅ Testing build..."
if npm run build; then
  echo "✓ Build: PASS - Production build successful"
else
  echo "✗ Build: FAIL - Build errors found"
  exit 1
fi

echo ""
echo "================================================"
echo "✅ ALL CHECKS PASSED!"
echo "================================================"
echo ""
echo "Ready to deploy! 🚀"
echo ""
echo "Next steps:"
echo "  git push origin ci/fix-import-path"
