# Docker Build Workflow

Comprehensive guide for the GitHub Actions Docker build system with GHCR (GitHub Container Registry).

## Overview

The CI pipeline uses a **reusable workflow architecture** to build and publish Docker images. This approach ensures consistency across all services while maintaining strict control over image proliferation.

## Architecture

### Workflow Files

| File | Purpose |
|------|---------|
| `.github/workflows/reusable-docker-build.yml` | Central reusable build logic |
| `.github/workflows/build-expense-manager.yml` | Expense Manager Service caller |
| `.github/workflows/build-bella-chat.yml` | Bella Chat Service caller |
| `.github/workflows/build-ems-mcp.yml` | EMS MCP Server caller |
| `.github/workflows/build-keys-ui.yml` | Keys Personal Assist UI caller |

### Services & VERSION Files

```
services/expense-manager-service/VERSION
services/bella-chat-service/VERSION
mcps/ems-mcp-server/VERSION
keys-personal-assist-ui/VERSION
```

## Trigger Events

| Event | Condition | Behavior |
|-------|-----------|----------|
| `workflow_dispatch` | Manual trigger via GitHub UI | Builds with optional custom tag |
| `push` to `main` | Only when `VERSION` file changes | Auto-builds and pushes to GHCR |

**Note:** No `pull_request` triggers to avoid unnecessary builds and GHCR pollution.

## Cautious Design Decisions

### 1. VERSION File Only Triggers

**Decision:** Builds only trigger on VERSION file changes, not on any source code changes.

**Rationale:**

- Prevents GHCR pollution with excessive image versions
- Maintains strict control over image proliferation
- Each build represents a deliberate release decision
- Reduces storage costs and registry clutter

**Trade-off:** Cannot auto-build on bugfix commits; must explicitly bump VERSION.

### 2. Conditional Latest Tag

**Decision:** `latest` tag is only pushed on `main` branch builds.

**Configuration:**

```yaml
type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' && inputs.push }}
```

**Rationale:**

- Prevents `latest` from pointing to unstable builds
- Ensures `latest` is always production-ready
- Avoids accidental rollbacks in deployments

### 3. Disabled Provenance and SBOM

**Decision:** Both provenance and SBOM generation are disabled.

```yaml
provenance: false
sbom: false
```

**Rationale:**

- Eliminates SHA package clutter in GHCR (the "extra packages" problem)
- Reduces build time and complexity
- Not required for internal use (no SLSA/cosign requirements)

**Trade-off:** No supply chain attestation. Re-enable if enterprise compliance requires it.

### 4. Scoped Build Cache

**Decision:** Each service has isolated GHA cache scope.

```yaml
cache-from: type=gha,scope=${{ inputs.image_name }}
cache-to: type=gha,mode=max,scope=${{ inputs.image_name }}
```

**Benefits:**

- Prevents monorepo cache pollution between services
- Faster builds for services with different dependencies
- Parallel builds don't corrupt shared cache

### 5. Digest-Based Output

**Decision:** Workflow exposes image digest as output.

```yaml
outputs:
  digest: ${{ steps.build.outputs.digest }}
  image: ${{ steps.meta.outputs.tags }}
```

**Use Case:**
Enables immutable deployments using `ghcr.io/org/app@sha256:abc123` instead of mutable tags.

### 6. Semantic Version Pins

**Decision:** Actions use semantic versions (`@v4`, `@v5`) instead of commit SHAs.

**Rationale:**

- Readable and maintainable
- GitHub's major version tags are rolling and tested
- SHA pinning requires Dependabot/Renovate for updates

**Security Note:** If supply-chain hardening becomes critical, migrate to SHA pinning with update automation.

### 7. No PR Builds

**Decision:** Removed `pull_request` triggers entirely.

**Rationale:**

- Every build creates a GHCR image (even if not pushed, layers are cached)
- Internal app doesn't need pre-merge validation builds
- VERSION file on main is the source of truth

## Image Tagging Strategy

### Generated Tags

| Tag Format | Example | When Applied |
|------------|---------|--------------|
| Semver | `ghcr.io/owner/expense-manager-service:1.2.0` | Always (from VERSION file) |
| `latest` | `ghcr.io/owner/expense-manager-service:latest` | Only on `main` branch |

### OCI Labels Applied

