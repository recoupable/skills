#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { once } from 'node:events';
import { createHash } from 'node:crypto';
import { mkdtemp, readFile, readdir, rm, mkdir, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import assert from 'node:assert/strict';

if (process.argv.length !== 4) {
  console.error('Usage: node scripts/verify-cli.mjs <CLI source directory> <evidence directory>');
  process.exit(2);
}
const source = resolve(process.argv[2]);
const evidence = resolve(process.argv[3]);
const binary = join(source, 'dist/bin.cjs');
const expectedRequests = [{ method: 'GET', path: '/api/accounts/id', apiKey: 'local-verification-fixture' }];
const pkg = JSON.parse(await readFile(join(source, 'package.json'), 'utf8'));
const report = {
  timestamp: new Date().toISOString(),
  source, version: pkg.version,
  binarySha256: createHash('sha256').update(await readFile(binary)).digest('hex'),
  scope: 'Real compiled CLI; loopback HTTP fixtures replace the backend; no production authentication claim.',
  cases: [], requests: [], cleanup: {},
};
let response = { status: 200, body: { status: 'success', accountId: 'verification-account' } };
const server = createServer((req, res) => {
  report.requests.push({ method: req.method, path: req.url, apiKey: req.headers['x-api-key'] });
  res.writeHead(response.status, { 'content-type': 'application/json' });
  res.end(JSON.stringify(response.body));
});
const workingDir = await mkdtemp(join(tmpdir(), 'recoup-cli-verify-'));

async function run(args, withKey = true) {
  const env = { ...process.env, RECOUP_API_URL: `http://127.0.0.1:${server.address().port}` };
  if (withKey) env.RECOUP_API_KEY = 'local-verification-fixture';
  else delete env.RECOUP_API_KEY;
  const child = spawn(process.execPath, [binary, ...args], { cwd: workingDir, env });
  let stdout = '', stderr = '';
  child.stdout.on('data', chunk => { stdout += chunk; });
  child.stderr.on('data', chunk => { stderr += chunk; });
  const timeout = setTimeout(() => child.kill('SIGKILL'), 10000);
  try {
    const [exitCode, signal] = await once(child, 'close');
    return { args, exitCode, signal, stdout, stderr };
  } finally { clearTimeout(timeout); }
}

async function check(name, args, predicate, withKey = true) {
  const start = report.requests.length;
  const result = await run(args, withKey);
  const row = { name, ...result, requests: report.requests.slice(start), pass: false };
  report.cases.push(row);
  predicate(row);
  row.pass = true;
}

try {
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  await check('version matches source package', ['--version'], row => {
    assert.equal(row.exitCode, 0);
    assert.equal(row.stdout.trim(), pkg.version);
    assert.equal(row.requests.length, 0);
  });
  await check('help exposes documented command groups', ['--help'], row => {
    assert.equal(row.exitCode, 0);
    for (const command of ['whoami', 'artists', 'chats', 'songs', 'emails', 'sandboxes', 'orgs', 'tasks', 'content']) {
      assert.match(row.stdout, new RegExp(`\\b${command}\\b`));
    }
    assert.equal(row.requests.length, 0);
  });
  await check('identity JSON reaches actual HTTP boundary', ['whoami', '--json'], row => {
    assert.equal(row.exitCode, 0);
    assert.deepEqual(JSON.parse(row.stdout), response.body);
    assert.deepEqual(row.requests, expectedRequests);
  });
  await check('identity plain text prints account ID', ['whoami'], row => {
    assert.equal(row.exitCode, 0);
    assert.equal(row.stdout.trim(), 'verification-account');
    assert.deepEqual(row.requests, expectedRequests);
  });
  await check('missing API key makes no HTTP request', ['whoami'], row => {
    assert.equal(row.exitCode, 1);
    assert.match(row.stderr, /RECOUP_API_KEY environment variable is not set/);
    assert.equal(row.requests.length, 0);
  }, false);
  response = { status: 401, body: { status: 'error', message: 'Verification key rejected' } };
  await check('API message error survives to CLI stderr', ['whoami'], row => {
    assert.equal(row.exitCode, 1);
    assert.match(row.stderr, /Verification key rejected/);
    assert.deepEqual(row.requests, expectedRequests);
  });
  response = { status: 403, body: { status: 'error', error: 'Verification account forbidden' } };
  await check('API error field survives to CLI stderr', ['whoami', '--json'], row => {
    assert.equal(row.exitCode, 1);
    assert.match(row.stderr, /Verification account forbidden/);
    assert.deepEqual(row.requests, expectedRequests);
  });
  assert.ok(report.requests.every(req => req.method === 'GET'));
  assert.deepEqual(await readdir(workingDir), []);
} catch (error) {
  report.failure = String(error.stack || error);
  process.exitCode = 1;
} finally {
  if (server.listening) await new Promise((done, reject) => server.close(error => error ? reject(error) : done()));
  await rm(workingDir, { recursive: true, force: true });
  report.cleanup = { serverClosed: !server.listening, scratchWorkingDirRemoved: true };
  report.pass = !report.failure && report.cases.length === 7 && report.cases.every(row => row.pass);
  await mkdir(evidence, { recursive: true });
  await writeFile(join(evidence, 'cli-verification.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ pass: report.pass, cases: report.cases.length, httpRequests: report.requests.length, evidence: join(evidence, 'cli-verification.json'), cleanup: report.cleanup }));
}
