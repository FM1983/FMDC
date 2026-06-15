#!/usr/bin/env node
/**
 * build-web.js
 *
 * This is a static web app — the game runs straight from `index.html` with no
 * bundler. Capacitor expects its web assets in a single directory (`webDir`,
 * configured as `www/` in capacitor.config.ts).
 *
 * This script (re)creates `www/` and copies the four web entry files into it.
 * It is wired as the `build` npm script and is run in CI before `cap sync`.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(ROOT, 'www');

// The files that make up the shippable web app. Keep this list in sync with the
// repo root entry files.
const FILES = ['index.html', 'sw.js', 'manifest.webmanifest', 'icon.svg'];

function main() {
  // Fresh output dir each build so removed files don't linger in www/.
  fs.rmSync(OUT_DIR, { recursive: true, force: true });
  fs.mkdirSync(OUT_DIR, { recursive: true });

  for (const file of FILES) {
    const src = path.join(ROOT, file);
    const dest = path.join(OUT_DIR, file);

    if (!fs.existsSync(src)) {
      console.error(`[build-web] ERROR: missing source file: ${file}`);
      process.exit(1);
    }

    fs.copyFileSync(src, dest);
    console.log(`[build-web] copied ${file} -> www/${file}`);
  }

  console.log(`[build-web] done. Web assets are in ${OUT_DIR}`);
}

main();
