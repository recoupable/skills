import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, writeFileSync, mkdirSync, rmSync, cpSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { execFileSync, spawnSync } from 'node:child_process';
import { parseFonts } from '../skills/recoup-internal-consulting-hyperframes-video/modes/faceless-explainer/scripts/lib/tokens.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const video = join(root, 'skills/recoup-internal-consulting-hyperframes-video');
const source = join(root, 'skills/recoup-internal-consulting-tasteful-design/brand');
const scratch = () => mkdtempSync(join(tmpdir(), 'recoup-brand-test-'));

for (const mode of ['pr-to-video', 'faceless-explainer', 'product-launch-video']) {
  test(`${mode}: default identity survives conflicting capture tokens and stages portable assets`, () => {
    const out = scratch();
    try {
      mkdirSync(join(out, 'capture/extracted'), { recursive: true });
      writeFileSync(join(out, 'capture/extracted/tokens.json'), JSON.stringify({
        colors: ['#FF0000'], fonts: ['Unrelated Serif', 'IBM Plex Mono']
      }));
      const builder = join(video, 'modes', mode, 'scripts/build-frame.mjs');
      execFileSync(process.execPath, [builder, '--hyperframes', out], { cwd: tmpdir() });
      const frame = readFileSync(join(out, 'frame.md'), 'utf8');
      assert.match(frame, /body: \{ fontFamily: "DM Sans", fontWeight: 400/);
      assert.match(frame, /label: \{ fontFamily: "IBM Plex Mono"/);
      assert.match(frame, /accent: "#007EBD"/);
      assert.deepEqual(parseFonts(frame), {display: '"DM Sans"', body: '"DM Sans"'});
      assert.doesNotMatch(frame, /Unrelated Serif|#FF0000/);
      const skin = readFileSync(join(out, 'caption-skin.html'), 'utf8');
      assert.match(skin, /data:font\/woff2;base64,/);
      assert.match(skin, /background:var\(--recoup-forest\)/);
      assert.doesNotMatch(skin, /EB Garamond|fonts\.googleapis/);
      assert.ok(readFileSync(join(out, 'recoup-brand/logos/lockup-white.svg')).length > 100);
      assert.equal(JSON.parse(readFileSync(join(out, 'brand.lock.json'))).brand, 'recoup-sky');
      // Exercise the actual downstream consumer, including its reserved skin hooks.
      writeFileSync(join(out, 'STORYBOARD.md'), '---\nformat: 16:9\n---\n## Frame 1 — Example\n- duration: 3\n');
      writeFileSync(join(out, 'audio_meta.json'), JSON.stringify({ voices: [{ frame: 1, words: [
        { text: 'A', start: .2, end: .4 }, { text: 'clear', start: .4, end: .7 },
        { text: 'step.', start: .7, end: 1.1 }
      ] }] }));
      execFileSync(process.execPath, [join(video, 'modes', mode, 'scripts/captions.mjs'),
        'build', '--hyperframes', out], { cwd: tmpdir() });
      const compiled = readFileSync(join(out, 'compositions/captions.html'), 'utf8');
      assert.match(compiled, /data:font\/woff2;base64,/);
      assert.match(compiled, /font-family:'DM Sans'/);
      assert.match(compiled, /"text":"clear"/);
      assert.doesNotMatch(compiled, /var GROUPS = \[\];|EB Garamond/);
      assert.notEqual(spawnSync(process.execPath, [builder, '--preset', 'claude', '--hyperframes', out]).status, 0);
    } finally { rmSync(out, { recursive: true, force: true }); }
  });
}

test('explicit source brand retains custom colors and named display/body roles', () => {
  const out = scratch();
  try {
    mkdirSync(join(out, 'capture/extracted'), { recursive: true });
    writeFileSync(join(out, 'capture/extracted/tokens.json'), JSON.stringify({
      colors: ['#112233', '#FDFDFD', '#AA3311'],
      fonts: ['Source Sans', 'Source Mono'],
      typography: { display: { family: 'Source Sans' }, body: { family: 'Source Sans' } }
    }));
    execFileSync(process.execPath, [join(video, 'modes/pr-to-video/scripts/build-frame.mjs'),
      '--brand', 'source', '--preset', 'claude', '--hyperframes', out], { cwd: tmpdir() });
    const frame = readFileSync(join(out, 'frame.md'), 'utf8');
    assert.match(frame, /#AA3311/);
    assert.match(frame, /fontFamily: "Source Sans"/);
    assert.doesNotMatch(frame, /fontFamily: "Source Mono"|brand: recoup-sky/);
  } finally { rmSync(out, { recursive: true, force: true }); }
});

test('a media skill brand package runs standalone, embeds fonts, and fails on changed font bytes', async () => {
  const out = scratch();
  try {
    const isolated = join(out, 'isolated');
    cpSync(join(video, 'brand'), isolated, { recursive: true });
    const mod = await import(pathToFileURL(join(isolated, 'materialize.mjs')));
    assert.match(mod.inlineCSS(), /data:font\/woff2;base64,/);
    mod.materialize(join(out, 'result'));
    const lockPath = join(out, 'result/brand.lock.json');
    const lock = JSON.parse(readFileSync(lockPath));
    writeFileSync(lockPath, JSON.stringify({ ...lock, expression: 'editorial', referenceIds: ['carousel-paper-trail'] }));
    mod.materialize(join(out, 'result'));
    assert.deepEqual(JSON.parse(readFileSync(lockPath)).referenceIds, ['carousel-paper-trail']);
    assert.equal(JSON.parse(readFileSync(lockPath)).expression, 'editorial');
    writeFileSync(lockPath, JSON.stringify({ brand: 'client-brand' }));
    assert.throws(() => mod.materialize(join(out, 'result')), /already selects client-brand/);
    writeFileSync(join(isolated, 'fonts/dm-sans.woff2'), 'damaged');
    assert.throws(() => mod.inlineCSS(), /asset changed/);
  } finally { rmSync(out, { recursive: true, force: true }); }
});

test('caption theme compiler defaults to Recoup, keeps all words and embeds the actual font', () => {
  const out = scratch();
  try {
    writeFileSync(join(out, 'theme.json'), JSON.stringify({ width: 1280, height: 720, duration: 3,
      lines: [['One', 'clear', 'next', 'step.']] }));
    writeFileSync(join(out, 'transcript.json'), JSON.stringify({ words:
      ['One', 'clear', 'next', 'step.'].map((text, i) => ({ text, start: i * .4 + .2, end: i * .4 + .5 })) }));
    execFileSync(process.execPath, [join(video, 'modes/embedded-captions/scripts/make-theme.cjs'), out]);
    const rail = readFileSync(join(out, 'rail.html'), 'utf8');
    assert.match(rail, /font-family:'DM Sans'/);
    assert.match(rail, /background:#132B26/);
    assert.match(rail, /data:font\/woff2;base64,/);
    for (const word of ['One', 'clear', 'next', 'step.']) assert.ok(rail.includes(word));
  } finally { rmSync(out, { recursive: true, force: true }); }
});

test('all six self-contained copies match the canonical reviewed package', () => {
  execFileSync('python3', [join(root, 'scripts/check_vendored.py')]);
  const finals = JSON.parse(readFileSync(join(source, 'finals.json')));
  assert.equal(finals.assets.length, 52);
  assert.ok(finals.assets.every(x => x.stage === 'final' && x.assets.every(a => a.sha256.length === 64)));
});
