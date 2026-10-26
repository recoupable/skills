export function fixtureCli(mode = '') {
  return `
const mode = ${JSON.stringify(mode)};
const args = process.argv.slice(2);
if (args.includes('--version') || args.includes('--help')) {
  if (mode === 'requires-key-for-discovery' && !process.env.RECOUP_API_KEY) process.exit(1);
  if (args.includes('--version')) console.log('1.2.3');
  else {
    const commands = ['whoami', 'artists', 'chats', 'songs', 'emails', 'sandboxes', 'orgs', 'tasks', 'content'];
    console.log('Usage: recoup [command]\\nManage tasks with Recoup\\n\\nCommands:');
    for (const command of commands) {
      if (mode !== 'missing-command-row' || command !== 'tasks') console.log('  ' + command + '  Description');
    }
  }
  process.exit(0);
}
if (!process.env.RECOUP_API_KEY) {
  console.error('RECOUP_API_KEY environment variable is not set');
  process.exit(1);
}
const base = process.env.RECOUP_API || process.env.RECOUP_API_URL;
const path = mode === 'wrong-endpoint' ? '/api/wrong-endpoint' : '/api/accounts/id';
fetch(base + path, { headers: { 'x-api-key': process.env.RECOUP_API_KEY } }).then(async response => {
  const body = await response.json();
  if (!response.ok) {
    console.error(body.message || body.error);
    process.exitCode = 1;
  } else console.log(args.includes('--json') ? JSON.stringify(body) : body.accountId);
}).catch(error => { console.error(error.message); process.exitCode = 1; });
`;
}
