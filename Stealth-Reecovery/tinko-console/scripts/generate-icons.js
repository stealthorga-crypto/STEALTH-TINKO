#!/usr/bin/env node
/* eslint-disable @typescript-eslint/no-require-imports */
/**
 * Generate PWA Icons Script
 * 
 * This script creates placeholder icons for PWA installation.
 * For production, replace with actual branded icons using tools like:
 * - https://realfavicongenerator.net/
 * - https://www.pwabuilder.com/imageGenerator
 * - Adobe Illustrator / Figma export
 */

const fs = require('fs');
const path = require('path');

const iconsDir = path.join(__dirname, '..', 'public', 'icons');

// Ensure icons directory exists
if (!fs.existsSync(iconsDir)) {
  fs.mkdirSync(iconsDir, { recursive: true });
}

const sizes = [72, 96, 128, 144, 152, 192, 384, 512];
const brandColor = '#2563eb'; // primary-600

// Generate SVG icons for each size
sizes.forEach(size => {
  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
  <rect width="${size}" height="${size}" fill="${brandColor}" rx="${size * 0.15}"/>
  <text 
    x="50%" 
    y="50%" 
    dominant-baseline="central" 
    text-anchor="middle" 
    font-family="system-ui, -apple-system, sans-serif" 
    font-size="${size * 0.5}" 
    font-weight="700" 
    fill="white"
  >T</text>
</svg>`;

  fs.writeFileSync(path.join(iconsDir, `icon-${size}x${size}.png.svg`), svg);
  console.log(`✓ Generated icon-${size}x${size}.png.svg`);
});

// Generate maskable icons (with safe zone)
[192, 512].forEach(size => {
  const padding = size * 0.1;
  const innerSize = size - (padding * 2);
  
  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
  <rect width="${size}" height="${size}" fill="${brandColor}"/>
  <rect x="${padding}" y="${padding}" width="${innerSize}" height="${innerSize}" fill="white" rx="${innerSize * 0.15}"/>
  <text 
    x="50%" 
    y="50%" 
    dominant-baseline="central" 
    text-anchor="middle" 
    font-family="system-ui, -apple-system, sans-serif" 
    font-size="${size * 0.35}" 
    font-weight="700" 
    fill="${brandColor}"
  >T</text>
</svg>`;

  fs.writeFileSync(path.join(iconsDir, `icon-maskable-${size}x${size}.png.svg`), svg);
  console.log(`✓ Generated icon-maskable-${size}x${size}.png.svg`);
});

// Generate shortcut icons
const shortcuts = ['dashboard', 'rules', 'settings'];
shortcuts.forEach(name => {
  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="96" height="96" viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg">
  <rect width="96" height="96" fill="${brandColor}" rx="14"/>
  <text 
    x="50%" 
    y="65%" 
    dominant-baseline="central" 
    text-anchor="middle" 
    font-family="system-ui, -apple-system, sans-serif" 
    font-size="12" 
    font-weight="600" 
    fill="white"
  >${name.charAt(0).toUpperCase()}</text>
</svg>`;

  fs.writeFileSync(path.join(iconsDir, `shortcut-${name}.png.svg`), svg);
  console.log(`✓ Generated shortcut-${name}.png.svg`);
});

console.log('\n🎨 Icon generation complete!');
console.log('📝 Note: These are placeholder SVGs. For production:');
console.log('   1. Design proper branded icons in Figma/Illustrator');
console.log('   2. Export as PNG at 2x resolution');
console.log('   3. Use tools like pwa-asset-generator or realfavicongenerator.net');
console.log('   4. Replace these placeholders with actual PNG files\n');
