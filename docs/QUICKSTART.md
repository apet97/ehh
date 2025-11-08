# Clankerbot Quick Start Guide

Get Clankerbot running in under 5 minutes with this comprehensive quick start guide.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [Docker Compose (Recommended)](#docker-compose-recommended)
  - [Local Development](#local-development)
  - [Docker](#docker)
  - [Kubernetes](#kubernetes)
- [Configuration](#configuration)
- [Verify Installation](#verify-installation)
- [Testing](#testing)
  - [Smoke Tests](#smoke-tests)
  - [Postman Collection](#postman-collection)
  - [REST Client (VS Code)](#rest-client-vs-code)
  - [Manual UI](#manual-ui)
- [First API Calls](#first-api-calls)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## Prerequisites

### Required
- **Clockify API credentials** (at least one):
  - User API key (get from Clockify Settings → API), OR
  - Addon token (for Clockify addons)

### Optional
- **DeepSeek API key** (for LLM-based natural language parsing)
  - Sign up at [platform.deepseek.com](https://platform.deepseek.com/)
  - Free tier available

### For Installation

#### Docker Compose (Recommended)
- Docker 20.10+ and Docker Compose v2
- 512MB RAM minimum
- Internet access for image downloads

#### Local Development
- Python 3.11+
- pip 23+
- 512MB RAM minimum

#### Kubernetes
- Kubernetes cluster 1.24+
- kubectl configured
- Helm 3.10+ (for Helm chart)

## Pull from GitHub Container Registry

Clankerbot images are published to GitHub Container Registry (GHCR) for all releases.

**Latest stable release:**
```bash
docker pull ghcr.io/your-org/clankerbot:latest
```

**Specific version:**
```bash
docker pull ghcr.io/your-org/clankerbot:0.2.1
```

**Run directly from GHCR:**
```bash
docker run -d \
  --name clankerbot \
  -p 8000:8000 \
  -e CLOCKIFY_API_KEY=your_api_key \
  -e DEEPSEEK_API_KEY=your_deepseek_key \
  ghcr.io/your-org/clankerbot:latest
```

**Available tags:**
- `latest` - Latest stable release
- `0.2.1`, `0.2.0` - Specific version tags
- `main` - Latest commit from main branch (not recommended for production)

**Image verification:**

All images are signed with Cosign and include SBOM attestations:

```bash
# Verify signature
cosign verify ghcr.io/your-org/clankerbot:latest \
  --certificate-identity-regexp "https://github.com/your-org/clankerbot" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com"

# View SBOM
cosign download attestation ghcr.io/your-org/clankerbot:latest | \
  jq -r '.payload' | base64 -d | jq .
```

## Installation Methods

### Docker Compose (Recommended)

Best for: Quick testing, development, small deployments

```bash
# 1. Clone repository
git clone https://github.com/your-org/clankerbot.git
cd clankerbot

# 2. Create environment file
cp .env.example .env

# 3. Edit .env with your credentials
nano .env  # or vim, code, etc.

# Required: Add at least one Clockify credential
# CLOCKIFY_API_KEY=your_clockify_api_key_here
# OR
# CLOCKIFY_ADDON_TOKEN=your_addon_token_here

# Optional: Add DeepSeek API key for LLM parsing
# DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 4. Start service
docker compose up -d

# 5. View logs (optional)
docker compose logs -f

# 6. Verify health
curl http://localhost:8000/healthz
# Expected: {"ok":true,"data":{"status":"healthy"},"requestId":"..."}

curl http://localhost:8000/readyz
# Expected: {"ok":true,"data":{"ready":true,"checks":{...}},"requestId":"..."}
```

**Stop service:**
```bash
docker compose down
```

**Update to latest version:**
```bash
docker compose pull
docker compose up -d
```

### Local Development

Best for: Active development, debugging, testing changes

```bash
# 1. Clone repository
git clone https://github.com/your-org/clankerbot.git
cd clankerbot

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create environment file
cp .env.example .env
nano .env  # Add your API keys

# 5. Run development server
uvicorn app.main:app --reload --port 8000

# The --reload flag enables auto-reload on code changes
# Server will start at http://localhost:8000

# 6. In another terminal, verify health
curl http://localhost:8000/healthz
```

**Stop server:**
Press `Ctrl+C` in terminal

**Run tests:**
```bash
pytest -v
```

### Docker

Best for: Production single-host deployment, custom orchestration

```bash
# 1. Build image
docker build -t clankerbot:latest .

# 2. Run container
docker run -d \
  --name clankerbot \
  -p 8000:8000 \
  -e CLOCKIFY_API_KEY=your_api_key \
  -e DEEPSEEK_API_KEY=your_deepseek_key \
  -e RATE_LIMIT_PER_MINUTE=60 \
  --restart unless-stopped \
  clankerbot:latest

# 3. View logs
docker logs -f clankerbot

# 4. Verify health
curl http://localhost:8000/healthz
```

**Using environment file:**
```bash
docker run -d \
  --name clankerbot \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  clankerbot:latest
```

**Stop container:**
```bash
docker stop clankerbot
docker rm clankerbot
```

### Kubernetes

Best for: Production multi-host deployment, high availability

#### Option 1: kubectl (Raw Manifests)

```bash
# 1. Create namespace (optional)
kubectl create namespace clankerbot

# 2. Create secret with API keys
kubectl create secret generic clankerbot-secrets \
  --from-literal=clockify-api-key=your_clockify_key \
  --from-literal=deepseek-api-key=your_deepseek_key \
  -n clankerbot

# 3. Apply manifests
kubectl apply -f deploy/k8s/ -n clankerbot

# 4. Verify deployment
kubectl get pods -n clankerbot
kubectl get svc -n clankerbot

# 5. Port-forward to test locally (optional)
kubectl port-forward -n clankerbot svc/clankerbot 8000:8000

# 6. Verify health
curl http://localhost:8000/healthz
```

#### Option 2: Helm Chart

```bash
# 1. Create namespace
kubectl create namespace clankerbot

# 2. Install chart from GHCR
helm install clankerbot ./deploy/helm/clankerbot \
  --namespace clankerbot \
  --set image.repository=ghcr.io/your-org/clankerbot \
  --set image.tag=0.2.1 \
  --set secrets.clockifyApiKey=your_clockify_key \
  --set secrets.deepseekApiKey=your_deepseek_key

# 3. Verify installation
helm status clankerbot -n clankerbot
kubectl get pods -n clankerbot

# 4. Port-forward to test
kubectl port-forward -n clankerbot svc/clankerbot 8000:8000

# 5. Verify health
curl http://localhost:8000/healthz
```

##### Helm Values Reference

Common configuration options (see `deploy/helm/clankerbot/values.yaml` for full reference):

**Image Configuration:**
```yaml
image:
  repository: ghcr.io/your-org/clankerbot
  pullPolicy: IfNotPresent
  tag: "0.2.1"
```

**Replica and Scaling:**
```yaml
replicaCount: 3

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

**Resources:**
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**High Availability:**
```yaml
podDisruptionBudget:
  enabled: true
  minAvailable: 1

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: clankerbot
          topologyKey: kubernetes.io/hostname
```

**Ingress:**
```yaml
ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: clankerbot.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: clankerbot-tls
      hosts:
        - clankerbot.example.com
```

**Security:**
```yaml
secrets:
  clockifyApiKey: "your_clockify_key"
  deepseekApiKey: "your_deepseek_key"
  webhookSharedSecret: "generate_with_openssl_rand_hex_32"

env:
  RATE_LIMIT_PER_MINUTE: "120"
  RATE_LIMIT_BURST: "50"
  MAX_REQUEST_SIZE_MB: "2"
  WEBHOOK_IP_ALLOWLIST: "192.168.1.0/24,10.0.0.0/8"
```

**Observability:**
```yaml
env:
  LOG_JSON: "true"
  METRICS_ENABLED: "true"
  OTEL_EXPORTER_OTLP_ENDPOINT: "http://otel-collector:4318"

serviceMonitor:
  enabled: true
  interval: 30s
```

**Full values file location:**
```
deploy/helm/clankerbot/values.yaml
```

View with:
```bash
cat deploy/helm/clankerbot/values.yaml
```

**Custom values file (production):**
```bash
# Create production-values.yaml
cat > production-values.yaml <<EOF
replicaCount: 3

resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "500m"

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: clankerbot.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: clankerbot-tls
      hosts:
        - clankerbot.example.com

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
EOF

# Install with custom values
helm install clankerbot ./deploy/helm/clankerbot \
  -f production-values.yaml \
  --set secrets.clockifyApiKey=your_key \
  --set secrets.deepseekApiKey=your_key
```

**Upgrade:**
```bash
helm upgrade clankerbot ./deploy/helm/clankerbot \
  -f production-values.yaml
```

**Uninstall:**
```bash
helm uninstall clankerbot -n clankerbot
```

## Configuration

### Minimum Required Configuration

```bash
# .env file - Minimum viable configuration

# Clockify (at least one required)
CLOCKIFY_API_KEY=your_clockify_api_key
# OR
# CLOCKIFY_ADDON_TOKEN=your_addon_token
```

### Recommended Production Configuration

```bash
# .env file - Production configuration

# === Clockify ===
CLOCKIFY_API_KEY=your_clockify_api_key
CLOCKIFY_BASE_URL=https://api.clockify.me/api

# === LLM (Optional but recommended) ===
DEEPSEEK_API_KEY=your_deepseek_api_key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# === Security ===
WEBHOOK_SHARED_SECRET=randomly_generated_secret_at_least_32_chars
RATE_LIMIT_PER_MINUTE=120

# === Server ===
CORS_ORIGINS=https://app.example.com,https://admin.example.com

# === Observability ===
LOG_JSON=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
```

### Generate Secure Secrets

```bash
# Generate webhook secret
openssl rand -hex 32

# Or use Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Verify Installation

Run these checks to ensure Clankerbot is working correctly:

### 1. Health Check
```bash
curl http://localhost:8000/healthz

# Expected response:
# {
#   "ok": true,
#   "data": {"status": "healthy"},
#   "requestId": "01JCEXAMPLE123"
# }
```

### 2. Readiness Check
```bash
curl http://localhost:8000/readyz

# Expected response:
# {
#   "ok": true,
#   "data": {
#     "ready": true,
#     "checks": {
#       "llm": "configured",       # or "missing" if no DEEPSEEK_API_KEY
#       "clockify": "configured"   # or "missing" if no Clockify credentials
#     }
#   },
#   "requestId": "01JCEXAMPLE456"
# }
```

### 3. Parse Action (Rule-based)
```bash
curl -X POST http://localhost:8000/actions/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "clockify.get_user"}'

# Expected response:
# {
#   "ok": true,
#   "data": {
#     "integration": "clockify",
#     "operation": "get_user",
#     "params": {},
#     "parser": "rule"
#   },
#   "requestId": "01JCEXAMPLE789"
# }
```

### 4. Parse Action (LLM-based, if configured)
```bash
curl -X POST "http://localhost:8000/actions/parse?llm=true" \
  -H "Content-Type: application/json" \
  -d '{"text": "Get my Clockify user information"}'

# Expected response:
# {
#   "ok": true,
#   "data": {
#     "integration": "clockify",
#     "operation": "get_user",
#     "params": {},
#     "parser": "llm"           # or "fallback" if LLM parsing failed
#   },
#   "requestId": "01JCEXAMPLEABC"
# }
```

### 5. Execute Action
```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "get_user",
    "params": {}
  }'

# Expected response:
# {
#   "ok": true,
#   "id": "user123abc",
#   "email": "you@example.com",
#   "name": "Your Name",
#   "activeWorkspace": "workspace123",
#   ...
# }
```

## Testing

### Smoke Tests

Run automated smoke tests to verify all endpoints:

```bash
# Using the provided script
bash scripts/smoke_test.sh

# Expected output:
# ✓ Health check passed
# ✓ Readiness check passed
# ✓ Parser (rule-based) passed
# ✓ Parser (LLM) passed
# ✓ Action execution passed
# ✓ Webhook endpoint passed
#
# All smoke tests passed!
```

**Exit codes:**
- `0` - All tests passed
- `1` - One or more tests failed

### Postman Collection

Use the pre-configured Postman collection for interactive API testing:

1. **Import collection:**
   - Open Postman
   - Click "Import"
   - Select `postman/clankerbot.postman_collection.json`
   - Select `postman/clankerbot.postman_environment.json`

2. **Configure environment:**
   - Set `base_url` to `http://localhost:8000`
   - Set `clockify_workspace_id` to your workspace ID
   - Optionally set `webhook_secret` if configured

3. **Run requests:**
   - Health → healthz
   - Health → readyz
   - Parser → Parse (rule-based)
   - Parser → Parse (LLM)
   - Actions → Get User
   - Actions → List Workspaces
   - Webhooks → Send Test Webhook

### REST Client (VS Code)

If using VS Code with REST Client extension:

1. **Open HTTP files:**
   - `http/health.http`
   - `http/actions.http`
   - `http/webhooks.http`

2. **Configure variables:**
   - Edit `@host` if not using `localhost:8000`
   - Edit `@workspaceId` with your Clockify workspace ID

3. **Send requests:**
   - Click "Send Request" above any request
   - View response in split pane

### Manual UI

Use the standalone HTML interface for visual API testing:

1. **Open in browser:**
   ```bash
   # If running with Docker Compose or Kubernetes with static files mounted
   open http://localhost:8000/tools/manual.html

   # Or open the file directly
   open tools/manual.html
   ```

2. **Update base URL:**
   - If not using `localhost:8000`, update the API URL in each section

3. **Test features:**
   - **Parser section**: Enter text and click "Parse"
   - **Action Runner section**: Fill in fields and click "Run Action"
   - **Webhook Sender section**: Paste JSON payload and click "Send Webhook"

## First API Calls

### Get Your User Info

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "get_user",
    "params": {}
  }'
```

### List Your Workspaces

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "list_workspaces",
    "params": {}
  }'
```

### Get a Specific Workspace

```bash
# Replace WORKSPACE_ID with your workspace ID from list_workspaces
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "get_workspace",
    "params": {
      "workspaceId": "WORKSPACE_ID"
    }
  }'
```

### Create a Client

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "create_client",
    "params": {
      "workspaceId": "WORKSPACE_ID",
      "body": {
        "name": "My New Client",
        "archived": false
      }
    }
  }'
```

### List Projects

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "list_projects",
    "params": {
      "workspaceId": "WORKSPACE_ID"
    }
  }'
```

### Create a Project

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "create_project",
    "params": {
      "workspaceId": "WORKSPACE_ID",
      "body": {
        "name": "My New Project",
        "clientId": "CLIENT_ID",
        "isPublic": false,
        "color": "#FF5733"
      }
    }
  }'
```

### Create a Time Entry

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "create_time_entry",
    "params": {
      "workspaceId": "WORKSPACE_ID",
      "body": {
        "start": "2024-01-15T10:00:00Z",
        "end": "2024-01-15T12:00:00Z",
        "description": "Working on API integration",
        "projectId": "PROJECT_ID",
        "billable": true
      }
    }
  }'
```

## Troubleshooting

### Service Won't Start

**Symptoms:** Container/process exits immediately

**Checks:**
1. Check logs:
   ```bash
   # Docker Compose
   docker compose logs clankerbot

   # Docker
   docker logs clankerbot

   # Local
   # Check terminal output
   ```

2. Verify environment variables:
   ```bash
   # Check .env file exists
   cat .env

   # Verify at least one Clockify credential is set
   grep CLOCKIFY .env
   ```

3. Test minimal configuration:
   ```bash
   # Temporarily use test credentials
   export CLOCKIFY_API_KEY=test_key
   uvicorn app.main:app --port 8000
   ```

### Health Check Fails

**Symptoms:** `/healthz` returns 503 or connection refused

**Checks:**
1. Verify service is running:
   ```bash
   # Docker Compose
   docker compose ps

   # Docker
   docker ps | grep clankerbot
   ```

2. Check if port is accessible:
   ```bash
   # Test if port 8000 is listening
   netstat -an | grep 8000
   # or
   lsof -i :8000
   ```

3. Check firewall:
   ```bash
   # Linux
   sudo ufw status

   # macOS
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
   ```

### Readiness Check Shows "missing"

**Symptoms:** `/readyz` shows `"llm": "missing"` or `"clockify": "missing"`

**Cause:** API keys not configured

**Fix:**
```bash
# Add missing API keys to .env
echo "DEEPSEEK_API_KEY=your_key_here" >> .env
echo "CLOCKIFY_API_KEY=your_key_here" >> .env

# Restart service
docker compose restart
```

### LLM Parsing Always Falls Back

**Symptoms:** Parser always returns `"parser": "fallback"` even with `llm=true`

**Checks:**
1. Verify DeepSeek API key is configured:
   ```bash
   curl http://localhost:8000/readyz | jq '.data.checks.llm'
   # Should return: "configured"
   ```

2. Check logs for LLM errors:
   ```bash
   docker compose logs clankerbot | grep -i "llm"
   ```

3. Test DeepSeek API key directly:
   ```bash
   curl https://api.deepseek.com/chat/completions \
     -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "deepseek-chat",
       "messages": [{"role": "user", "content": "Hello"}]
     }'
   ```

### Actions Return "unauthorized"

**Symptoms:** `/actions/run` returns error code `"unauthorized"`

**Cause:** Invalid or missing Clockify API key

**Fix:**
1. Verify API key in Clockify:
   - Go to Clockify → Settings → API
   - Copy API key

2. Test API key directly:
   ```bash
   curl https://api.clockify.me/api/v1/user \
     -H "X-Api-Key: $CLOCKIFY_API_KEY"
   ```

3. Update .env and restart:
   ```bash
   # Update .env with valid key
   nano .env

   # Restart service
   docker compose restart
   ```

### Webhook Returns 401

**Symptoms:** POST to `/webhooks/clockify` returns 401 Unauthorized

**Cause:** Webhook secret mismatch

**Fix:**
```bash
# If secret is configured, include it in requests
curl -X POST http://localhost:8000/webhooks/clockify \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your_secret_from_env" \
  -d '{...}'

# Or disable secret validation (development only)
# Remove WEBHOOK_SHARED_SECRET from .env and restart
```

### Rate Limited (429 Errors)

**Symptoms:** Frequent 429 responses with error code `"rate_limited"`

**Fix:**
```bash
# Increase rate limit in .env
echo "RATE_LIMIT_PER_MINUTE=120" >> .env

# Restart service
docker compose restart
```

### Port 8000 Already in Use

**Symptoms:** "Address already in use" error

**Fix:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process (replace PID)
kill -9 PID

# Or use different port
docker compose run -p 8080:8000 clankerbot
# Then access at http://localhost:8080
```

### Docker Compose Won't Start

**Symptoms:** `docker compose up` fails

**Checks:**
1. Verify Docker Compose version:
   ```bash
   docker compose version
   # Should be v2.x or higher
   ```

2. Check Docker daemon:
   ```bash
   docker ps
   # If fails, start Docker daemon
   ```

3. Validate compose.yaml syntax:
   ```bash
   docker compose config
   # Should output valid YAML
   ```

## Next Steps

### Production Deployment

1. **Review security settings:**
   - Set WEBHOOK_SHARED_SECRET
   - Configure CORS_ORIGINS
   - Adjust RATE_LIMIT_PER_MINUTE
   - Enable LOG_JSON=true

2. **Set up monitoring:**
   - Configure OTEL_EXPORTER_OTLP_ENDPOINT for traces
   - Monitor /healthz and /readyz endpoints
   - Set up alerting on error rates

3. **Deploy to Kubernetes:**
   - Use Helm chart with production values
   - Enable HPA for auto-scaling
   - Configure Ingress with TLS

4. **Set up CI/CD:**
   - Review `.github/workflows/ci.yml`
   - Add deployment pipeline
   - Enable secrets scanning

### Development

1. **Read architecture docs:**
   - See `docs/ARCH.md` for system design
   - See `docs/RUNBOOK.md` for operations

2. **Run tests:**
   ```bash
   pytest -v --cov=app
   ```

3. **Add new integration:**
   - See `app/integrations/clockify.py` as example
   - Implement `Integration` interface
   - Register with `@register_integration`

4. **Code quality:**
   ```bash
   # Lint
   ruff check app/ tests/

   # Format
   black app/ tests/
   ```

### Learn More

- **API Documentation:** See README.md for full API reference
- **Operations Guide:** See docs/RUNBOOK.md for production operations
- **Architecture:** See docs/ARCH.md for system design
- **Changelog:** See docs/CHANGELOG.md for release notes

### Get Help

- **Issues:** https://github.com/your-org/clankerbot/issues
- **Clockify API Docs:** https://clockify.me/developers-api
- **DeepSeek API Docs:** https://platform.deepseek.com/

---

**Happy automating with Clankerbot!**
