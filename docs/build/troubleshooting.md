# Troubleshooting Guide

Common issues and solutions for building and running the application.

## Build Issues

### Docker Build Fails

**Symptom:**
```
Error: buildx failed with: ERROR: failed to solve: rpc error
```

**Solutions:**

1. **Docker not running:**
   ```bash
   docker info  # Should show server info
   # Start Docker Desktop if not running
   ```

2. **Out of disk space:**
   ```bash
   docker system prune -f  # Clean unused images
   docker builder prune -f  # Clean build cache
   ```

3. **Buildx not initialized:**
   ```bash
   docker buildx create --use
   docker buildx inspect --bootstrap
   ```

### CI/CD Build Fails

**Symptom:** GitHub Actions workflow fails

**Check:**
1. VERSION file was committed
2. `packages: write` permission is in workflow
3. Service path is correct in workflow

**Fix:**
```bash
# Ensure VERSION change is committed
git add services/expense-manager-service/VERSION
git commit -m "chore(ems): bump version"
git push origin main
```

## Run Issues

### Port Conflicts

**Symptom:**
```
Error: listen tcp 0.0.0.0:8000: bind: address already in use
```

**Find process using port:**
```bash
# Linux/macOS
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

**Fix:** Edit `docker/.env`:
```bash
EMS_PORT=8001
BELLA_CHAT_PORT=8002
KEYS_UI_PORT=5001
```

### Services Won't Start

**Symptom:** `docker compose up` hangs or fails

**Check logs:**
```bash
docker compose logs [service-name]
```

**Common causes:**
1. **Missing environment file:**
   ```bash
   cp docker/.env.example docker/.env
   # Edit with your API keys
   ```

2. **Database not ready:**
   ```bash
   # Wait for db to be healthy
   docker compose up -d db
   sleep 10
   docker compose up -d
   ```

3. **Image pull fails:**
   ```bash
   # Check image exists in GHCR
   docker pull ghcr.io/[owner]/expense-manager-service:latest
   
   # Ensure you're logged in
   docker login ghcr.io -u USERNAME
   ```

### Out of Memory

**Symptom:**
```
Error: container exited with code 137
```

**Solutions:**

1. **Reduce service profile:**
   ```bash
   # Use minimal profile
   docker compose up -d expense-manager-service db
   ```

2. **Increase Docker memory:**
   - Docker Desktop → Settings → Resources → Memory
   - Increase to 6GB+ for full profile

3. **Clear unused containers:**
   ```bash
   docker system prune -a
   ```

## Electron App Issues

### Build Fails

**Symptom:** `npm run build:electron` fails

**Solutions:**

1. **Node version:**
   ```bash
   node --version  # Should be 18+
   nvm use 18      # Switch if needed
   ```

2. **Clear dependencies:**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Missing native modules:**
   ```bash
   npm rebuild
   ```

### Services Not Connecting

**Symptom:** Desktop app shows "Service unavailable"

**Check:**
1. Docker Desktop is running
2. Services are healthy:
   ```bash
   docker compose ps
   ```
3. Firewall not blocking ports

## Image Registry Issues

### GHCR Authentication

**Symptom:**
```
Error: unauthorized: authentication required
```

**Fix:**
```bash
# Login to GHCR
docker login ghcr.io -u USERNAME
# Enter personal access token as password

# Or use GITHUB_TOKEN
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### Image Not Found

**Symptom:**
```
Error: manifest unknown
```

**Check:**
1. Image was pushed successfully (check Actions tab)
2. Repository is public or you have access
3. Tag exists:
   ```bash
   docker pull ghcr.io/[owner]/[image]:[tag]
   ```

## Performance Issues

### Slow Builds

**Causes:**
1. No build cache
2. Large context (check `.dockerignore`)
3. Network issues pulling base images

**Optimize:**
```bash
# Check cache is working
docker build --cache-from type=gha .

# Minimize context
cat .dockerignore  # Should exclude node_modules, .git
```

### Slow Startup

**Causes:**
1. Large images
2. Database migrations running
3. Resource constraints

**Solutions:**
1. Use `minimal` profile
2. Pre-pull images:
   ```bash
   docker compose pull
   ```
3. Check resource usage:
   ```bash
   docker stats
   ```

## Debugging

### Enable Verbose Logging

**Docker:**
```bash
DEBUG=1 docker compose up
```

**Electron:**
```bash
DEBUG=* npm run electron:dev
```

### Check Service Health

```bash
# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:5000

# Check logs
docker compose logs -f --tail=100
```

### Reset Everything

**Nuclear option - clears all data:**

```bash
# Stop and remove everything
docker compose down -v
docker system prune -a --volumes

# Rebuild from scratch
docker compose up --build -d
```

## Getting Help

If issues persist:

1. Check [GitHub Actions logs](../../actions) for CI failures
2. Review [CI/CD Pipeline](./ci-cd-pipeline.md) documentation
3. Check [Local Development](./local-development.md) setup
4. Verify [Scripts Reference](./scripts-reference.md) usage

## Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `port already allocated` | Port in use | Change port in `.env` |
| `no space left on device` | Disk full | `docker system prune` |
| `connection refused` | Service not ready | Wait for health check |
| `unauthorized` | GHCR auth issue | `docker login ghcr.io` |
| `manifest unknown` | Image doesn't exist | Check image name/tag |
| `exit code 137` | OOM killed | Increase memory limit |
