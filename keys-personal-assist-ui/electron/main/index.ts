import { app, BrowserWindow, dialog, ipcMain, nativeImage, shell } from 'electron'
import path from 'path'

// Handle native directory picker dialog requests
ipcMain.handle('dialog:selectDirectory', async () => {
    const result = await dialog.showOpenDialog({
        title: 'Select Backup Folder Location',
        properties: ['openDirectory', 'createDirectory']
    })
    if (!result.canceled && result.filePaths.length > 0) {
        return result.filePaths[0]
    }
    return null
})

// Register custom protocol handler for Windows/macOS/Linux

if (process.defaultApp) {
    if (process.argv.length >= 2) {
        app.setAsDefaultProtocolClient('bella-app', process.execPath, [path.resolve(process.argv[1])])
    }
} else {
    app.setAsDefaultProtocolClient('bella-app')
}

let mainWindow: BrowserWindow | null = null
let pendingUrl: string | null = null

// Handle macOS custom protocol activation when app is running or cold-started
app.on('open-url', (event, url) => {
    event.preventDefault()
    if (mainWindow) {
        mainWindow.webContents.send('oauth-callback', url)
    } else {
        pendingUrl = url
    }
})

function createWindow(): void {
    const isDev = !!process.env['ELECTRON_RENDERER_URL']
    const iconPath = isDev
        ? path.join(__dirname, '../../public/icon.png')
        : path.join(__dirname, '../renderer/icon.png')
    const icon = nativeImage.createFromPath(iconPath)

    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        minWidth: 900,
        minHeight: 600,
        show: false,
        autoHideMenuBar: true,
        icon,
        webPreferences: {
            preload: path.join(__dirname, '../preload/index.mjs'),
            contextIsolation: true,
            nodeIntegration: false,
            sandbox: false,
        },
    })

    mainWindow.on('ready-to-show', () => {
        mainWindow?.show()
    })

    // Open external links in the system browser, not inside the app
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url)
        return { action: 'deny' }
    })

    // Handle cold start URL delivery on Windows/Linux
    const coldStartUrl = process.argv.find((arg) => arg.startsWith('bella-app://'))
    if (coldStartUrl) {
        mainWindow.webContents.on('did-finish-load', () => {
            mainWindow?.webContents.send('oauth-callback', coldStartUrl)
        })
    }

    // Handle cold start URL delivery on macOS
    if (pendingUrl) {
        mainWindow.webContents.on('did-finish-load', () => {
            if (pendingUrl) {
                mainWindow?.webContents.send('oauth-callback', pendingUrl)
                pendingUrl = null
            }
        })
    }

    if (process.env['ELECTRON_RENDERER_URL']) {
        // Dev: electron-vite injects this env var pointing to the Vite dev server
        mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
    } else {
        // Prod: load the built renderer index.html
        mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'))
    }

    mainWindow.on('closed', () => {
        mainWindow = null
    })
}

const gotSingleInstanceLock = app.requestSingleInstanceLock()

if (!gotSingleInstanceLock) {
    app.quit()
} else {
    app.on('second-instance', (event, commandLine) => {
        if (mainWindow) {
            if (mainWindow.isMinimized()) {
                mainWindow.restore()
            }
            mainWindow.focus()
        }

        // Handle custom protocol URL delivery for secondary instances on Windows/Linux
        const url = commandLine.find((arg) => arg.startsWith('bella-app://'))
        if (url && mainWindow) {
            mainWindow.webContents.send('oauth-callback', url)
        }
    })

    app.whenReady().then(() => {
        createWindow()

        app.on('activate', () => {
            // macOS: re-create the window when the dock icon is clicked and no windows are open
            if (BrowserWindow.getAllWindows().length === 0) {
                createWindow()
            }
        })
    })
}

app.on('window-all-closed', () => {
    // On macOS apps conventionally stay active until the user quits explicitly
    if (process.platform !== 'darwin') {
        app.quit()
    }
})
