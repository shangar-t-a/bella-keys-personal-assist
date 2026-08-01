import { ipcMain, dialog, app, BrowserWindow, nativeImage, shell } from "electron";
import path from "path";
import __cjs_mod__ from "node:module";
const __filename = import.meta.filename;
const __dirname = import.meta.dirname;
const require2 = __cjs_mod__.createRequire(import.meta.url);
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
