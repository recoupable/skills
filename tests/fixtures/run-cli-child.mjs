import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';

const [mode, pidFile] = process.argv.slice(2);
if (mode === 'split-utf8') {
  const bytes = Buffer.from('Beyoncé 東京 🎵\n');
  for (const byte of bytes) {
    process.stdout.write(Buffer.from([byte]));
    process.stderr.write(Buffer.from([byte]));
    await new Promise(resolve => setTimeout(resolve, 10));
  }
} else {
  const grandchild = spawn(process.execPath, ['-e', 'setInterval(() => {}, 1000)', pidFile], {
    stdio: mode === 'exit-ignored' ? 'ignore' : ['ignore', 'inherit', 'inherit'],
  });
  writeFileSync(pidFile, JSON.stringify([process.pid, grandchild.pid]));
  grandchild.unref();
  if (mode === 'timeout-inherited') setInterval(() => {}, 1000);
  else process.exit(0);
}
