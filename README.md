# Clankerbot

Enterprise-grade automation service that executes the pipeline: **User input (HTTP) → Optional LLM parsing (DeepSeek) → Action (Clockify API call) → Webhook handling**.

## Features

### Core Pipeline
- **Rule-based parser**: Fast, deterministic action parsing (`integration.operation param=value`)
- **LLM parser**: Natural language to action via DeepSeek, with automatic fallback to rule parser
- **Clockify integration**: First-class support with typed async client
- **Webhook receiver**: Idempotent handling of Clockify webhooks with secret validation

### Enterprise Reliability
- **Timeout & retry**: 20s timeouts, 3 retries with exponential backoff on 429/5xx
- **Error mapping**: Structured errors (unauthorized, validation_error, rate_limited, upstream_error)
- **Request tracing**: ULID-based request IDs in all logs and responses
- **Rate limiting**: Token bucket per IP+path (default 60/min)

### Observability
- **Structured logging**: JSON logs (LOG_JSON=true) with request_id, path, status, duration_ms
- **Health endpoints**: `/healthz` (liveness), `/readyz` (dependency checks)
- **OpenTelemetry ready**: Optional OTLP export (feature flag)

### Security
- **Secret management**: Env-only, never hardcoded
- **Webhook validation**: Optional shared secret (WEBHOOK_SHARED_SECRET)
- **Non-root container**: Runs as user `clankerbot` (UID 1000)
- **Input validation**: Pydantic models for all requests
- **CORS**: Configurable origins

## Quick Start

### Docker Compose (Recommended)

```bash
# 1. Clone and configure
git clone <repo-url> clankerbot
cd clankerbot
cp .env.example .env
# Edit .env with your API keys

# 2. Start service
docker compose up -d

# 3. Verify health
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
uvicorn app.main:app --reload --port 8000
```

## Environment Variables

### Required

```bash
# Clockify (at least one)
CLOCKIFY_API_KEY=sk_xxx              # User API key
# OR
CLOCKIFY_ADDON_TOKEN=addon_xxx       # Addon token
```

### Optional

```bash
# LLM (required for llm=true parsing)
DEEPSEEK_API_KEY=sk_xxx
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# Security
WEBHOOK_SHARED_SECRET=my_secret      # Enable webhook authentication
RATE_LIMIT_PER_MINUTE=60             # Default: 60

# Observability
LOG_JSON=true                        # Enable JSON logging
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318

# Server
CORS_ORIGINS=http://localhost:3000   # Comma-separated
```

## API Endpoints

### Health

```bash
# Liveness
curl http://localhost:8000/healthz
# Response: {"ok": true, "data": {"status": "healthy"}, "requestId": "..."}

# Readiness
curl http://localhost:8000/readyz
# Response: {"ok": true, "data": {"ready": true, "checks": {"llm": "configured", "clockify": "configured"}}, "requestId": "..."}
```

### Parse Actions

```bash
# Rule-based parsing
curl -X POST http://localhost:8000/actions/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "clockify.get_user"}'
# Response: {"ok": true, "data": {"integration": "clockify", "operation": "get_user", "params": {}, "parser": "rule"}, "requestId": "..."}

# LLM parsing (with fallback)
curl -X POST "http://localhost:8000/actions/parse?llm=true" \
  -H "Content-Type: application/json" \
  -d '{"text": "Get my Clockify user info"}'
# Response: {"ok": true, "data": {"integration": "clockify", "operation": "get_user", "params": {}, "parser": "llm"}, "requestId": "..."}
# On LLM failure: parser="fallback"
```

### Run Actions

```bash
# Get user
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{"integration": "clockify", "operation": "get_user", "params": {}}'
# Response: {"ok": true, "id": "user123", "email": "you@example.com", ...}

# List workspaces
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{"integration": "clockify", "operation": "list_workspaces", "params": {}}'
# Response: {"ok": true, "workspaces": [...]}

# Create client
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "create_client",
    "params": {
      "workspaceId": "your_workspace_id",
      "body": {"name": "New Client", "archived": false}
    }
  }'
```

### Webhooks

```bash
# Clockify webhook (with secret)
curl -X POST http://localhost:8000/webhooks/clockify \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your_secret" \
  -H "X-Clockify-Event-Id: evt_12345" \
  -d '{
    "id": "entry123",
    "userId": "user123",
    "workspaceId": "ws123",
    "timeInterval": {
      "start": "2024-01-01T10:00:00Z",
      "end": "2024-01-01T11:00:00Z"
    }
  }'
# Response: {"ok": true, "data": {"received": true, "duplicate": false, "event": {...}}, "requestId": "..."}

# Duplicate detection
# Repeat same request with same X-Clockify-Event-Id:
# Response: {"ok": true, "data": {"received": true, "duplicate": true, ...}, "requestId": "..."}
```

