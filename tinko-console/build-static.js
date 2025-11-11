#!/usr/bin/env node

// Custom build script for Azure Static Web Apps
// This ensures we use standard Next.js build without turbopack

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔧 Starting Azure Static Web Apps build...');
console.log('📦 Node version:', process.version);
console.log('🚀 Next.js build without turbopack...');

// Ensure we're in the correct directory
process.chdir(__dirname);

try {
  // Set environment variables to disable turbopack
  process.env.TURBOPACK = '0';
  process.env.NODE_ENV = 'production';
  process.env.BUILD_TARGET = 'static';
  process.env.IS_STATIC_EXPORT = 'true';
  
  // Remove any potential turbopack cache
  const turbopackDir = path.join(process.cwd(), '.turbo');
  if (fs.existsSync(turbopackDir)) {
    console.log('🧹 Cleaning turbopack cache...');
    fs.rmSync(turbopackDir, { recursive: true, force: true });
  }
  
  const nextConfigPath = path.join(process.cwd(), 'next.config.ts');
  console.log('📝 Next.js config exists:', fs.existsSync(nextConfigPath));
  
  // Run Next.js build without any turbopack flags
  console.log('🏗️  Running Next.js build...');
  
  // Use platform-specific path
  const isWindows = process.platform === 'win32';
  const nextBin = isWindows ? '.\\node_modules\\.bin\\next.cmd' : './node_modules/.bin/next';
  
  // Force standard build without turbopack
  execSync(`${nextBin} build`, { 
    stdio: 'inherit',
    env: { 
      ...process.env, 
      TURBOPACK: '0',
      NODE_ENV: 'production',
      BUILD_TARGET: 'static'
    }
  });
  
  // Verify the output directory exists
  const outDir = path.join(process.cwd(), 'out');
  if (fs.existsSync(outDir)) {
    console.log('✅ Build successful! Output directory created:', outDir);
    const files = fs.readdirSync(outDir);
    console.log('📁 Files in out directory:', files.slice(0, 10));
  } else {
    throw new Error('❌ Build failed: no "out" directory created');
  }
  
} catch (error) {
  console.error('❌ Build failed:', error.message);
  process.exit(1);
}