# Clankerbot v0.2.0 - Enterprise Release 🚀

We're excited to announce **Clankerbot v0.2.0**, a complete transformation into an enterprise-grade automation service with first-class Clockify integration!

## 🎯 What's New

### Enterprise Reliability
- ✅ **LLM Parser with Fallback**: Natural language to actions via DeepSeek, with automatic fallback
- ✅ **Robust Clockify Client**: Fully typed async client with retry logic and error mapping
- ✅ **Webhook Idempotency**: Duplicate detection via LRU cache and event IDs
- ✅ **Rate Limiting**: Token bucket middleware (60 req/min default)
- ✅ **Request Tracing**: ULID-based IDs in all logs and responses
- ✅ **Health Endpoints**: `/healthz` and `/readyz` for liveness/readiness probes

### Developer Experience
- 📦 **One-command Smoke Tests**: `./scripts/smoke.sh`
- 📮 **Postman Collection**: Import and start testing immediately
- 🌐 **Manual Web UI**: Test API from browser at `/tools/manual.html`
- 📖 **Comprehensive Docs**: Quickstart, Architecture, Runbook
- 🧪 **Full Test Coverage**: Unit, integration, and smoke tests

### Production Ready
- 🐳 **Multi-arch Docker**: Supports amd64 and arm64
- ☸️  **Kubernetes Ready**: Deployment files and Helm chart included
- 🔒 **Secret Scanning**: Gitleaks integration in CI
- 📊 **JSON Logging**: Structured logs with OpenTelemetry support
- 🔐 **Security**: Webhook secrets, rate limiting, non-root container

## 📥 Quick Start

```bash
# Clone and configure
git clone https://github.com/apet97/ehh.git clankerbot
cd clankerbot
echo "CLOCKIFY_API_KEY=your_key_here" > .env

# Start with Docker Compose
docker compose up -d

# Run smoke tests
./scripts/smoke.sh
```

## 🧪 Testing

### Smoke Tests
```bash
./scripts/smoke.sh http://localhost:8000
```

### Postman
1. Import `postman/Clankerbot.postman_collection.json`
2. Set `baseUrl` variable to `http://localhost:8000`
3. Run requests

### Web UI
Open http://localhost:8000/tools/manual.html in your browser

## 🔧 Configuration

### Minimal (Required)
```bash
CLOCKIFY_API_KEY=your_key_here
```

### Recommended for Production
```bash
CLOCKIFY_API_KEY=your_key_here
WEBHOOK_SHARED_SECRET=$(openssl rand -hex 32)
RATE_LIMIT_PER_MINUTE=120
LOG_JSON=true
```

See [.env.example](.env.example) for all options.

## 📚 Documentation

- [Quickstart Guide](docs/QUICKSTART.md) - Get running in 5 minutes
- [Architecture](docs/ARCH.md) - System design and failure modes
- [Runbook](docs/RUNBOOK.md) - Operations and troubleshooting
- [Changelog](docs/CHANGELOG.md) - All changes in v0.2.0

## 🔄 Upgrading from v0.1.0

All existing endpoints remain backward compatible. New features are opt-in via environment variables.

**Migration steps:**
1. Pull latest code
2. Update `.env` with new optional variables (see `.env.example`)
3. Restart service
4. Run smoke tests to verify

## 🐳 Docker

```bash
# Build
docker build -t clankerbot:0.2.0 .

# Run
docker run -d -p 8000:8000 \
  -e CLOCKIFY_API_KEY=your_key \
  clankerbot:0.2.0
```

## ☸️ Kubernetes

```bash
# Using kubectl
kubectl apply -f deploy/k8s/

# Using Helm
helm install clankerbot deploy/helm/clankerbot/ \
  --set env.CLOCKIFY_API_KEY=your_key
```

## 🧰 API Endpoints

### Health
- `GET /healthz` - Liveness probe
- `GET /readyz` - Readiness probe with dependency checks

### Actions
- `POST /actions/parse` - Parse actions (rule-based or LLM)
- `POST /actions/run` - Execute actions

### Webhooks
- `POST /webhooks/clockify` - Receive Clockify webhooks (with idempotency)

### Tools
- `GET /tools/manual.html` - Manual testing UI

## ✨ Clockify Operations

- `get_user` - Get current user
- `list_workspaces` - List all workspaces
- `list_clients` - List clients in workspace
- `create_client` - Create new client
- `list_projects` - List projects in workspace
- `create_project` - Create new project
- `create_time_entry` - Create time entry

See [README.md](README.md) for full API documentation.

## 🙏 Contributors

This release was made possible by enterprise requirements for production-grade automation.

## 📝 Full Changelog

See [CHANGELOG.md](docs/CHANGELOG.md) for complete details.

## 🐛 Known Issues

None at this time. Report issues at https://github.com/apet97/ehh/issues

---

**Installation**: See [Quickstart Guide](docs/QUICKSTART.md)
**Upgrading**: All changes are backward compatible
**Support**: https://github.com/apet97/ehh/issues
