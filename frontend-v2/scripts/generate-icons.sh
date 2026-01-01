#!/bin/bash

# Script to generate PWA icons from upskill-logo.svg
# This script uses ImageMagick or inkscape if available

SVG_FILE="public/upskill-logo.svg"
PUBLIC_DIR="public"

if [ ! -f "$SVG_FILE" ]; then
    echo "Error: SVG file not found at $SVG_FILE"
    exit 1
fi

# Check for ImageMagick
if command -v convert &> /dev/null; then
    echo "Using ImageMagick to generate icons..."
    convert -background none -resize 192x192 "$SVG_FILE" "$PUBLIC_DIR/icon-192.png"
    convert -background none -resize 512x512 "$SVG_FILE" "$PUBLIC_DIR/icon-512.png"
    convert -background none -resize 32x32 "$SVG_FILE" "$PUBLIC_DIR/favicon-32.png"
    echo "✓ Icons generated successfully!"
# Check for Inkscape
elif command -v inkscape &> /dev/null; then
    echo "Using Inkscape to generate icons..."
    inkscape -w 192 -h 192 "$SVG_FILE" -o "$PUBLIC_DIR/icon-192.png"
    inkscape -w 512 -h 512 "$SVG_FILE" -o "$PUBLIC_DIR/icon-512.png"
    inkscape -w 32 -h 32 "$SVG_FILE" -o "$PUBLIC_DIR/favicon-32.png"
    echo "✓ Icons generated successfully!"
else
    echo "Error: Neither ImageMagick nor Inkscape found."
    echo "Please install one of them, or use the Node.js script:"
    echo "  npm install --save-dev sharp"
    echo "  node generate-icons.js"
    exit 1
fi

