# Icon Generation

The app uses `upskill-logo.svg` as the source for all icons and favicons.

## Generating Icons

Icons are automatically generated from the SVG logo. To generate them:

### Option 1: Using Node.js (Recommended)
```bash
npm install
npm run generate-icons
```

This will generate:
- `icon-192.png` - For PWA (192x192)
- `icon-512.png` - For PWA (512x512)
- `favicon-32.png` - For favicon (32x32)

### Option 2: Using ImageMagick
```bash
convert -background none -resize 192x192 public/upskill-logo.svg public/icon-192.png
convert -background none -resize 512x512 public/upskill-logo.svg public/icon-512.png
```

### Option 3: Using Inkscape
```bash
inkscape -w 192 -h 192 public/upskill-logo.svg -o public/icon-192.png
inkscape -w 512 -h 512 public/upskill-logo.svg -o public/icon-512.png
```

## Current Configuration

- **Favicon**: Uses `upskill-logo.svg` directly (configured in `app/layout.tsx`)
- **PWA Icons**: Uses SVG as primary, with PNG fallbacks (192x192 and 512x512)
- **Apple Touch Icon**: Uses `upskill-logo.svg`

All icons reference `public/upskill-logo.svg` as the source.

