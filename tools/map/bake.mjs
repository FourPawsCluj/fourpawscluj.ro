// Draws the watercolor map (src/map-base.svg + tools/map/map.json) once into images:
// src/static/img/map-<w>.webp for each width in MAP_WIDTHS (tools/build.py), and src/map-base.sha256
// so the build can tell when the images are out of date; plus map-grain.webp, the paper grain tile. The page shows these images, not the SVG:
// the watercolor filters took 270 ms to repaint in Safari each time the map came back on screen.
//
//     node tools/map/bake.mjs
//
// Needs Google Chrome, Playwright (here: the global @playwright/cli), cwebp (Homebrew `webp`)
// and the internet (DM Sans for the "CLUJ-NAPOCA" label). Afterwards run tools/images/previews.py.
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { createRequire } from 'node:module';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const py = args => execFileSync('python3', ['-I', join(ROOT, 'tools', 'build.py'), ...args], { encoding: 'utf8', maxBuffer: 1 << 26 });
const widths = execFileSync('python3', ['-I', '-B', '-c', 'import sys; sys.path.insert(0, sys.argv[1]); import build; print(*build.MAP_WIDTHS)', join(ROOT, 'tools')], { encoding: 'utf8' }).trim().split(' ').map(Number);
const svg = py(['--map-base']);
const GRAIN_PX = 260;  // 100 map units at 2.6 px each: the largest map image is 2280 px for 880 units

let chromium;
try { ({ chromium } = await import('playwright')); } catch {
  const g = execFileSync('npm', ['root', '-g'], { encoding: 'utf8' }).trim();
  ({ chromium } = createRequire(join(g, '@playwright', 'cli', 'package.json'))('playwright-core'));
}

const html = `<!doctype html><html><head>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=block" rel="stylesheet">
<style>html,body{margin:0;background:#FBF3E6}svg{display:block;width:100vw;height:100vh}</style></head><body>${svg}</body></html>`;

const tmp = mkdtempSync(join(tmpdir(), 'bake-'));
const browser = await chromium.launch({ channel: 'chrome' });
try {
  for (const w of widths) {
    const h = Math.round(w * 490 / 880);
    const page = await browser.newPage({ viewport: { width: w, height: h } });
    await page.setContent(html, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const png = join(tmp, `map-${w}.png`);
    await page.screenshot({ path: png });
    const out = join(ROOT, 'src', 'static', 'img', `map-${w}.webp`);
    execFileSync('cwebp', ['-quiet', '-q', '72', '-m', '6', png, '-o', out]);
    console.log(`map-${w}.webp`);
    await page.close();
  }
  // the paper grain: one seamless tile, 100 map units square, laid over the map by CSS (multiply, 50%)
  const page = await browser.newPage({ viewport: { width: GRAIN_PX, height: GRAIN_PX } });
  await page.setContent(`<style>html,body{margin:0;background:transparent}</style>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="${GRAIN_PX}" height="${GRAIN_PX}" style="display:block">
<filter id="g" x="0" y="0" width="1" height="1"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="2" stitchTiles="stitch"/>
<feColorMatrix values="0 0 0 0 .55  0 0 0 0 .45  0 0 0 0 .35  0 0 0 -1.4 1.05"/></filter>
<rect width="100" height="100" filter="url(#g)"/></svg>`);
  const png = join(tmp, 'grain.png');
  await page.screenshot({ path: png, omitBackground: true });
  execFileSync('cwebp', ['-quiet', '-q', '70', '-alpha_q', '70', '-m', '6', png, '-o', join(ROOT, 'src', 'static', 'img', 'map-grain.webp')]);
  console.log('map-grain.webp');
} finally {
  await browser.close();
  rmSync(tmp, { recursive: true, force: true });
}
writeFileSync(join(ROOT, 'src', 'map-base.sha256'), createHash('sha256').update(svg).digest('hex') + '\n');
