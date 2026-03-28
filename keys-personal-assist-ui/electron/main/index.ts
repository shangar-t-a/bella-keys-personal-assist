import { app, BrowserWindow, shell, nativeImage } from 'electron'
import path from 'path'

function createWindow(): void {
    const isDev = !!process.env['ELECTRON_RENDERER_URL']
    const iconPath = isDev
        ? path.join(__dirname, '../../public/favicon.ico')
        : path.join(__dirname, '../renderer/favicon.ico')
    const icon = nativeImage.createFromPath(iconPath)

    const mainWindow = new BrowserWindow({
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
        mainWindow.show()
    })

    // Open external links in the system browser, not inside the app
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url)
        return { action: 'deny' }
    })

    if (process.env['ELECTRON_RENDERER_URL']) {
        // Dev: electron-vite injects this env var pointing to the Vite dev server
        mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
    } else {
        // Prod: load the built renderer index.html
        mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'))
    }
}

app.whenReady().then(() => {
    createWindow()

    app.on('activate', () => {
        // macOS: re-create the window when the dock icon is clicked and no windows are open
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow()
        }
    })
})

app.on('window-all-closed', () => {
    // On macOS apps conventionally stay active until the user quits explicitly
    if (process.platform !== 'darwin') {
        app.quit()
    }
})
