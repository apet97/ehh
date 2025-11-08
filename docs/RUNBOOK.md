# Clankerbot Runbook

Operations guide for running and maintaining Clankerbot in production.

## Deployment

### Docker Compose (Recommended)

```bash
# 1. Clone repository
git clone <repo-url> clankerbot
cd clankerbot

# 2. Create .env file
cp .env.example .env
# Edit .env with your credentials

# 3. Start service
docker compose up -d

# 4. Check health
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

### Docker

```bash
# Build
docker build -t clankerbot:latest .

# Run
docker run -d \
  -p 8000:8000 \
  -e CLOCKIFY_API_KEY=your_key \
  -e DEEPSEEK_API_KEY=your_key \
  --name clankerbot \
  clankerbot:latest
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export CLOCKIFY_API_KEY=your_key
export DEEPSEEK_API_KEY=your_key

# Run server
uvicorn app.main:app --reload --port 8000
```

## Configuration

### Required Environment Variables

```bash
# Clockify (at least one required)
CLOCKIFY_API_KEY=sk_xxx              # User API key
# OR
CLOCKIFY_ADDON_TOKEN=addon_xxx       # Addon token

# LLM (optional, required for llm=true parsing)
DEEPSEEK_API_KEY=sk_xxx
```

### Optional Environment Variables

```bash
# LLM Configuration
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# Clockify Configuration
CLOCKIFY_BASE_URL=https://api.clockify.me/api

# Security
WEBHOOK_SHARED_SECRET=my_secret_123   # Enable webhook authentication
RATE_LIMIT_PER_MINUTE=60              # Requests per minute per IP+path

# Observability
LOG_JSON=true                          # Enable JSON logging
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318

# Server
CORS_ORIGINS=http://localhost:3000,https://app.example.com
```

## Operations

### Rotating API Keys

#### Clockify API Key

```bash
# 1. Generate new key in Clockify web UI (Settings → API)
# 2. Update environment variable
#    Docker Compose: Edit .env, then:
docker compose down
docker compose up -d

#    Kubernetes: Update secret, rollout restart
kubectl create secret generic clankerbot-secrets \
  --from-literal=clockify-api-key=NEW_KEY \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl rollout restart deployment/clankerbot
```

#### DeepSeek API Key

Same procedure as Clockify, use DEEPSEEK_API_KEY

### Changing Rate Limits

```bash
# Update RATE_LIMIT_PER_MINUTE in .env
RATE_LIMIT_PER_MINUTE=120

# Restart service
docker compose restart
```

### Handling 429 Rate Limit Errors

#### From Clockify API

Clankerbot automatically retries 3 times with backoff. If still failing:

1. Check Clockify plan limits
2. Reduce request frequency
3. Contact Clockify support for higher limits

#### From Clankerbot (self-imposed)

Clients receive 429 with error code "rate_limited". Solutions:

1. Increase RATE_LIMIT_PER_MINUTE
2. Implement client-side backoff
3. Distribute load across multiple IPs

### Webhook Setup

#### 1. Configure Secret (Recommended)

```bash
# Generate secret
SECRET=$(openssl rand -hex 32)
echo "WEBHOOK_SHARED_SECRET=$SECRET" >> .env

# Restart
docker compose restart
```

#### 2. Register Webhook in Clockify

1. Go to Clockify → Settings → Webhooks
2. Add webhook URL: `https://your-domain.com/webhooks/clockify`
3. Add custom header: `X-Webhook-Secret: <your_secret>`
4. Select events to subscribe
5. Save

#### 3. Test Webhook

```bash
# Trigger test event in Clockify, check logs:
docker compose logs -f clankerbot

# Or send manual test:
curl -X POST https://your-domain.com/webhooks/clockify \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your_secret" \
  -H "X-Clockify-Event-Id: test_123" \
  -d '{"id": "test", "workspaceId": "ws123", "userId": "user123"}'
```

## Monitoring

### Health Checks

