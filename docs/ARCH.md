# Clankerbot Architecture

## Overview

Clankerbot is an enterprise-grade automation service that processes user input through an HTTP API, optionally enriches it with LLM parsing (DeepSeek), executes actions via integrations (primarily Clockify), and handles webhooks with idempotency.

## System Architecture

```
┌──────────────┐
│  HTTP Client │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│          FastAPI Application                │
│  ┌────────────────────────────────────┐    │
│  │  Middleware Stack                  │    │
│  │  - Request ID injection            │    │
│  │  - Rate limiting (token bucket)    │    │
│  │  - CORS                             │    │
│  │  - Logging                          │    │
│  └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │  Endpoints                          │    │
│  │  - GET  /healthz                    │    │
│  │  - GET  /readyz                     │    │
│  │  - POST /actions/parse?llm=bool     │    │
│  │  - POST /actions/run                │    │
│  │  - POST /schedules                  │    │
│  │  - POST /webhooks/clockify          │    │
│  │  - POST /webhooks/{provider}        │    │
│  └────────────────────────────────────┘    │
└─────────────┬───────────────────────────────┘
              │
    ┌─────────┴──────────┐
    │                    │
    ▼                    ▼
┌─────────┐      ┌────────────────┐
│ LLM     │      │  Integrations  │
│ Parser  │      │  - Clockify    │
│         │      │  - Slack       │
│ DeepSeek│      │  - Extensible  │
└─────────┘      └────────────────┘
    │                    │
    │                    ▼
    │            ┌──────────────┐
    │            │ Clockify API │
    │            │ (External)   │
    │            └──────────────┘
    │
    ▼
┌─────────────────┐
│ Rule Parser     │
│ (Fallback)      │
└─────────────────┘
```

## Pipeline Flow

### 1. User Input → Parse → Action

**With LLM (llm=true):**
```
User text → LLM Parser (DeepSeek)
              ↓ (on success)
            Action object (parser: "llm")
              ↓ (on failure)
          Rule Parser (fallback)
              ↓
            Action object (parser: "fallback")
```

**Without LLM (llm=false or default):**
```
User text → Rule Parser
              ↓
            Action object (parser: "rule")
```

### 2. Action Execution

```
Action → Integration Router
           ↓
       Clockify Client (or other)
           ↓
       HTTP Request (with retry)
           ↓
       Clockify API
           ↓
       Response mapping
           ↓
       ApiResponse envelope
```

### 3. Webhook Handling

```
Clockify Webhook → Secret validation (optional)
                     ↓
                   Idempotency check (X-Clockify-Event-Id)
                     ↓
                   Event normalization
                     ↓
                   ApiResponse with event data
```

## Component Details

### Middleware

1. **RequestIDMiddleware**: Generates or extracts request IDs, adds to response headers
2. **RateLimitMiddleware**: Token bucket per (IP, path), returns 429 on limit
3. **CORSMiddleware**: Configurable origins

### LLM Client

- **Timeout**: 20s default
- **Retries**: 3 attempts with exponential backoff (0.5s, 1s, 2s)
- **Retry conditions**: 429 (rate limit), 5xx (server errors)
- **Fallback**: On failure, actions.py falls back to rule parser

### Clockify Client

- **Authentication**: X-Api-Key or X-Addon-Token
- **Base URL**: Configurable (default: https://api.clockify.me/api)
- **Timeout**: 20s default
- **Retries**: 3 attempts on 429/5xx
- **Error mapping**:
  - 401 → unauthorized
  - 400 → validation_error
  - 404 → not_found
  - 429 → rate_limited
  - 5xx → upstream_error

### Webhook Idempotency

- **Mechanism**: In-memory LRU cache (1000 events max)
- **Key**: X-Clockify-Event-Id header
- **Behavior**: Duplicate events return success but flag `duplicate: true`

### Rate Limiting

- **Algorithm**: Token bucket
- **Default**: 60 requests/minute per (IP, path)
- **Configurable**: RATE_LIMIT_PER_MINUTE env var
- **Response**: 429 with ApiError code "rate_limited"

## Failure Modes and Mitigations

| Failure | Mitigation |
|---------|-----------|
| LLM timeout | 3 retries, then fallback to rule parser |
| LLM invalid response | Catch JSON parse error, fallback to rule parser |
| Clockify 429 | 3 retries with exponential backoff |
| Clockify 5xx | 3 retries with exponential backoff |
| Clockify 401 | Immediate error, no retry |
| Duplicate webhook | Idempotency check prevents reprocessing |
| Rate limit exceeded | Return 429, client should backoff |

## Observability

### Logging

- **Format**: Plain text (default) or JSON (LOG_JSON=true)
- **Fields**: timestamp, level, message, request_id, path, status, duration_ms
- **Levels**: INFO (default), configurable

### Request Tracing

- **Request ID**: ULID format, in X-Request-ID header
- **Propagation**: Logged in all request/response logs

### OpenTelemetry (Optional)

- **Feature flag**: OTEL_EXPORTER_OTLP_ENDPOINT
- **Instrumentation**: FastAPI, httpx (when enabled)

## Security

1. **Webhook secrets**: Optional WEBHOOK_SHARED_SECRET, validated via X-Webhook-Secret header
2. **API keys**: Never hardcoded, read from env
3. **Rate limiting**: Prevents abuse
4. **Non-root container**: Runs as user `clankerbot` (UID 1000)
5. **Input validation**: Pydantic models for all requests

## Scalability Considerations

- **Stateless**: No persistent state (except in-memory webhook cache)
- **Horizontal scaling**: Deploy multiple instances behind load balancer
- **Rate limit**: Move to Redis for shared state across instances
- **Webhook cache**: Move to Redis for shared idempotency across instances

## Dependencies

- FastAPI: Web framework
- httpx: Async HTTP client
- Pydantic: Data validation
- APScheduler: Cron scheduling
- python-dotenv: Environment configuration
