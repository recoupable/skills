import { spawn } from 'node:child_process';
import { once } from 'node:events';

export async function runCliCase({ binary, args, workingDir, port, withKey, timeoutMs = 10000 }) {
  if (!['darwin', 'linux'].includes(process.platform)) {
    throw new Error('CLI verification requires macOS or Linux process groups');
  }
  const env = {
    HOME: workingDir, USERPROFILE: workingDir,
    TMPDIR: workingDir, TEMP: workingDir, TMP: workingDir,
    NO_COLOR: '1', RECOUP_API_URL: `http://127.0.0.1:${port}`,
  };
  for (const key of ['PATH', 'Path', 'SystemRoot', 'WINDIR']) {
    if (process.env[key]) env[key] = process.env[key];
  }
  if (withKey) env.RECOUP_API_KEY = 'local-verification-fixture';
  const child = spawn(process.execPath, [binary, ...args], { cwd: workingDir, env, detached: true });
  let stdout = '', stderr = '';
  child.stdout.setEncoding('utf8');
  child.stderr.setEncoding('utf8');
  child.stdout.on('data', chunk => { stdout += chunk; });
  child.stderr.on('data', chunk => { stderr += chunk; });
  let cleanupTimeout, rejectCleanup;
  const cleanupFailure = new Promise((_, reject) => { rejectCleanup = reject; });
  const failCleanup = error => {
    child.stdout.destroy();
    child.stderr.destroy();
    child.unref();
    rejectCleanup(error);
  };
  const stopGroup = () => {
    if (cleanupTimeout) return;
    try { if (child.pid) process.kill(-child.pid, 'SIGKILL'); }
    catch (error) {
      if (error.code !== 'ESRCH') {
        failCleanup(new Error(`Could not stop CLI process group ${child.pid}: ${error.message}`));
        return;
      }
    }
    cleanupTimeout = setTimeout(() => {
      failCleanup(new Error('CLI process group did not close within one second of cleanup'));
    }, 1000);
  };
  child.once('exit', stopGroup);
  const timeout = setTimeout(stopGroup, timeoutMs);
  try {
    const [exitCode, signal] = await Promise.race([once(child, 'close'), cleanupFailure]);
    return { args, exitCode, signal, stdout, stderr };
  } finally {
    clearTimeout(timeout);
    clearTimeout(cleanupTimeout);
    child.removeListener('exit', stopGroup);
  }
}
