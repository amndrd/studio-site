// Full-page PNG export of a local HTML page (to drop into Figma when the MCP quota is used up).
// usage: node export.mjs <page.html> <out.png> [scale]
import { createRequire } from 'node:module';
import { homedir } from 'node:os';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
// Playwright comes from another local project (PLAYWRIGHT_PKG = its package.json, default ~/Desktop/Portfolio/tools)
const require = createRequire(process.env.PLAYWRIGHT_PKG || `${homedir()}/Desktop/Portfolio/tools/package.json`);
const { chromium } = require('playwright');
const [page, out, scale] = process.argv.slice(2);
const b = await chromium.launch({ channel: 'chrome', headless: true });
const p = await b.newPage({ viewport: { width: 2400, height: 1400 }, deviceScaleFactor: Number(scale || 1) });
await p.route('**mcp.figma.com/**', r => r.abort());               // no capture script in the export
await p.goto(pathToFileURL(path.resolve(page)).href, { waitUntil: 'networkidle' });
await p.waitForTimeout(1200);
await p.screenshot({ path: out, fullPage: true });
console.log('saved', out);
await b.close();
