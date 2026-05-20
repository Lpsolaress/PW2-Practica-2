const { spawn } = require('node:child_process');

function npmCmd() {
  return process.platform === 'win32' ? 'npm.cmd' : 'npm';
}

function run(name, args) {
  const child = spawn(npmCmd(), args, {
    stdio: 'inherit',
    env: process.env
  });

  child.on('exit', (code, signal) => {
    if (signal) return;
    if (code === 0) return;
    process.exitCode = code ?? 1;
  });

  return child;
}

const children = [
  run('api', ['--prefix', 'frontend', 'run', 'start']),
  run('web', ['--prefix', 'svelte-frontend', 'run', 'dev'])
];

function shutdown(signal) {
  for (const child of children) {
    if (!child || child.killed) continue;
    child.kill(signal);
  }
}

process.on('SIGINT', () => {
  shutdown('SIGINT');
  process.exit(0);
});

process.on('SIGTERM', () => {
  shutdown('SIGTERM');
  process.exit(0);
});

process.on('exit', () => shutdown('SIGTERM'));

