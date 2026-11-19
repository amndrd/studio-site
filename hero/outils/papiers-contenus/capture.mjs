// Screenshot a local page at an exact pixel size (css size x device scale factor).
// usage: node capture.mjs <url> <out.png> <cssW> <cssH> <dsf> [darkScheme=1]
import { createRequire } from 'node:module';
import { homedir } from 'node:os';
// Playwright comes from another local project (PLAYWRIGHT_PKG = its package.json, default ~/Desktop/Portfolio/tools)
const require = createRequire(process.env.PLAYWRIGHT_PKG || `${homedir()}/Desktop/Portfolio/tools/package.json`);
const { chromium } = require('playwright');
const [url, out, w, h, dsf, dark] = process.argv.slice(2);
const b = await chromium.launch({ channel: 'chrome', headless: true });
const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: +dsf, colorScheme: 'light' });
await p.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
try { await p.waitForFunction(() => !document.body || document.body.dataset.ready === '1' || !document.querySelector('[data-wait]'), null, { timeout: 15000 }); } catch (e) {}
await p.waitForTimeout(1500);
await p.screenshot({ path: out, clip: { x: 0, y: 0, width: +w, height: +h } });
await b.close();
console.log('saved', out);
