import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { fixtureCli } from './fixtures/verification-cli.mjs';

const helper = fileURLToPath(new URL('../skills/recoup-internal-dev-verify-cli/scripts/verify-cli.mjs', import.meta.url));

async function verify(t, { mode, missing, env = {} } = {}) {
  const root = await mkdtemp(join(tmpdir(), 'verify-cli-regression-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  const source = join(root, 'source');
  const evidence = join(root, 'evidence');
  await mkdir(join(source, 'dist'), { recursive: true });
  if (missing !== 'package') await writeFile(join(source, 'package.json'), '{"version":"1.2.3"}');
  if (missing !== 'binary') await writeFile(join(source, 'dist/bin.cjs'), fixtureCli(mode));
  const child = spawn(process.execPath, [helper, source, evidence], {
    env: { ...process.env, ...env }, stdio: ['ignore', 'pipe', 'pipe'],
  });
  let stderr = '';
  child.stderr.on('data', chunk => { stderr += chunk; });
  child.stdout.resume();
  const timeout = setTimeout(() => child.kill('SIGKILL'), 15000);
  const [exitCode] = await once(child, 'close').finally(() => clearTimeout(timeout));
  const report = JSON.parse(await readFile(join(evidence, 'cli-verification.json'), 'utf8'));
  assert.deepEqual(report.cleanup, { serverClosed: true, scratchWorkingDirRemoved: true }, stderr);
  return { exitCode, report };
}

test('isolates ambient endpoint and credentials from every child', async t => {
  const { exitCode, report } = await verify(t, { env: {
    RECOUP_API: 'http://127.0.0.1:1/do-not-contact',
    RECOUP_API_KEY: 'ambient-key-must-not-be-inherited',
  } });
  assert.equal(exitCode, 0);
  assert.equal(report.pass, true);
  assert.equal(report.cases.length, 7);
  assert.equal(report.requests.length, 4);
});

for (const missing of ['package', 'binary']) {
  test(`records missing ${missing} as failed verification`, async t => {
    const { exitCode, report } = await verify(t, { missing });
    assert.equal(exitCode, 1);
    assert.equal(report.pass, false);
    assert.match(report.failure, /ENOENT/);
  });
}

for (const mode of ['requires-key-for-discovery', 'missing-command-row', 'wrong-endpoint']) {
  test(`rejects the ${mode} mutant`, async t => {
    const { exitCode, report } = await verify(t, { mode });
    assert.equal(exitCode, 1);
    assert.equal(report.pass, false);
    assert.ok(report.cases.some(row => row.pass === false));
  });
}
