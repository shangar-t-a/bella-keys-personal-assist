const isElectron = import.meta.env.VITE_APP_ENV === 'electron'

export function getEmsBase(): string {
    return isElectron ? 'http://localhost:8000' : '/api/ems'
}

export function getBellaChatBase(): string {
    return isElectron ? 'http://localhost:5000' : '/api/bella-chat'
}
