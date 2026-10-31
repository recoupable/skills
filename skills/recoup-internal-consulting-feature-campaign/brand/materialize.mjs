#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { cpSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const hash = value => createHash('sha256').update(value).digest('hex');
export function loadBrand() {
  const brand = JSON.parse(readFileSync(join(root, 'brand.json'), 'utf8'));
  for (const [file, asset] of Object.entries(brand.assets)) {
    if (hash(readFileSync(join(root, file))) !== asset.sha256) {
      throw new Error(`Recoup brand asset changed: ${file}. Refresh the reviewed package before rendering.`);
    }
  }
  return brand;
}

export function inlineCSS() {
  loadBrand();
  return readFileSync(join(root, 'brand.css'), 'utf8').replace(/url\('([^']+)'\)/g,
    (_, file) => `url('data:font/woff2;base64,${readFileSync(join(root, file)).toString('base64')}')`);
}

export function materialize(output) {
  const brand = loadBrand();
  const target = resolve(output);
  const lockPath = join(target, 'brand.lock.json');
  const previous = existsSync(lockPath) ? JSON.parse(readFileSync(lockPath, 'utf8')) : {};
  if (previous.brand && previous.brand !== brand.id) {
    throw new Error(`Output already selects ${previous.brand}; use a new output directory for a Recoup rebrand.`);
  }
  mkdirSync(join(target, 'recoup-brand'), { recursive: true });
  for (const file of ['brand.json', 'brand.css', 'finals.json', 'GUIDE.md', 'fonts', 'logos']) {
    cpSync(join(root, file), join(target, 'recoup-brand', file), { recursive: true });
  }
  const lock = { ...previous, brand: brand.id, version: brand.version, sourceCommit: brand.source.commit,
    manifestSha256: hash(readFileSync(join(root, 'brand.json'))), referenceIds: [], expression: 'functional' };
  lock.referenceIds = previous.referenceIds ?? [];
  lock.expression = previous.expression ?? 'functional';
  writeFileSync(lockPath, JSON.stringify(lock, null, 2) + '\n');
  return brand;
}

export function buildRecoupFrame(output) {
  const brand = materialize(output);
  const c = brand.colors;
  const md = `---
name: Recoup Sky
brand: ${brand.id}
brandVersion: ${brand.version}
colors:
  ink: "${c.ink}"
  canvas: "${c.white}"
  accent: "${c.sky}"
  accent-2: "${c.lime}"
  forest: "${c.forest}"
  muted: "${c.muted}"
  pale: "${c.pale}"
  link: "${c.link}"
  border: "${c.border}"
typography:
  display: { fontFamily: "DM Sans", fontWeight: 500, lineHeight: 1.05 }
  body: { fontFamily: "DM Sans", fontWeight: 400, lineHeight: 1.45 }
  label: { fontFamily: "IBM Plex Mono", fontWeight: 400 }
spacing:
  safeMargin: "6%"
components:
  card:
    radius: 16
    borderWidth: 1
---

# Recoup Sky

Read recoup-brand/GUIDE.md and brand.lock.json. For a top-level HTML page load recoup-brand/brand.css. For a nested HyperFrames
sub-composition embed the inline CSS/fonts and exact SVG inside the template; the
player clones template contents. Use the exact SVGs in recoup-brand/logos. This frame adds
canvas-scale composition to the selected identity; it cannot replace that identity.
One clear idea per beat, DM Sans readable at phone scale, mono for short labels only.
Functional white, editorial paper or expressive sky/forest fields; lime carries emphasis.
Use calm fades and small reveals. No compulsory ambient loops or personal footer.
Caption bands use a solid forest plate with white DM Sans and lime emphasis.
Keep new motion experimental until separately approved. Client/artist work may explicitly
select another brand with --brand source and its own frame/tokens.
`;
  writeFileSync(join(output, 'frame.md'), md);
  // Keep the caption engine's reserved hooks while binding identity to the same package.
  let skin = readFileSync(join(root, 'caption-skin.html'), 'utf8');
  skin = skin.replace('<!-- RECOUP_FONT_CSS -->', `<style>${inlineCSS()}</style>`);
  writeFileSync(join(output, 'caption-skin.html'), skin);
  return brand;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  if (process.argv.includes('--inline-css')) process.stdout.write(inlineCSS());
  else {
    if (!process.argv[2]) throw new Error('Usage: materialize.mjs <output-directory> | --inline-css');
    const brand = materialize(process.argv[2]);
    console.log(`Staged ${brand.id}@${brand.version} in ${resolve(process.argv[2])}`);
  }
}
