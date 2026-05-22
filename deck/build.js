// Build: render index.html -> presentation PDF + per-page PNG previews
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const DECK = __dirname;
const SRC = 'file://' + path.join(DECK, 'index.html');
const OUT_PDF = path.join(DECK, 'Citadel-Capital-Executive-Aviation-Platform.pdf');
const PREVIEW = path.join(DECK, 'preview');

(async () => {
  if (!fs.existsSync(PREVIEW)) fs.mkdirSync(PREVIEW);

  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--font-render-hinting=none'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720, deviceScaleFactor: 1.5 });
  await page.goto(SRC, { waitUntil: 'networkidle0' });
  await page.evaluateHandle('document.fonts.ready');

  // PDF
  await page.pdf({
    path: OUT_PDF,
    width: '1280px',
    height: '720px',
    printBackground: true,
    preferCSSPageSize: true,
  });
  console.log('PDF  ->', path.relative(process.cwd(), OUT_PDF));

  // per-page previews
  const pages = await page.$$('.page');
  for (let i = 0; i < pages.length; i++) {
    const n = String(i + 1).padStart(2, '0');
    await pages[i].screenshot({ path: path.join(PREVIEW, `page-${n}.png`) });
  }
  console.log('PNG  ->', pages.length, 'pages in deck/preview/');

  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
