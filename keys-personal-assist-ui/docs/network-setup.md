# Network Setup

## Architecture Overview

```txt
Browser (localhost:3000)
    ↓
nginx (port 80 in container)
    ↓
    ├─→ /api/bella-chat/* → bella-chat-service:5000
    └─→ /api/ems/*        → expense-manager-service:8000
```

## How It Works

### Development Mode (`npm run dev`)

Vite dev server runs on `localhost:3000` with built-in proxy:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api/bella-chat': {
      target: 'http://localhost:5000',  // Your local backend
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api\/bella-chat/, ''),
    },
    '/api/ems': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api\/ems/, ''),
    },
  },
}
```

**Example:**

- Browser requests: `http://localhost:3000/api/ems/v1/account/list`
- Vite proxies to: `http://localhost:8000/v1/account/list`

### Production Mode (Docker)

nginx serves static files and proxies API requests:

```nginx
# nginx.conf
location /api/bella-chat {
    proxy_pass http://bella-chat-service:5000;
    # ... proxy headers
}

location /api/ems {
    proxy_pass http://expense-manager-service:8000;
    # ... proxy headers
}
```

**Example:**

- Browser requests: `http://localhost:3000/api/ems/v1/account/list`
- nginx proxies to: `http://expense-manager-service:8000/v1/account/list`

## API Client Configuration

Both clients use relative paths that work in dev and production:

```typescript
// src/api/clients/ems-client.ts
class EMSClient {
  private baseURL = '/api/ems';  // ← Relative path
}

// src/api/clients/bella-chat-client.ts
class BellaChatClient {
  private baseURL = '/api/bella-chat';  // ← Relative path
}
```

No environment variables needed. Proxying handles routing automatically.

## Docker Networking

All services run on `bella-keys-network` bridge network:

```yaml
# docker-compose.yaml
networks:
  bella-keys-network:
    driver: bridge
```

**Service Names = DNS Names:**

- `expense-manager-service` → Resolves to container IP
- `bella-chat-service` → Resolves to container IP
- `postgres-database` → Resolves to container IP
- `qdrant` → Resolves to container IP

**Why not IPs?**

- Container IPs change on restart
- Service names are stable
- Docker DNS handles resolution automatically

## Port Mapping

| Service | Internal Port | External Port | Access |
|---------|--------------|---------------|---------|
| UI (nginx) | 80 | 3000 | <http://localhost:3000> |
| EMS | 8000 | 8000 | <http://localhost:8000> |
| Bella Chat | 5000 | 5000 | <http://localhost:5000> |
| Postgres | 5432 | 5432 | localhost:5432 |
| Qdrant | 6333/6334 | 6333/6334 | <http://localhost:6333> |
| Phoenix | 6006 | 6006 | <http://localhost:6006> |

## Container Communication Flow

### Internal (Container-to-Container)

```txt
keys-personal-assist-ui (nginx)
    ├─→ bella-chat-service:5000      ✓ Uses service name
    └─→ expense-manager-service:8000  ✓ Uses service name

bella-chat-service
    └─→ qdrant:6333                   ✓ Uses service name

expense-manager-service
    └─→ postgres-database:5432        ✓ Uses service name
```

### External (Host-to-Container)

```txt
Your Machine
    ├─→ localhost:3000  → UI
    ├─→ localhost:5000  → Bella Chat
    ├─→ localhost:8000  → EMS
    └─→ localhost:5432  → Postgres
```

## Multi-Stage Build

UI container uses 2-stage build for optimization:

**Stage 1 - Builder (node:25-alpine):**

- Install dependencies
- Build React app → `/app/dist`
- **Size: ~300 MB** (discarded)

**Stage 2 - Production (nginx:1.27-alpine):**

- Copy nginx config
- Copy built assets from stage 1
- **Size: ~22 MB** (final image)

**Benefits:**

- 94% smaller image
- No Node.js in production
- Faster startup, lower memory
- More secure (no source code/deps)

## Running the App

### Local Development

```bash
cd keys-personal-assist-ui
npm run dev
# Vite dev server starts on http://localhost:3000
# Hot reload enabled
```

### Docker Production

```bash
# From project root
docker-compose up -d

# Check status
docker-compose ps

# View UI logs
docker logs keys-personal-assist-ui

# Rebuild UI after changes
docker-compose build keys-personal-assist-ui
docker-compose up -d keys-personal-assist-ui
```

## Build Optimizations

The build is configured for optimal performance:

1. **Code Splitting**: All routes lazy-loaded
   - HomePage: 2.3 KB
   - ChatPage: 21.3 KB (loads markdown libs on-demand)
   - DashboardPage: 2.6 KB
   - SpendingAccountSummaryPage: 12.7 KB

2. **Vendor Chunking**: Libraries split into separate chunks
   - vendor-react: 0 KB (tree-shaken)
   - vendor-mui: 256 KB → 77.5 KB gzipped
   - vendor-markdown: 779 KB → 270 KB gzipped (lazy)
   - vendor-router: 46 KB → 16.5 KB gzipped

3. **Asset Optimization**:
   - Gzip compression enabled
   - 1-year cache for static assets
   - Fonts loaded progressively

**Initial Load (Homepage):** ~470 KB gzipped
**Chat Page (on-demand):** +270 KB gzipped

## Troubleshooting

### UI can't connect to backend

- **Dev**: Check backend is running on localhost:5000/8000
- **Docker**: Check `docker-compose ps` shows all services "Up"
- **Docker**: Check logs: `docker logs <service-name>`

### Port already in use

```bash
# Find process using port 3000
netstat -ano | findstr :3000

# Kill the process (replace PID)
taskkill /PID <pid> /F
```

### nginx config changes not applying

```bash
# Rebuild UI container
docker-compose build keys-personal-assist-ui
docker-compose up -d keys-personal-assist-ui
```

### API request fails with CORS

- Should never happen - nginx proxies prevent CORS
- If you see CORS errors, the proxy isn't working
- Check nginx config and container logs

## Key Takeaways

1. **Always use relative paths** in API clients (`/api/ems`, not `http://localhost:8000`)
2. **Service names, not IPs** for container-to-container communication
3. **Proxying eliminates CORS** - nginx/Vite handles cross-origin requests
4. **Multi-stage builds** = small production images
5. **Code splitting** = fast initial loads
