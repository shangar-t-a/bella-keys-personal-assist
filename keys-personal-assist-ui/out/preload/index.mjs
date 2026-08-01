import { contextBridge, ipcRenderer } from "electron";
contextBridge.exposeInMainWorld("electronAPI", {
  platform: process.platform,
  selectDirectory: () => ipcRenderer.invoke("dialog:selectDirectory"),
  getDefaultBackupDir: () => ipcRenderer.invoke("dialog:getDefaultBackupDir"),
  listHostBackups: (dirPath) => ipcRenderer.invoke("dialog:listHostBackups", dirPath),
  writeHostBackup: (dirPath, filename, content) => ipcRenderer.invoke("dialog:writeHostBackup", dirPath, filename, content),
  readHostBackup: (dirPath, filename) => ipcRenderer.invoke("dialog:readHostBackup", dirPath, filename),
  deleteHostBackup: (dirPath, filename) => ipcRenderer.invoke("dialog:deleteHostBackup", dirPath, filename),
  saveBackupFile: (filename, content) => ipcRenderer.invoke("dialog:saveBackupFile", filename, content),
  openBackupFile: () => ipcRenderer.invoke("dialog:openBackupFile"),
  onOAuthCallback: (callback) => {
    const listener = (_event, url) => callback(url);
    ipcRenderer.on("oauth-callback", listener);
    return () => {
      ipcRenderer.off("oauth-callback", listener);
    };
  }
});
