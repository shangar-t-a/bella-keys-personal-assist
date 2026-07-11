import { contextBridge, ipcRenderer } from "electron";
contextBridge.exposeInMainWorld("electronAPI", {
  platform: process.platform,
  onOAuthCallback: (callback) => {
    const listener = (_event, url) => callback(url);
    ipcRenderer.on("oauth-callback", listener);
    return () => {
      ipcRenderer.off("oauth-callback", listener);
    };
  }
});
