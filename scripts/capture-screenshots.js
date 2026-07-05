const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const OUT = path.join(__dirname, '../docs/assets/screenshots');
const BASE = process.env.SCREENSHOT_URL || 'http://127.0.0.1:5001';

const shots = [
  { file: 'dashboard.png', tab: 0, waitFor: 'Gaming PC' },
  { file: 'devices.png', tab: 1, waitFor: 'plex.home.lab' },
  { file: 'integration.png', tab: 3, waitFor: 'Global NPM config' },
  { file: 'statistics.png', tab: 5, waitFor: 'Total wakes' },
  { file: 'settings.png', tab: 7, waitFor: 'Change password' },
  { file: 'waiting.png', url: '/waiting?domain=plex.home.lab', waitFor: 'plex.home.lab' },
];

async function clickTab(page, index) {
  await page.evaluate((i) => {
    const tabs = document.querySelectorAll('[role="tab"]');
    if (tabs[i]) tabs[i].click();
  }, index);
}

async function waitForText(page, text, timeout = 15000) {
  await page.waitForFunction(
    (needle) => document.body && document.body.innerText.includes(needle),
    { timeout },
    text
  );
  await new Promise((r) => setTimeout(r, 600));
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1440,900'],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });

  await page.goto(BASE, { waitUntil: 'networkidle0', timeout: 60000 });
  await waitForText(page, 'Welcome back');

  for (const shot of shots) {
    if (shot.url) {
      await page.goto(`${BASE}${shot.url}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    } else {
      await clickTab(page, shot.tab);
    }

    await waitForText(page, shot.waitFor);

    await page.screenshot({
      path: path.join(OUT, shot.file),
      fullPage: false,
    });
    console.log('Saved', shot.file);
  }

  await browser.close();
  console.log('Done.');
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
