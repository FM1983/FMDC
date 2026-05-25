// Build: render index.html -> presentation PDF + per-page PNG previews.
// Optional photography: drop cover.jpg / profile.jpg / livery.jpg into
// assets/photos/ and they are auto-detected and embedded; otherwise the
// pages fall back to the vector aircraft illustration.
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const DECK = __dirname;
const SRC = 'file://' + path.join(DECK, 'index.html');
const OUT_PDF = path.join(DECK, 'Citadel-Capital-Executive-Aviation-Platform.pdf');
const PREVIEW = path.join(DECK, 'preview');
const PHOTO_DIR = path.join(DECK, 'assets', 'photos');

function loadPhotos() {
  const slots = ['cover', 'profile', 'livery'];
  const exts = ['jpg', 'jpeg', 'png', 'webp'];
  const out = {};
  if (!fs.existsSync(PHOTO_DIR)) return out;
  for (const slot of slots) {
    for (const ext of exts) {
      const fp = path.join(PHOTO_DIR, slot + '.' + ext);
      if (fs.existsSync(fp)) {
        const mime = ext === 'jpg' ? 'jpeg' : ext;
        out[slot] = `data:image/${mime};base64,` + fs.readFileSync(fp).toString('base64');
        break;
      }
    }
  }
  return out;
}

(async () => {
  if (!fs.existsSync(PREVIEW)) fs.mkdirSync(PREVIEW);
  const photos = loadPhotos();
  const found = Object.keys(photos);
  console.log('Photos:', found.length ? found.join(', ') : 'none — using vector illustration');

  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--font-render-hinting=none'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720, deviceScaleFactor: 1.5 });
  await page.goto(SRC, { waitUntil: 'networkidle0' });

  // wire up any detected photography
  await page.evaluate((photos) => {
    for (const [slot, uri] of Object.entries(photos)) {
      document.body.classList.add('has-photo-' + slot);
      document.body.style.setProperty('--photo-' + slot, `url("${uri}")`);
    }
  }, photos);

  await page.evaluateHandle('document.fonts.ready');

  await page.pdf({
    path: OUT_PDF,
    width: '1280px',
    height: '720px',
    printBackground: true,
    preferCSSPageSize: true,
  });
  console.log('PDF  ->', path.relative(process.cwd(), OUT_PDF));

  const pages = await page.$$('.page');
  for (let i = 0; i < pages.length; i++) {
    const n = String(i + 1).padStart(2, '0');
    await pages[i].screenshot({ path: path.join(PREVIEW, `page-${n}.png`) });
  }
  console.log('PNG  ->', pages.length, 'pages in deck/preview/');

  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
