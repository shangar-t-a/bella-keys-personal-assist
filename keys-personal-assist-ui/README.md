# Keys Personal Assist UI

React-based desktop interface for Bella Keys, powered by Electron.

## Technology Stack

* React 19
* TypeScript
* Vite
* Material UI v6
* React Router v7
* React Hook Form + Zod
* Sonner

## Development

### Installation
```bash
npm install --legacy-peer-deps
```

### Local Dev Server
```bash
npm run dev
```
Launches the frontend locally at `http://localhost:3000`.

### Production Build
```bash
npm run build
```
Outputs build artifacts to the `dist/` directory.

## API Integration

The frontend communicates with backend services using relative paths:
* `/api/ems/*` redirects to the Expense Manager Service.
* `/api/bella-chat/*` redirects to the Bella Chat Service.

Vite dev server proxies these paths locally in development, while Nginx handles the routing in production containers. See [network-setup.md](docs/network-setup.md) for details.
