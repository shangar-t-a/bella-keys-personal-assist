# Network Setup

## Architecture

```txt
Browser (localhost:3000)
    ↓
nginx (port 80 in container)
    ↓
    ├─→ /api/bella-chat/* → bella-chat-dev:5000
    └─→ /api/ems/*        → ems-dev:8000
```

## How It Works

### Development Mode

The Vite development server runs on `localhost:3000` and proxies backend requests:
* `/api/bella-chat` targets `http://localhost:5000`
* `/api/ems` targets `http://localhost:8000`

### Production Mode (Docker)

Nginx serves static files and routes backend requests:
* `/api/bella-chat` targets `http://bella-chat-dev:5000`
* `/api/ems` targets `http://ems-dev:8000`

## Port Configuration

| Service | Internal Port | External Port | URL / Access |
| :--- | :--- | :--- | :--- |
| UI (nginx) | 80 | 3000 | http://localhost:3000 |
| EMS | 8000 | 8000 | http://localhost:8000 |
| Bella Chat | 5000 | 5000 | http://localhost:5000 |
| Postgres | 5432 | 5432 | localhost:5432 |
| Qdrant | 6333 | 6333 | http://localhost:6333 |
| Phoenix | 6006 | 6006 | http://localhost:6006 |

## Docker Networking

All services run on the `bella-network-dev` bridge network. Containerized services communicate using Docker DNS resolution (e.g., `bella-chat-dev:5000`, `ems-dev:8000`).
