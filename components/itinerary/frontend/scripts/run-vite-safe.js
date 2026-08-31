/**
 * Vite fails to transform modules when the project path contains an apostrophe
 * (e.g. C:\Users\Name's ...). On Windows, mirror the frontend into a safe
 * directory and run the dev server from there.
 */
import { spawn, spawnSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(__dirname, '..');
// On Windows, realpathSync.native expands subst/8.3 paths to the true long path
const realFrontendRoot = (
  fs.realpathSync.native || fs.realpathSync
)(frontendRoot);
const SAFE_ROOT = process.env.TOUR_CEYLON_SAFE_ROOT || 'C:\\tour_ceylon_fe';
// Vite cannot transform JSX when any path segment contains an apostrophe
const hasUnsafePath = /['\u2019]/.test(frontendRoot) || /['\u2019]/.test(realFrontendRoot);

function copyPath(src, dest) {
  if (!fs.existsSync(src)) return;
  fs.cpSync(src, dest, { recursive: true, force: true });
}

function syncToSafeRoot() {
  const safeResolved = path.resolve(SAFE_ROOT);
  if (path.resolve(frontendRoot) === safeResolved || realFrontendRoot === safeResolved) {
    return;
  }
  fs.mkdirSync(SAFE_ROOT, { recursive: true });
  for (const item of [
    'src',
    'public',
    'index.html',
    'vite.config.js',
    'package.json',
    'package-lock.json',
    '.env',
    '.env.local',
    '.env.development',
  ]) {
    copyPath(path.join(frontendRoot, item), path.join(SAFE_ROOT, item));
  }

  if (!fs.existsSync(path.join(SAFE_ROOT, 'node_modules'))) {
    console.log(`[vite-safe] Installing dependencies in ${SAFE_ROOT} ...`);
    const install = spawnSync('npm', ['install'], {
      cwd: SAFE_ROOT,
      stdio: 'inherit',
      shell: true,
    });
    if (install.status !== 0) {
      process.exit(install.status || 1);
    }
  }
}

function runVite(cwd) {
  const args = process.argv.slice(2);
  // Avoid shell:true so Windows doesn't mangle paths/args; invoke vite bin directly.
  const viteBin = path.join(cwd, 'node_modules', 'vite', 'bin', 'vite.js');
  const cmd = fs.existsSync(viteBin) ? process.execPath : 'npx';
  const cmdArgs = fs.existsSync(viteBin) ? [viteBin, ...args] : ['vite', ...args];
  const child = spawn(cmd, cmdArgs, {
    cwd,
    stdio: 'inherit',
    shell: !fs.existsSync(viteBin),
    env: process.env,
  });
  child.on('exit', (code, signal) => {
    if (signal) process.kill(process.pid, signal);
    process.exit(code ?? 1);
  });
}

if (hasUnsafePath) {
  console.log(`[vite-safe] Unsafe project path detected:`);
  console.log(`[vite-safe]   cwd:  ${frontendRoot}`);
  console.log(`[vite-safe]   real: ${realFrontendRoot}`);
  console.log(`[vite-safe] Syncing to ${SAFE_ROOT} and starting Vite there.`);
  syncToSafeRoot();
  runVite(SAFE_ROOT);
} else {
  runVite(frontendRoot);
}
