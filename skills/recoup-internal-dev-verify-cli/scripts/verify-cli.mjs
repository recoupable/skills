#!/usr/bin/env node
import { createServer } from 'node:http';
import { once } from 'node:events';
import { createHash } from 'node:crypto';
import { mkdtemp, readFile, readdir, rm, mkdir, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import assert from 'node:assert/strict';
import { runCliCase } from './run-cli-case.mjs';
import { verifyCliCases } from './verify-cli-cases.mjs';

if (process.argv.length !== 4) {
  console.error('Usage: node scripts/verify-cli.mjs <CLI source directory> <evidence directory>');
  process.exit(2);
}
const source = resolve(process.argv[2]);
const evidence = resolve(process.argv[3]);
const binary = join(source, 'dist/bin.cjs');
const report = {
  timestamp: new Date().toISOString(),
  source,
  scope: 'Real compiled CLI; loopback HTTP fixtures replace the backend; no production authentication claim.',
  cases: [], requests: [], cleanup: {},
};
let response;
let workingDir;
const server = createServer((req, res) => {
  report.requests.push({ method: req.method, path: req.url, apiKey: req.headers['x-api-key'] });
  res.writeHead(response.status, { 'content-type': 'application/json' });
  res.end(JSON.stringify(response.body));
});

async function check(name, args, predicate, withKey = true) {
  const start = report.requests.length;
  const result = await runCliCase({ binary, args, workingDir, port: server.address().port, withKey });
  const row = { name, ...result, requests: report.requests.slice(start), pass: false };
  report.cases.push(row);
  predicate(row);
  row.pass = true;
}

try {
  const pkg = JSON.parse(await readFile(join(source, 'package.json'), 'utf8'));
  report.version = pkg.version;
  report.binarySha256 = createHash('sha256').update(await readFile(binary)).digest('hex');
  workingDir = await mkdtemp(join(tmpdir(), 'recoup-cli-verify-'));
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  await verifyCliCases({ check, version: pkg.version, respond: next => { response = next; } });
  assert.deepEqual(await readdir(workingDir), []);
} catch (error) {
  report.failure = String(error.stack || error);
  process.exitCode = 1;
} finally {
  const cleanupErrors = [];
  if (server.listening) {
    try { await new Promise((done, reject) => server.close(error => error ? reject(error) : done())); }
    catch (error) { cleanupErrors.push(String(error)); }
  }
  let scratchWorkingDirRemoved = !workingDir;
  try {
    if (workingDir) await rm(workingDir, { recursive: true, force: true });
    scratchWorkingDirRemoved = true;
  } catch (error) { cleanupErrors.push(String(error)); }
  report.cleanup = { serverClosed: !server.listening, scratchWorkingDirRemoved };
  if (cleanupErrors.length) {
    report.cleanupErrors = cleanupErrors;
    process.exitCode = 1;
  }
  report.pass = !report.failure && !cleanupErrors.length && report.cases.length === 7 && report.cases.every(row => row.pass);
  await mkdir(evidence, { recursive: true });
  await writeFile(join(evidence, 'cli-verification.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ pass: report.pass, cases: report.cases.length, httpRequests: report.requests.length, evidence: join(evidence, 'cli-verification.json'), cleanup: report.cleanup }));
}
