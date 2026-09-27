// Renders promo.html frame-by-frame into an MP4.
// Usage: node render.mjs [--fps 30] [--out yuyouji-promo.mp4] [--still 12.5,15]
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const dir = path.dirname(fileURLToPath(import.meta.url));
const arg = (name, def) => { const i = process.argv.indexOf(`--${name}`); return i > 0 ? process.argv[i + 1] : def; };
const fps = Number(arg('fps', 30));
const out = path.resolve(dir, arg('out', 'yuyouji-promo.mp4'));
const audio = arg('audio', path.join(dir, 'music.wav'));
const still = arg('still', null);
const ffmpeg = process.env.FFMPEG || 'ffmpeg';

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(path.join(dir, 'promo.html')).href + '?capture');
await page.evaluate(async () => {
  // make sure every glyph subset we use is loaded before capturing
  await document.fonts.ready;
  const text = document.body.innerText + (window.STORY || '');
  await Promise.all(['400 40px "Noto Sans TC"', '700 40px "Noto Sans TC"', '900 40px "Noto Sans TC"',
    '700 40px "Noto Serif TC"', '900 40px "Noto Serif TC"'].map((f) => document.fonts.load(f, text)));
});
const duration = await page.evaluate(() => window.DURATION);

if (still) {
  for (const t of still.split(',').map(Number)) {
    await page.evaluate((t) => window.render(t), t);
    const file = path.join(dir, `still-${t}.png`);
    await page.screenshot({ path: file });
    console.log('wrote', file);
  }
  await browser.close();
  process.exit(0);
}

const args = ['-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-'];
if (audio) args.push('-i', audio);
args.push('-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart');
if (audio) args.push('-c:a', 'aac', '-b:a', '192k', '-shortest');
args.push(out);
const ff = spawn(ffmpeg, args, { stdio: ['pipe', 'inherit', 'inherit'] });

const frames = Math.round(duration * fps);
for (let f = 0; f < frames; f++) {
  await page.evaluate((t) => window.render(t), f / fps);
  const buf = await page.screenshot({ type: 'png' });
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  if (f % fps === 0) process.stderr.write(`\rframe ${f}/${frames}`);
}
ff.stdin.end();
await new Promise((r) => ff.on('close', r));
await browser.close();
console.log('\nwrote', out);
