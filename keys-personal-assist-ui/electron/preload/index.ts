import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
    platform: process.platform,
    selectDirectory: () => ipcRenderer.invoke('dialog:selectDirectory'),
    getDefaultBackupDir: () => ipcRenderer.invoke('dialog:getDefaultBackupDir'),
    listHostBackups: (dirPath?: string) => ipcRenderer.invoke('dialog:listHostBackups', dirPath),
    writeHostBackup: (dirPath: string, filename: string, content: string) => ipcRenderer.invoke('dialog:writeHostBackup', dirPath, filename, content),
    readHostBackup: (dirPath: string, filename: string) => ipcRenderer.invoke('dialog:readHostBackup', dirPath, filename),
    deleteHostBackup: (dirPath: string, filename: string) => ipcRenderer.invoke('dialog:deleteHostBackup', dirPath, filename),
    saveBackupFile: (filename: string, content: string) => ipcRenderer.invoke('dialog:saveBackupFile', filename, content),
    openBackupFile: () => ipcRenderer.invoke('dialog:openBackupFile'),
    onOAuthCallback: (callback: (url: string) => void) => {


        const listener = (_event: unknown, url: string) => callback(url)

        ipcRenderer.on('oauth-callback', listener)
        return () => {
            ipcRenderer.off('oauth-callback', listener)
        }
    }
})
