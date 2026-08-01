import { ipcMain, dialog, app, BrowserWindow, nativeImage, shell } from "electron";
import fs from "fs";
import path from "path";
import __cjs_mod__ from "node:module";
const __filename = import.meta.filename;
const __dirname = import.meta.dirname;
const require2 = __cjs_mod__.createRequire(import.meta.url);
function formatBytes(sizeBytes) {
  if (sizeBytes < 1024) return `${sizeBytes} B`;
  if (sizeBytes < 1024 * 1024) return `${(sizeBytes / 1024).toFixed(1)} KB`;
  return `${(sizeBytes / (1024 * 1024)).toFixed(2)} MB`;
}
ipcMain.handle("dialog:selectDirectory", async () => {
  const result = await dialog.showOpenDialog({
    title: "Select Backup Folder Location",
    properties: ["openDirectory", "createDirectory"]
  });
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});
ipcMain.handle("dialog:getDefaultBackupDir", async () => {
  const defaultDir = path.join(app.getPath("home"), ".bella-keys", "backups");
  if (!fs.existsSync(defaultDir)) {
    fs.mkdirSync(defaultDir, { recursive: true });
  }
  return defaultDir;
});
ipcMain.handle("dialog:listHostBackups", async (_event, targetDir) => {
  const dirPath = targetDir || path.join(app.getPath("home"), ".bella-keys", "backups");
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    return [];
  }
  const files = fs.readdirSync(dirPath);
  const snapshots = [];
  for (const file of files) {
    if (file.endsWith(".json") && (file.startsWith("ems_backup_") || file.startsWith("pre_restore_"))) {
      const fullPath = path.join(dirPath, file);
      try {
        const stat = fs.statSync(fullPath);
        snapshots.push({
          filename: file,
          filepath: fullPath,
          size_bytes: stat.size,
          formatted_size: formatBytes(stat.size),
          created_at: stat.mtime.toISOString(),
          type: file.startsWith("pre_restore_") ? "pre_restore" : "manual",
          record_counts: {},
          total_records: 0
        });
      } catch {
      }
    }
  }
  snapshots.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  return snapshots;
});
ipcMain.handle("dialog:writeHostBackup", async (_event, dirPath, filename, content) => {
  const targetDir = dirPath || path.join(app.getPath("home"), ".bella-keys", "backups");
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }
  const fullPath = path.join(targetDir, filename);
  fs.writeFileSync(fullPath, content, "utf-8");
  const stat = fs.statSync(fullPath);
  return {
    filename,
    filepath: fullPath,
    size_bytes: stat.size,
    formatted_size: formatBytes(stat.size),
    created_at: stat.mtime.toISOString()
  };
});
ipcMain.handle("dialog:readHostBackup", async (_event, dirPath, filename) => {
  const targetDir = dirPath || path.join(app.getPath("home"), ".bella-keys", "backups");
  const fullPath = path.join(targetDir, filename);
  if (!fs.existsSync(fullPath)) {
    throw new Error(`Backup file not found on host PC: ${fullPath}`);
  }
  return fs.readFileSync(fullPath, "utf-8");
});
ipcMain.handle("dialog:deleteHostBackup", async (_event, dirPath, filename) => {
  const targetDir = dirPath || path.join(app.getPath("home"), ".bella-keys", "backups");
  const fullPath = path.join(targetDir, filename);
  if (fs.existsSync(fullPath)) {
    fs.unlinkSync(fullPath);
  }
  return true;
});
ipcMain.handle("dialog:saveBackupFile", async (_event, defaultFilename, content) => {
  const result = await dialog.showSaveDialog({
    title: "Save Backup File to PC Folder",
    defaultPath: defaultFilename,
    filters: [{ name: "JSON Backup File", extensions: ["json"] }]
  });
  if (!result.canceled && result.filePath) {
    fs.writeFileSync(result.filePath, content, "utf-8");
    return result.filePath;
  }
  return null;
});
ipcMain.handle("dialog:openBackupFile", async () => {
  const result = await dialog.showOpenDialog({
    title: "Select Backup File from PC",
    properties: ["openFile"],
    filters: [{ name: "JSON Backup File", extensions: ["json"] }]
  });
  if (!result.canceled && result.filePaths.length > 0) {
    const filePath = result.filePaths[0];
    const content = fs.readFileSync(filePath, "utf-8");
    const filename = path.basename(filePath);
    return { filePath, filename, content };
  }
  return null;
});
if (process.defaultApp) {
  if (process.argv.length >= 2) {
    app.setAsDefaultProtocolClient("bella-app", process.execPath, [path.resolve(process.argv[1])]);
  }
} else {
  app.setAsDefaultProtocolClient("bella-app");
}
let mainWindow = null;
let pendingUrl = null;
app.on("open-url", (event, url) => {
  event.preventDefault();
  if (mainWindow) {
    mainWindow.webContents.send("oauth-callback", url);
  } else {
    pendingUrl = url;
  }
});
function createWindow() {
  const isDev = !!process.env["ELECTRON_RENDERER_URL"];
  const iconPath = isDev ? path.join(__dirname, "../../public/icon.png") : path.join(__dirname, "../renderer/icon.png");
  const icon = nativeImage.createFromPath(iconPath);
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    show: false,
    autoHideMenuBar: true,
    icon,
    webPreferences: {
      preload: path.join(__dirname, "../preload/index.mjs"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });
  mainWindow.on("ready-to-show", () => {
    mainWindow?.show();
  });
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });
  const coldStartUrl = process.argv.find((arg) => arg.startsWith("bella-app://"));
  if (coldStartUrl) {
    mainWindow.webContents.on("did-finish-load", () => {
      mainWindow?.webContents.send("oauth-callback", coldStartUrl);
    });
  }
  if (pendingUrl) {
    mainWindow.webContents.on("did-finish-load", () => {
      if (pendingUrl) {
        mainWindow?.webContents.send("oauth-callback", pendingUrl);
        pendingUrl = null;
      }
    });
  }
  if (process.env["ELECTRON_RENDERER_URL"]) {
    mainWindow.loadURL(process.env["ELECTRON_RENDERER_URL"]);
  } else {
    mainWindow.loadFile(path.join(__dirname, "../renderer/index.html"));
  }
  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}
const gotSingleInstanceLock = app.requestSingleInstanceLock();
if (!gotSingleInstanceLock) {
  app.quit();
} else {
  app.on("second-instance", (event, commandLine) => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) {
        mainWindow.restore();
      }
      mainWindow.focus();
    }
    const url = commandLine.find((arg) => arg.startsWith("bella-app://"));
    if (url && mainWindow) {
      mainWindow.webContents.send("oauth-callback", url);
    }
  });
  app.whenReady().then(() => {
    createWindow();
    app.on("activate", () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
      }
    });
  });
}
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
