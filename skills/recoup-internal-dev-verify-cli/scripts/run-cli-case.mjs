import { spawn } from 'node:child_process';
import { once } from 'node:events';

export async function runCliCase({ binary, args, workingDir, port, withKey }) {
  const env = {
    HOME: workingDir, USERPROFILE: workingDir,
    TMPDIR: workingDir, TEMP: workingDir, TMP: workingDir,
    NO_COLOR: '1', RECOUP_API_URL: `http://127.0.0.1:${port}`,
  };
  for (const key of ['PATH', 'Path', 'SystemRoot', 'WINDIR']) {
    if (process.env[key]) env[key] = process.env[key];
  }
  if (withKey) env.RECOUP_API_KEY = 'local-verification-fixture';
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
