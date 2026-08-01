import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
    platform: process.platform,
    selectDirectory: () => ipcRenderer.invoke('dialog:selectDirectory'),
    onOAuthCallback: (callback: (url: string) => void) => {

        const listener = (_event: unknown, url: string) => callback(url)
        ipcRenderer.on('oauth-callback', listener)
        return () => {
            ipcRenderer.off('oauth-callback', listener)
        }
    }
})