## Supported Clockify Operations

| Operation | Description | Params |
|-----------|-------------|--------|
| get_user | Get current user | - |
| list_workspaces | List all workspaces | - |
| get_workspace | Get workspace by ID | workspaceId |
| create_client | Create client | workspaceId, body: {name, archived?} |
| list_clients | List clients | workspaceId |
| create_time_entry | Create time entry | workspaceId, body: {start, end?, description?, projectId?, ...} |

## Testing

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
pytest -v

# With coverage
pytest -v --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_clockify_client.py -v
```

## Architecture

See [docs/ARCH.md](docs/ARCH.md) for detailed architecture documentation.

**High-level pipeline:**

```
User → FastAPI → [LLM Parser → Fallback] → Integration → Clockify API
                       ↓
              Structured Response
```

**Key components:**
- **Middleware**: Request ID, rate limiting, CORS, logging
- **Parsers**: LLM (DeepSeek) with fallback to rule-based
- **Integrations**: Pluggable (Clockify, Slack, extensible)
- **Clockify Client**: Typed async client with retry logic
- **Webhook Router**: Idempotency via LRU cache

## Operations

See [docs/RUNBOOK.md](docs/RUNBOOK.md) for operations guide.

**Common tasks:**
- Rotating API keys
- Adjusting rate limits
- Handling 429 errors
- Webhook setup
- Monitoring and troubleshooting

## Development

### Project Structure

```
clankerbot/
├── app/
│   ├── main.py              # FastAPI app, middleware
│   ├── actions.py           # Action parsers (rule, LLM)
│   ├── llm.py               # LLM client (DeepSeek)
│   ├── models.py            # Pydantic models, API envelopes
│   ├── config.py            # Settings
│   ├── scheduler.py         # APScheduler for cron jobs
│   ├── utils/
│   │   ├── http.py          # HTTP client factory
│   │   ├── ids.py           # Request ID generation
│   │   └── logging.py       # Logging configuration
│   ├── middleware/
│   │   └── ratelimit.py     # Rate limiting middleware
│   ├── integrations/
│   │   ├── base.py          # Integration interface
│   │   ├── clockify.py      # Clockify integration
│   │   ├── clockify_client.py    # Async Clockify client
│   │   ├── clockify_types.py     # Pydantic models for Clockify
│   │   ├── clockify_openapi.json # Clockify API spec
│   │   └── slack.py         # Slack integration
│   └── routes/
│       ├── actions.py       # Action endpoints
│       └── webhooks_clockify.py  # Clockify webhook endpoint
├── tests/
│   ├── test_actions.py
│   ├── test_clockify_client.py
│   ├── test_webhooks.py
│   └── test_ratelimit.py
├── docs/
│   ├── ARCH.md              # Architecture documentation
│   └── RUNBOOK.md           # Operations runbook
├── .github/workflows/
│   └── ci.yml               # CI pipeline (lint, test, build)
├── Dockerfile               # Multi-stage production build
├── compose.yaml             # Docker Compose config
├── requirements.txt
└── README.md
```

### Adding a New Integration

1. Create `app/integrations/your_integration.py`
2. Implement `Integration` interface from `base.py`
3. Register with `@register_integration("name")` decorator
4. Import in `app/main.py` to populate registry

See `app/integrations/clockify.py` for reference.

### Code Quality

```bash
# Lint
ruff check app/ tests/

# Format
black app/ tests/

# Type check (optional, add mypy to requirements)
mypy app/
```

## Security Notes

1. **Never commit secrets**: Use `.env` (gitignored)
2. **Webhook secrets**: Set WEBHOOK_SHARED_SECRET in production
3. **Rate limiting**: Adjust per your threat model
4. **TLS**: Terminate TLS at reverse proxy (nginx, Cloudflare, etc.)
5. **Principle of least privilege**: Use Clockify addon tokens with minimal scopes when possible

## License

MIT License - see LICENSE file

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/my-feature`)
3. Commit changes with clear messages
4. Add tests for new functionality
5. Ensure CI passes (`ruff`, `black`, `pytest`)
6. Create pull request

## Support

- **Documentation**: See `docs/` directory
- **Issues**: https://github.com/your-org/clankerbot/issues
- **Clockify API**: https://clockify.me/developers-api
- **DeepSeek API**: https://platform.deepseek.com/
