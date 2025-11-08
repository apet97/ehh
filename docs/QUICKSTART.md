# Clankerbot Quickstart

Get Clankerbot running in under 5 minutes.

## Prerequisites

- Docker & Docker Compose (recommended)
- OR Python 3.11+ (for local development)
- Clockify API key (get from https://app.clockify.me/user/settings)

## Quick Start with Docker Compose

### 1. Clone and Configure

```bash
git clone <repo-url> clankerbot
cd clankerbot

# Create .env file
cat > .env << 'EOF'
CLOCKIFY_API_KEY=your_clockify_api_key_here
EOF
```

### 2. Start the Service

```bash
docker compose up -d

# Check logs
docker compose logs -f
```

### 3. Verify It Works

```bash
# Run smoke tests
./scripts/smoke.sh

# Or test manually
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

**Expected output:**
```json
{
  "ok": true,
  "data": {"status": "healthy"},
  "requestId": "..."
}
```

## Local Development (Without Docker)

### 1. Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your CLOCKIFY_API_KEY
```

### 3. Run Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Verify

```bash
# In another terminal
./scripts/smoke.sh
```

## Testing the API

### Option 1: Smoke Test Script

```bash
./scripts/smoke.sh

# Against custom URL
./scripts/smoke.sh http://your-server.com
```

### Option 2: Postman

1. Open Postman
2. Import → File → `postman/Clankerbot.postman_collection.json`
3. Set environment variable `baseUrl` to `http://localhost:8000`
4. Run requests in the collection

### Option 3: VS Code REST Client

1. Install "REST Client" extension
2. Open `http/requests.http`
3. Click "Send Request" above any request

### Option 4: cURL

```bash
# Health check
curl http://localhost:8000/healthz

# Parse action (rule-based)
curl -X POST http://localhost:8000/actions/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "clockify.get_user"}'

# Parse action (LLM - requires DEEPSEEK_API_KEY)
curl -X POST "http://localhost:8000/actions/parse?llm=true" \
  -H "Content-Type: application/json" \
  -d '{"text": "Get my Clockify user info"}'

# Run action
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{"integration": "clockify", "operation": "get_user", "params": {}}'
```

## Common Operations

### Get Your Clockify User

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{"integration": "clockify", "operation": "get_user", "params": {}}'
```

### List Workspaces

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{"integration": "clockify", "operation": "list_workspaces", "params": {}}'
```

### Create a Client

```bash
# Replace YOUR_WORKSPACE_ID with actual workspace ID from list_workspaces
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "create_client",
    "params": {
      "workspaceId": "YOUR_WORKSPACE_ID",
      "body": {
        "name": "My New Client",
        "archived": false
      }
    }
  }'
```

## Optional: Enable LLM Parsing

LLM parsing converts natural language to actions but requires a DeepSeek API key.

### 1. Get API Key

Sign up at https://platform.deepseek.com/ and create an API key.

### 2. Add to .env

```bash
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
```

### 3. Restart Service

```bash
docker compose restart
```

### 4. Test LLM Parsing

```bash
curl -X POST "http://localhost:8000/actions/parse?llm=true" \
  -H "Content-Type: application/json" \
  -d '{"text": "Get my Clockify user information"}'

# Should return: "parser": "llm"
```

## Troubleshooting

### Service won't start

**Check logs:**
```bash
docker compose logs
```

**Common issues:**
- Port 8000 already in use: Change port in `compose.yaml`
- Invalid API key: Check `.env` file

### API returns "unauthorized"

**Cause:** Missing or invalid Clockify API key

**Fix:**
```bash
# Verify key is set
grep CLOCKIFY_API_KEY .env

# Test key manually
curl https://api.clockify.me/api/v1/user \
  -H "X-Api-Key: your_key_here"

# Update .env and restart
docker compose restart
```

### LLM always falls back to rule parser

**Cause:** Missing or invalid DeepSeek API key

**This is expected behavior** - the service works fine without LLM, just use rule-based format: `integration.operation param=value`

**To enable LLM:** Add `DEEPSEEK_API_KEY` to `.env` and restart.

### Smoke tests fail

**Run with verbose output:**
```bash
bash -x ./scripts/smoke.sh
```

**Check each endpoint individually:**
```bash
curl -v http://localhost:8000/healthz
curl -v http://localhost:8000/readyz
```

## Next Steps

- 📖 Read [README.md](../README.md) for full API documentation
- 🏗️ Check [docs/ARCH.md](./ARCH.md) for architecture details
- 🔧 See [docs/RUNBOOK.md](./RUNBOOK.md) for operations guide
- 🧪 Run tests: `pytest -v`
- 🐳 Build Docker image: `docker build -t clankerbot:latest .`

## Configuration Reference

### Minimal .env (Required)

```bash
CLOCKIFY_API_KEY=your_key_here
```

### Full .env (All Options)

```bash
# Clockify (required)
CLOCKIFY_API_KEY=your_key_here
CLOCKIFY_BASE_URL=https://api.clockify.me/api

# LLM (optional)
DEEPSEEK_API_KEY=your_deepseek_key_here
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# Security (optional)
WEBHOOK_SHARED_SECRET=your_webhook_secret
RATE_LIMIT_PER_MINUTE=60

# Observability (optional)
LOG_JSON=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318

# Server (optional)
CORS_ORIGINS=http://localhost:3000
```

See [.env.example](.env.example) for detailed comments.
