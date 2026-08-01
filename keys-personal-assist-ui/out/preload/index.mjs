import { contextBridge, ipcRenderer } from "electron";
contextBridge.exposeInMainWorld("electronAPI", {
  platform: process.platform,
  selectDirectory: () => ipcRenderer.invoke("dialog:selectDirectory"),
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
