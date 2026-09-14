// Resolve only the selected runtime/project or this installed skill's dependencies.
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');

function roots() {
  return [...new Set([
    process.env.HYPERFRAMES_SKILL_RUNTIME_DIR,
    process.env.HYPERFRAMES_ROOT, // explicit legacy checkout, never auto-discovered
    process.cwd(),
    path.resolve(__dirname, '../..'),
  ].filter(Boolean).map(p => path.resolve(p)))];
}
function packageDir(name) {
  for (const root of roots()) {
    const dir = path.join(root, 'node_modules', name);
    if (fs.existsSync(path.join(dir, 'package.json'))) return dir;
  }
  throw new Error(`Missing ${name}. Prepare the video runtime and set HYPERFRAMES_SKILL_RUNTIME_DIR; see engine/runtime/SETUP.md.`);
}
function exportEntry(value, condition) {
  if (typeof value === 'string') return value;
  if (!value || typeof value !== 'object') return null;
  for (const key of [condition, 'node', 'default']) {
    const entry = exportEntry(value[key], condition);
    if (entry) return entry;
  }
  return null;
}
function resolvePackage(name, condition = 'import') {
  const parts = name.split('/');
  const baseName = name.startsWith('@') ? parts.slice(0, 2).join('/') : parts[0];
  const dir = packageDir(baseName);
  const subpath = name.slice(baseName.length).replace(/^\//, '');
  if (subpath) {
    const file = path.resolve(dir, subpath);
    if (!file.startsWith(dir + path.sep) || !fs.existsSync(file)) throw new Error(`Missing package resource: ${name}`);
    return file;
  }
  const manifest = JSON.parse(fs.readFileSync(path.join(dir, 'package.json'), 'utf8'));
  const entry = manifest.exports?.['.'] ?? manifest.exports;
  const relative = exportEntry(entry, condition) ?? manifest.main ?? 'index.js';
  if (typeof relative !== 'string') throw new Error(`Unsupported package entry for ${name}`);
  const file = path.resolve(dir, relative);
  if (!file.startsWith(dir + path.sep) || !fs.existsSync(file)) throw new Error(`Package entry missing: ${name}`);
  return file;
}
function loadPackage(name) {
  return createRequire(__filename)(resolvePackage(name, 'require'));
}
function cliPath() {
  if (process.env.HYPERFRAMES_CLI) {
    const file = path.resolve(process.env.HYPERFRAMES_CLI);
    if (!fs.existsSync(file)) throw new Error('HYPERFRAMES_CLI does not exist');
    return file;
  }
  if (process.env.HYPERFRAMES_ROOT) {
    const file = path.resolve(process.env.HYPERFRAMES_ROOT, 'packages/cli/dist/cli.js');
    if (fs.existsSync(file)) return file;
  }
  const dir = packageDir('hyperframes');
  const manifest = JSON.parse(fs.readFileSync(path.join(dir, 'package.json'), 'utf8'));
  const bin = typeof manifest.bin === 'string' ? manifest.bin : manifest.bin?.hyperframes;
  if (!bin || !fs.existsSync(path.join(dir, bin))) throw new Error('Installed hyperframes CLI has no valid binary');
  return path.join(dir, bin);
}
module.exports = { roots, packageDir, resolvePackage, loadPackage, cliPath };
if (require.main === module) {
  try { process.stdout.write(cliPath() + '\n'); }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
