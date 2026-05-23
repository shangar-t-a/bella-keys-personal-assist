const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const https = require('https');

const uiDir = path.resolve(__dirname, '../../keys-personal-assist-ui');
const cacheDir = path.join(process.env.LOCALAPPDATA || path.join(process.env.USERPROFILE, 'AppData/Local'), 'electron-builder/Cache/winCodeSign');
const targetDir = path.join(cacheDir, 'winCodeSign-2.6.0');
const sevenZipBin = path.join(uiDir, 'node_modules/7zip-bin/win/x64/7za.exe');

if (process.platform !== 'win32') {
  console.log('Not on Windows, skipping winCodeSign setup.');
  process.exit(0);
}

console.log('Checking winCodeSign cache to avoid symbolic link extraction failures...');

// Check if already extracted
if (fs.existsSync(path.join(targetDir, 'windows-10'))) {
  console.log('winCodeSign is already correctly set up.');
  process.exit(0);
}

// Ensure cache directory exists
fs.mkdirSync(cacheDir, { recursive: true });

// Check for existing 7z files in the cache directory
let zipPath = '';
const files = fs.readdirSync(cacheDir);
const sevenZipFiles = files.filter(f => f.endsWith('.7z'));

if (sevenZipFiles.length > 0) {
  // Sort by mtime to find the latest downloaded one
  const sorted = sevenZipFiles.map(f => {
    const filePath = path.join(cacheDir, f);
    return { name: filePath, time: fs.statSync(filePath).mtimeMs };
  }).sort((a, b) => b.time - a.time);
  zipPath = sorted[0].name;
  console.log(`Found cached 7z archive: ${zipPath}`);
}

async function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, (response) => {
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download: ${response.statusCode}`));
        return;
      }
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    }).on('error', (err) => {
      fs.unlink(dest, () => {});
      reject(err);
    });
  });
}

async function main() {
  try {
    if (!zipPath) {
      zipPath = path.join(cacheDir, 'winCodeSign-2.6.0.7z');
      console.log('Downloading winCodeSign-2.6.0.7z from GitHub releases...');
      const url = 'https://github.com/electron-userland/electron-builder-binaries/releases/download/winCodeSign-2.6.0/winCodeSign-2.6.0.7z';
      await downloadFile(url, zipPath);
      console.log('Downloaded successfully.');
    }

    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }

    console.log(`Extracting ${zipPath} to ${targetDir} excluding 'darwin'...`);
    
    if (!fs.existsSync(sevenZipBin)) {
      console.error(`Cannot find 7za.exe at ${sevenZipBin}`);
      process.exit(1);
    }

    const res = spawnSync(sevenZipBin, ['x', zipPath, `-o${targetDir}`, '-x!darwin', '-y'], {
      stdio: 'inherit'
    });

    if (res.status !== 0) {
      console.error('7-Zip extraction failed');
      process.exit(res.status || 1);
    }

    console.log('winCodeSign setup completed successfully!');
  } catch (err) {
    console.error('Setup failed:', err);
    process.exit(1);
  }
}

main();
