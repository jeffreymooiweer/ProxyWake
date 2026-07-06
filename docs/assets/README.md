# Documentation assets

## Icon

`icon.png` is the canonical ProxyWake app icon (favicon, UI logo, PWA manifest).

Regenerate all frontend icon sizes after updating the source file:

```bash
python3 scripts/generate_app_icons.py
```

This updates `frontend/public/` (`favicon.ico`, `icon.png`, `icon-16.png` … `icon-512.png`, `apple-touch-icon.png`, `proxywake.png`).

## Banner

`banner.svg` is the repository banner used in the README.

## Screenshots

README screenshots live in `screenshots/`:

- `dashboard.png`
- `devices.png`
- `integration.png`
- `statistics.png`
- `settings.png`
- `waiting.png`

### Regenerating screenshots

1. Seed demo data:

   ```bash
   export PROXYWAKE_DATA_DIR=/tmp/proxywake-screenshots
   python3 scripts/seed_screenshots.py
   ```

2. Build frontend and start the backend:

   ```bash
   cd frontend && npm ci && npm run build
   cd ../backend && PROXYWAKE_DATA_DIR=/tmp/proxywake-screenshots python app.py
   ```

3. Capture (requires Node.js and Puppeteer):

   ```bash
   cd scripts && npm ci
   SCREENSHOT_URL=http://127.0.0.1:5001 node capture-screenshots.js
   ```

4. Commit the updated PNG files.

Screenshots are optional for development but recommended before releases for README polish.
