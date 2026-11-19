// Screenshot a packaging page at an exact pixel size, with a transparent background (unprinted metal stays bare).
// usage: node capture-emballages.mjs <url> <out.png> <cssW> <cssH> <dsf>
import { createRequire } from 'node:module';
import { homedir } from 'node:os';
// Playwright comes from another local project (PLAYWRIGHT_PKG = its package.json, default ~/Desktop/Portfolio/tools)
const require = createRequire(process.env.PLAYWRIGHT_PKG || `${homedir()}/Desktop/Portfolio/tools/package.json`);
const { chromium } = require('playwright');
const [url, out, w, h, dsf] = process.argv.slice(2);
const b = await chromium.launch({ channel: 'chrome', headless: true });
const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: +dsf, colorScheme: 'light' });
await p.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
await p.waitForTimeout(1200);
await p.screenshot({ path: out, clip: { x: 0, y: 0, width: +w, height: +h }, omitBackground: true });
await b.close();
console.log('saved', out);