```bash
# Basic health (always returns ok if app is running)
curl http://localhost:8000/healthz

# Readiness (checks dependencies)
curl http://localhost:8000/readyz
# Returns: {"ok": true, "data": {"ready": true, "checks": {"llm": "configured", "clockify": "configured"}}}
```

### Logs

```bash
# Docker Compose
docker compose logs -f

# Docker
docker logs -f clankerbot

# JSON logs (if LOG_JSON=true)
docker compose logs clankerbot | jq .
```

### Key Metrics to Monitor

1. **Request rate**: Monitor via X-Request-ID in logs
2. **Error rate**: Count ApiResponse with ok=false
3. **LLM fallback rate**: Count parser="fallback" in /actions/parse responses
4. **Webhook duplicates**: Count duplicate=true in webhook responses
5. **429 errors**: Both self-imposed and from Clockify

## Troubleshooting

### LLM Parsing Always Falls Back

**Symptoms**: All llm=true requests return parser="fallback"

**Checks**:
1. `curl /readyz` → Check if llm="configured"
2. Verify DEEPSEEK_API_KEY is set and valid
3. Check logs for "LLM parsing failed" warnings
4. Test API key manually:
   ```bash
   curl https://api.deepseek.com/chat/completions \
     -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}]}'
   ```

### Clockify Actions Fail with "unauthorized"

**Symptoms**: /actions/run returns error code "unauthorized"

**Checks**:
1. `curl /readyz` → Check if clockify="configured"
2. Verify CLOCKIFY_API_KEY or CLOCKIFY_ADDON_TOKEN is set
3. Test key manually:
   ```bash
   curl https://api.clockify.me/api/v1/user \
     -H "X-Api-Key: $CLOCKIFY_API_KEY"
   ```

### Webhook Returns 401

**Symptoms**: POST /webhooks/clockify returns unauthorized

**Cause**: WEBHOOK_SHARED_SECRET is set but X-Webhook-Secret header missing/wrong

**Fix**:
- Add correct X-Webhook-Secret header to webhook calls
- OR remove WEBHOOK_SHARED_SECRET from env to disable validation

### High Memory Usage

**Symptoms**: Container OOM or high memory usage

**Possible causes**:
1. Webhook event cache growing (max 1000 entries)
2. Rate limit buckets accumulating (1 per IP+path)

**Mitigations**:
- Restart service to clear caches
- In production, move to Redis-backed caching

### Rate Limit Hit Frequently

**Symptoms**: Frequent 429 responses

**Solutions**:
1. Increase RATE_LIMIT_PER_MINUTE
2. Check if traffic is legitimate (review logs by IP)
3. Implement upstream rate limiting (nginx, API gateway)

## Backups and Disaster Recovery

Clankerbot is stateless. No backups needed.

**To restore**:
1. Redeploy from git
2. Set environment variables
3. Reconfigure webhooks in Clockify

## Security Incidents

### API Key Leaked

1. **Immediate**: Rotate key (see "Rotating API Keys")
2. **Investigate**: Check logs for unauthorized usage
3. **Notify**: Alert team, consider Clockify support if needed

### Unauthorized Access to Webhooks

1. **Immediate**: Enable WEBHOOK_SHARED_SECRET if not set
2. **Investigate**: Check logs for suspicious IPs
3. **Mitigate**: Add IP allowlist at reverse proxy level

## Performance Tuning

### Reduce LLM Latency

- Use faster LLM model (if available)
- Reduce LLM timeout (default 20s)
- Disable LLM parsing if not needed (llm=false)

### Reduce Clockify Latency

- Use regional Clockify URL if available (CLOCKIFY_BASE_URL)
- Optimize retry logic (adjust max_retries in code)

### Scale Horizontally

```bash
# Docker Compose: Scale to 3 replicas
docker compose up -d --scale clankerbot=3

# Kubernetes: Scale deployment
kubectl scale deployment/clankerbot --replicas=3
```

**Note**: For multi-instance deployments, migrate webhook cache and rate limiter to Redis.

## Support

- **Issues**: https://github.com/your-org/clankerbot/issues
- **Docs**: See README.md, ARCH.md
- **Clockify API**: https://clockify.me/developers-api
