const { spawnSync } = require('child_process');
const fs = require('var-fs' in global ? null : 'fs'); // standard require
const path = require('path');

const uiDir = path.resolve(__dirname, '../../keys-personal-assist-ui');
const electronDir = path.join(uiDir, 'node_modules/electron');
const packageJsonPath = path.join(uiDir, 'package.json');

// Check and install dependencies if needed
const lockFile = path.join(uiDir, 'package-lock.json');
const markerFile = path.join(uiDir, 'node_modules/.last-install');

let needsInstall = false;
if (!fs.existsSync(path.join(uiDir, 'node_modules'))) {
  needsInstall = true;
} else if (!fs.existsSync(markerFile)) {
  needsInstall = true;
} else if (fs.existsSync(lockFile)) {
  const lockTime = fs.statSync(lockFile).mtimeMs;
  const markerTime = fs.statSync(markerFile).mtimeMs;
  if (lockTime > markerTime) {
    needsInstall = true;
  }
}

if (needsInstall) {
  console.log('Dependencies are missing or outdated. Installing dependencies (optimized)...');
  const npmCmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';
  const res = spawnSync(npmCmd, ['install', '--ignore-scripts', '--prefer-offline', '--no-audit', '--no-fund', '--loglevel=error'], {
    cwd: uiDir,
    stdio: 'inherit',
    shell: true
  });
  if (res.status !== 0) {
    console.error('npm install failed');
    process.exit(res.status || 1);
  }
  // Create node_modules directory if it wasn't created, then write marker
  fs.mkdirSync(path.dirname(markerFile), { recursive: true });
  fs.writeFileSync(markerFile, new Date().toISOString());
  console.log('Dependencies installed successfully.');
}

if (!fs.existsSync(packageJsonPath)) {
  console.error('Cannot find package.json');
  process.exit(1);
}

const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
const electronVersion = (packageJson.devDependencies.electron || '').replace(/^[^\d]+/, '');

if (!electronVersion) {
  console.error('Electron version not found in package.json devDependencies');
  process.exit(1);
}

const platform = process.platform;
const arch = process.arch;

console.log(`Setting up Electron v${electronVersion} for ${platform}-${arch}...`);

// Determine the platform path
let platformPath = '';
if (platform === 'win32') {
  platformPath = 'electron.exe';
} else if (platform === 'darwin') {
  platformPath = 'Electron.app/Contents/MacOS/Electron';
} else {
  platformPath = 'electron';
}

const versionFile = path.join(electronDir, 'dist/version');
const pathFile = path.join(electronDir, 'path.txt');
const electronExecutable = path.join(electronDir, 'dist', platformPath);

// Check if already installed
if (fs.existsSync(versionFile) && fs.existsSync(pathFile) && fs.existsSync(electronExecutable)) {
  const currentVersion = fs.readFileSync(versionFile, 'utf8').trim().replace(/^v/, '');
  if (currentVersion === electronVersion) {
    console.log('Electron is already correctly installed.');
    process.exit(0);
  }
}

// Download the zip using @electron/get (which is installed in node_modules)
// Resolve node_modules path dynamically
module.paths.push(path.join(uiDir, 'node_modules'));
let downloadArtifact;
try {
  downloadArtifact = require('@electron/get').downloadArtifact;
} catch (e) {
  console.error('Failed to load @electron/get. Make sure npm install was run first.');
  process.exit(1);
}

async function main() {
  try {
    console.log('Downloading Electron zip...');
    const zipPath = await downloadArtifact({
      version: electronVersion,
      artifactName: 'electron',
      platform,
      arch
    });
    console.log('Downloaded zip to:', zipPath);

    const distDir = path.join(electronDir, 'dist');
    if (fs.existsSync(distDir)) {
      console.log('Removing old dist directory...');
      fs.rmSync(distDir, { recursive: true, force: true });
    }
    fs.mkdirSync(distDir, { recursive: true });

    console.log(`Extracting zip to ${distDir}...`);
    try {
      if (platform === 'win32') {
        console.log('Extracting with PowerShell Expand-Archive...');
        const res = spawnSync('powershell', [
          '-NoProfile',
          '-NonInteractive',
          '-Command',
          `Expand-Archive -Path '${zipPath.replace(/'/g, "''")}' -DestinationPath '${distDir.replace(/'/g, "''")}' -Force`
        ], { stdio: 'inherit' });
        if (res.status !== 0) {
          throw new Error('PowerShell extraction failed');
        }
      } else {
        console.log('Extracting with unzip...');
        const res = spawnSync('unzip', ['-o', zipPath, '-d', distDir], { stdio: 'inherit' });
        if (res.status !== 0) {
          throw new Error('unzip extraction failed');
        }
      }
    } catch (err) {
      console.warn('Native extraction failed, falling back to extract-zip npm package:', err.message);
      const extract = require('extract-zip');
      await extract(zipPath, { dir: distDir });
    }

    // Write path.txt (without any trailing newline!)
    fs.writeFileSync(pathFile, platformPath);
    console.log('Wrote path.txt');

    console.log('Electron setup completed successfully!');
  } catch (err) {
    console.error('Setup failed:', err);
    process.exit(1);
  }
}

main();
