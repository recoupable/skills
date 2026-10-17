import assert from 'node:assert/strict';

export async function verifyCliCases({ check, version, respond }) {
  const expectedRequests = [{ method: 'GET', path: '/api/accounts/id', apiKey: 'local-verification-fixture' }];
  const identity = { status: 'success', accountId: 'verification-account' };
  respond({ status: 200, body: identity });
  await check('version matches source package without credentials', ['--version'], row => {
    assert.equal(row.exitCode, 0);
    assert.equal(row.stdout.trim(), version);
    assert.equal(row.requests.length, 0);
  }, false);
  await check('help lists command rows without credentials', ['--help'], row => {
    assert.equal(row.exitCode, 0);
    const commandSection = row.stdout.split(/^Commands:\s*$/m)[1];
    assert.ok(commandSection, 'help must contain a Commands section');
    for (const command of ['whoami', 'artists', 'chats', 'songs', 'emails', 'sandboxes', 'orgs', 'tasks', 'content']) {
      assert.match(commandSection, new RegExp(`^ {2}${command}(?: +\\[[^\\]\\n]+\\])? {2,}\\S`, 'm'));
    }
    assert.equal(row.requests.length, 0);
  }, false);
  await check('identity JSON reaches actual HTTP boundary', ['whoami', '--json'], row => {
    assert.equal(row.exitCode, 0);
    assert.deepEqual(JSON.parse(row.stdout), identity);
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
  respond({ status: 401, body: { status: 'error', message: 'Verification key rejected' } });
  await check('API message error survives to CLI stderr', ['whoami'], row => {
    assert.equal(row.exitCode, 1);
    assert.match(row.stderr, /Verification key rejected/);
    assert.deepEqual(row.requests, expectedRequests);
  });
  respond({ status: 403, body: { status: 'error', error: 'Verification account forbidden' } });
  await check('API error field survives to CLI stderr', ['whoami', '--json'], row => {
    assert.equal(row.exitCode, 1);
    assert.match(row.stderr, /Verification account forbidden/);
    assert.deepEqual(row.requests, expectedRequests);
  });
}