```yaml
org.opencontainers.image.source=${{ github.server_url }}/${{ github.repository }}
org.opencontainers.image.revision=${{ github.sha }}
org.opencontainers.image.version=${{ steps.resolve-tag.outputs.resolved_tag }}
org.opencontainers.image.title=${{ inputs.image_name }}
org.opencontainers.image.description=${{ inputs.image_description }}
org.opencontainers.image.created=${{ github.event.head_commit.timestamp }}
org.opencontainers.image.licenses=MIT
```

## Usage

### Manual Build

1. Navigate to **Actions** tab in GitHub
2. Select service workflow (e.g., "Build Expense Manager Service")
3. Click **Run workflow**
4. Optionally enter version tag, or leave empty to use VERSION file
5. Click **Run workflow**

### Auto-Triggered Build

```bash
# Update VERSION
echo "1.2.3" > services/expense-manager-service/VERSION

# Commit and push
git add services/expense-manager-service/VERSION
git commit -m "chore(ems): bump version to 1.2.3"
git push origin main

# Workflow auto-triggers and builds/pushes
```

### Tag Resolution Priority

1. **Provided tag** (`inputs.version` from workflow dispatch)
2. **VERSION file** (if exists at `service_path/VERSION`)
3. **Git SHA** (fallback)

## Security Features

### Trivy Vulnerability Scanning

All pushed images are scanned for CRITICAL and HIGH severity vulnerabilities:

```yaml
- uses: aquasecurity/trivy-action@master
  with:
    format: 'sarif'
    severity: 'CRITICAL,HIGH'
```

Results uploaded to GitHub Security tab via SARIF format.

### Authentication

Uses `GITHUB_TOKEN` (automatically provided). Requires permissions:

```yaml
permissions:
  contents: read
  packages: write
```

### Concurrency Control

Prevents overlapping builds of the same service:

```yaml
concurrency:
  group: docker-${{ github.ref }}-${{ inputs.image_name }}
  cancel-in-progress: true
```

## Logging & Traceability

The workflow provides comprehensive logging at each stage:

```
📋 Workflow Inputs:
  service_path: ./services/expense-manager-service
  image_name: expense-manager-service
  tag: 1.2.0
  push: true

🔖 Using VERSION file: 1.2.0
📤 Image: ghcr.io/owner/expense-manager-service:1.2.0
💾 Cache scope: expense-manager-service

✅ Build Complete
📦 Image: ghcr.io/owner/expense-manager-service:1.2.0
🔐 Digest: sha256:abc123...
🏷️  Labels:
  org.opencontainers.image.title=expense-manager-service
  org.opencontainers.image.version=1.2.0
```

## Troubleshooting

### Issue: Workflow not triggering on VERSION change

**Check:** Ensure you're pushing to `main` branch, not a feature branch.

### Issue: Image not appearing in GHCR

**Check:** Verify `packages: write` permission is granted to the workflow.

### Issue: Cache not working between builds

**Check:** Ensure same `image_name` is passed consistently. Cache is scoped per image name.

### Issue: Trivy scan failing

**Check:** Image may have CRITICAL vulnerabilities. Check GitHub Security tab for SARIF report.

## Future Considerations

| Feature | Status | Decision |
|---------|--------|----------|
| Multi-arch (ARM64) | Ready | QEMU configured, add `linux/arm64` to platforms |
| SHA-pinned actions | Optional | Consider if supply-chain security becomes priority |
| PR builds | Disabled | Re-enable if pre-merge testing becomes essential |
| Provenance/SBOM | Disabled | Re-enable for enterprise compliance |

## Migration Guide

### Adding a New Service

1. Create `service-name/VERSION` file with initial version
2. Create `.github/workflows/build-service-name.yml`:

```yaml
name: Build Service Name

on:
  workflow_dispatch:
    inputs:
      version:
        description: "Image tag (leave empty to use VERSION file)"
        required: false
        type: string
  push:
    branches:
      - main
    paths:
      - "path/to/service/VERSION"

jobs:
  build:
    uses: ./.github/workflows/reusable-docker-build.yml
    permissions:
      contents: read
      packages: write
    with:
      service_path: ./path/to/service
      image_name: service-name
      tag: ${{ inputs.version }}
      image_description: "Service Name - Brief description"
```
