import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import runtime from '../skills/recoup-internal-consulting-hyperframes-video/engine/runtime/dependencies.cjs';
import { hyperframesPackageSpec } from '../skills/recoup-internal-consulting-hyperframes-video/engine/runtime/package-loader.mjs';
import { loadEnvFromDir } from '../skills/recoup-internal-consulting-hyperframes-video/engine/hyperframes-media/scripts/lib/heygen.mjs';

const scratch = mkdtempSync(join(tmpdir(), 'consulting-runtime-test-'));
const original = { ...process.env };
const cwd = process.cwd();
function fakePackage(name, entry = 'index.cjs', text = 'module.exports = {example:true};') {
  const dir = join(scratch, 'runtime', 'node_modules', name);
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, 'package.json'), JSON.stringify({name, main:entry}));
  writeFileSync(join(dir, entry), text);
  return dir;
}
test('runtime and credential boundaries', async t => {
  try {
    const project = join(scratch, 'project'); mkdirSync(project);
    process.chdir(project);
    delete process.env.HYPERFRAMES_ROOT; delete process.env.HYPERFRAMES_CLI;
    process.env.HYPERFRAMES_SKILL_RUNTIME_DIR = join(scratch, 'runtime');
    await t.test('loads explicit runtime and resolves declared CLI binary', () => {
      fakePackage('fixture-module'); assert.equal(runtime.loadPackage('fixture-module').example, true);
      const cliDir = fakePackage('hyperframes', 'cli.cjs', 'console.log("synthetic-cli");');
      writeFileSync(join(cliDir,'package.json'), JSON.stringify({name:'hyperframes', bin:{hyperframes:'cli.cjs'}}));
      const result = spawnSync(process.execPath, [runtime.cliPath()], {encoding:'utf8'});
      assert.equal(result.status, 0); assert.equal(result.stdout.trim(), 'synthetic-cli');
    });
    await t.test('does not discover packages in a parent project', () => {
      const dir = join(scratch, 'node_modules', 'parent-only'); mkdirSync(dir, {recursive:true});
      writeFileSync(join(dir,'package.json'), '{"name":"parent-only","main":"index.js"}');
      writeFileSync(join(dir,'index.js'), 'throw Error("should not load")');
      assert.throws(() => runtime.loadPackage('parent-only'), /Missing parent-only/);
    });
    await t.test('loads nested conditional package exports', () => {
      const dir = fakePackage('conditional-fixture');
      writeFileSync(join(dir,'package.json'), JSON.stringify({name:'conditional-fixture',exports:{'.':{
        require:{types:'./types.d.ts',default:'./index.cjs'},
        import:{types:'./types.d.mts',default:'./module.mjs'}
      }}}));
      writeFileSync(join(dir,'module.mjs'), 'export const example = true;');
      assert.equal(runtime.loadPackage('conditional-fixture').example, true);
      assert.equal(runtime.resolvePackage('conditional-fixture'), join(dir,'module.mjs'));
    });
    await t.test('package spec comes from bundled manifest outside upstream checkout', () => {
      assert.match(hyperframesPackageSpec('@hyperframes/producer'), /^@hyperframes\/producer@\d+\.\d+\.\d+$/);
      assert.throws(() => hyperframesPackageSpec('unknown'), /No pinned dependency/);
    });
    await t.test('environment loader stays in selected project and admits only provider keys', () => {
      for (const k of ['HYPERFRAMES_WORKSPACE_DIR','HEYGEN_API_KEY','HYPERFRAMES_API_KEY','ELEVENLABS_API_KEY','OTHER_TEST_SECRET']) delete process.env[k];
      writeFileSync(join(scratch,'.env'), 'HEYGEN_API_KEY=parent-must-not-load\n');
      loadEnvFromDir(project); assert.equal(process.env.HEYGEN_API_KEY, undefined);
      writeFileSync(join(project,'.env.local'), 'HEYGEN_API_KEY=fixture-local\nOTHER_TEST_SECRET=ignored\n');
      writeFileSync(join(project,'.env'), 'HEYGEN_API_KEY=fixture-lower-priority\n');
      loadEnvFromDir(project); assert.equal(process.env.HEYGEN_API_KEY, 'fixture-local');
      assert.equal(process.env.OTHER_TEST_SECRET, undefined);
      process.env.HEYGEN_API_KEY='fixture-shell'; loadEnvFromDir(project);
      assert.equal(process.env.HEYGEN_API_KEY,'fixture-shell');
    });
  } finally {
    process.chdir(cwd);
    for (const key of Object.keys(process.env)) if (!(key in original)) delete process.env[key];
    Object.assign(process.env, original); rmSync(scratch,{recursive:true,force:true});
  }
});
