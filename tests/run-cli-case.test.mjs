import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { setTimeout as delay } from 'node:timers/promises';
import { test } from 'node:test';
import { runCliCase } from '../skills/recoup-internal-dev-verify-cli/scripts/run-cli-case.mjs';

const binary = fileURLToPath(new URL('./fixtures/run-cli-child.mjs', import.meta.url));
const supported = ['darwin', 'linux'].includes(process.platform);

function liveFixture(pid, marker) {
  try {
    const details = execFileSync('ps', ['-p', String(pid), '-o', 'stat=', '-o', 'args='], {
      encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'],
    }).trim();
    return !details.startsWith('Z') && details.includes(marker);
  } catch (error) {
    if (error.status === 1 && !String(error.stderr).trim()) return false;
    throw error;
  }
}

async function bounded(promise) {
  let timer;
  try {
    return await Promise.race([promise, new Promise((_, reject) => {
      timer = setTimeout(() => reject(new Error('CLI case did not finish within 5 seconds')), 5000);
    })]);
  } finally { clearTimeout(timer); }
}

for (const mode of ['exit-inherited', 'exit-ignored', 'timeout-inherited']) {
  test(`cleans descendant processes when ${mode}`, { skip: !supported }, async () => {
    assert.equal(liveFixture(process.pid, ''), true, 'process inspection must work before starting fixtures');
    const workingDir = await mkdtemp(join(tmpdir(), 'recoup-case-processes-'));
    const pidFile = join(workingDir, 'fixture-pids.json');
    let pending;
    try {
      pending = runCliCase({ binary, args: [mode, pidFile], workingDir, port: 1, withKey: false, timeoutMs: 1000 });
      const result = await bounded(pending);
      const pids = JSON.parse(await readFile(pidFile, 'utf8'));
      if (mode === 'timeout-inherited') {
        assert.equal(result.exitCode, null);
        assert.equal(result.signal, 'SIGKILL');
      } else assert.equal(result.exitCode, 0);
      for (let attempt = 0; attempt < 40 && pids.some(pid => liveFixture(pid, pidFile)); attempt++) {
        await delay(25);
      }
      assert.deepEqual(pids.filter(pid => liveFixture(pid, pidFile)), [], 'fixture processes survived cleanup');
    } finally {
      const pids = JSON.parse(await readFile(pidFile, 'utf8').catch(() => '[]'));
      for (const pid of pids) {
        if (liveFixture(pid, pidFile)) {
          try { process.kill(pid, 'SIGKILL'); } catch (error) { if (error.code !== 'ESRCH') throw error; }
        }
      }
      if (pending) await bounded(pending).catch(() => {});
      await rm(workingDir, { recursive: true, force: true });
    }
  });
}

test('decodes split UTF-8 bytes across stdout and stderr chunks', { skip: !supported }, async () => {
  const workingDir = await mkdtemp(join(tmpdir(), 'recoup-case-unicode-'));
  try {
    const result = await bounded(runCliCase({ binary, args: ['split-utf8'], workingDir, port: 1, withKey: false }));
    assert.equal(result.exitCode, 0);
    assert.equal(result.stdout, 'Beyoncé 東京 🎵\n');
    assert.equal(result.stderr, 'Beyoncé 東京 🎵\n');
  } finally { await rm(workingDir, { recursive: true, force: true }); }
});

test('rejects unsupported process-group platforms before spawning', async () => {
  const platform = Object.getOwnPropertyDescriptor(process, 'platform');
  Object.defineProperty(process, 'platform', { value: 'win32' });
  try {
    await assert.rejects(runCliCase({}), /requires macOS or Linux/);
  } finally { Object.defineProperty(process, 'platform', platform); }
});
