#!/usr/bin/env node

/**
 * Script to generate PWA icons from upskill-logo.svg
 * 
 * Requirements:
 * - Install sharp: npm install --save-dev sharp
 * - Install svg2png or use sharp with svg
 * 
 * Usage: node generate-icons.js
 */

const fs = require('fs');
const path = require('path');

// Check if sharp is available
let sharp;
try {
  sharp = require('sharp');
} catch (e) {
  console.error('Error: sharp package is required. Install it with: npm install --save-dev sharp');
  process.exit(1);
}

const svgPath = path.join(__dirname, 'public', 'upskill-logo.svg');
const publicDir = path.join(__dirname, 'public');

// Check if SVG exists
if (!fs.existsSync(svgPath)) {
  console.error(`Error: SVG file not found at ${svgPath}`);
  process.exit(1);
}

// Generate icons
async function generateIcons() {
  try {
    console.log('Generating PWA icons from upskill-logo.svg...');
    
    // Read SVG
    const svgBuffer = fs.readFileSync(svgPath);
    
    // Generate 192x192 icon
    await sharp(svgBuffer)
      .resize(192, 192)
      .png()
      .toFile(path.join(publicDir, 'icon-192.png'));
    console.log('✓ Generated icon-192.png');
    
    // Generate 512x512 icon
    await sharp(svgBuffer)
      .resize(512, 512)
      .png()
      .toFile(path.join(publicDir, 'icon-512.png'));
    console.log('✓ Generated icon-512.png');
    
    // Also generate favicon.ico (16x16, 32x32, 48x48 in one file)
    // Note: sharp doesn't support multi-size ICO, so we'll generate a 32x32 PNG for favicon
    await sharp(svgBuffer)
      .resize(32, 32)
      .png()
      .toFile(path.join(publicDir, 'favicon-32.png'));
    console.log('✓ Generated favicon-32.png (can be used as favicon)');
    
    console.log('\n✅ All icons generated successfully!');
    console.log('\nNote: For favicon.ico, you may want to use an online converter');
    console.log('to convert favicon-32.png to .ico format, or use the SVG directly.');
    
  } catch (error) {
    console.error('Error generating icons:', error);
    process.exit(1);
  }
}

generateIcons();

