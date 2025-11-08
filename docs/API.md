# Clankerbot API Documentation

Complete API reference for Clankerbot v0.2.1 - Enterprise-grade webhook and API orchestration service.

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Response Envelope](#response-envelope)
- [Error Codes](#error-codes)
- [Rate Limiting](#rate-limiting)
- [Request Tracing](#request-tracing)
- [Endpoints](#endpoints)
  - [Health Endpoints](#health-endpoints)
  - [Action Parser](#action-parser)
  - [Action Runner](#action-runner)
  - [Webhook Receiver](#webhook-receiver)
  - [Metrics](#metrics)

---

## Overview

Clankerbot provides a unified API for:
- Parsing natural language or structured commands into executable actions
- Executing actions against integrated services (Clockify, Slack, etc.)
- Receiving and processing webhooks with idempotency guarantees
- Health and readiness checks for orchestration platforms

All responses follow a consistent envelope structure with request tracing support.

## Base URL

Default local development:
```
http://localhost:8000
```

Production (replace with your deployment):
```
https://clankerbot.example.com
```

All endpoints are prefixed with the base URL.

## Authentication

Clankerbot uses different authentication methods depending on the endpoint:

### API Key Authentication (Clockify Operations)

For executing Clockify operations, authentication is handled via environment variables:

**Option 1: User API Key**
```bash
CLOCKIFY_API_KEY=your_clockify_api_key
```

**Option 2: Addon Token**
```bash
CLOCKIFY_ADDON_TOKEN=your_addon_token
```

The API key is sent to Clockify as:
```
X-Api-Key: your_clockify_api_key
```

Or for addon tokens:
```
X-Addon-Token: your_addon_token
```

### Webhook Authentication

Webhooks can be secured with a shared secret:

**Request Header:**
```
X-Webhook-Secret: your_webhook_secret
```

Configure via environment variable:
```bash
WEBHOOK_SHARED_SECRET=randomly_generated_secret_at_least_32_chars
```

If `WEBHOOK_SHARED_SECRET` is set, all webhook requests must include the matching `X-Webhook-Secret` header.

## Response Envelope

All API responses use a consistent `ApiResponse` envelope:

### Success Response

```json
{
  "ok": true,
  "data": {
    "...": "response data here"
  },
  "error": null,
  "requestId": "01JCEXAMPLE123ABC"
}
```

**Fields:**
- `ok` (boolean): Always `true` for successful responses
- `data` (any): Response data, type varies by endpoint
- `error` (null): Always `null` for successful responses
- `requestId` (string): ULID-based unique request identifier

### Error Response

```json
{
  "ok": false,
  "data": null,
  "error": {
    "code": "validation_error",
    "message": "Human-readable error message",
    "details": {
      "field": "additional context if available"
    }
  },
  "requestId": "01JCEXAMPLE456DEF"
}
```

**Fields:**
- `ok` (boolean): Always `false` for error responses
- `data` (null): Always `null` for error responses
- `error` (object): Error details
  - `code` (string): Machine-readable error code (see [Error Codes](#error-codes))
  - `message` (string): Human-readable error description
  - `details` (object, optional): Additional context about the error
- `requestId` (string): ULID-based unique request identifier

## Error Codes

Clankerbot uses standardized error codes across all endpoints:

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `unauthorized` | 401 | Missing or invalid authentication credentials |
| `forbidden` | 403 | Authenticated but insufficient permissions |
| `validation_error` | 400 | Invalid request parameters or body |
| `rate_limited` | 429 | Rate limit exceeded for this IP/path |
| `upstream_error` | 502/503 | Upstream service (Clockify, LLM) error |
| `not_found` | 404 | Resource or operation not found |
| `internal_error` | 500 | Internal server error |

### Error Code Examples

#### unauthorized
```json
{
  "ok": false,
  "error": {
    "code": "unauthorized",
    "message": "Invalid Clockify API key or token"
  },
  "requestId": "01JCEX001"
}
```

#### validation_error
```json
{
  "ok": false,
  "error": {
    "code": "validation_error",
    "message": "workspaceId required"
  },
  "requestId": "01JCEX002"
}
```

#### rate_limited
```json
{
  "ok": false,
  "error": {
    "code": "rate_limited",
    "message": "Rate limit exceeded. Try again later."
  },
  "requestId": "01JCEX003"
}
```

#### upstream_error
```json
{
  "ok": false,
  "error": {
    "code": "upstream_error",
    "message": "Clockify server error: 503"
  },
  "requestId": "01JCEX004"
}
```

#### not_found
```json
{
  "ok": false,
  "error": {
    "code": "not_found",
    "message": "Resource not found"
  },
  "requestId": "01JCEX005"
}
```

#### internal_error
```json
{
  "ok": false,
  "error": {
    "code": "internal_error",
    "message": "Unexpected error occurred"
  },
  "requestId": "01JCEX006"
}
```

## Rate Limiting

Clankerbot implements token bucket rate limiting per IP address and path combination.

**Default Limits:**
- 60 requests per minute per IP+path
- Burst capacity: 30 requests
- Configurable via `RATE_LIMIT_PER_MINUTE` and `RATE_LIMIT_BURST`

**429 Response:**
```json
{
  "ok": false,
  "error": {
    "code": "rate_limited",
    "message": "Rate limit exceeded. Try again later."
  },
  "requestId": "01JCEXAMPLE789"
}
```

**Best Practices:**
- Implement exponential backoff on 429 responses
- Cache responses when possible
- Use batch operations if available
- Monitor rate limit headers (if implemented)

## Request Tracing

All requests are assigned a unique request ID (ULID format) for distributed tracing.

**Request Header (Optional):**
```
X-Request-ID: 01JCEXAMPLE123
```

If provided, the same ID will be used. Otherwise, a new ULID will be generated.

**Response Header:**
```
X-Request-ID: 01JCEXAMPLE123
```

The request ID is also included in:
- Response JSON (`requestId` field)
- Server logs (for correlation)

**Example:**
```bash
curl -H "X-Request-ID: 01JCEX001" http://localhost:8000/healthz
```

---

## Endpoints

### Health Endpoints

#### GET /healthz

Basic liveness probe. Returns healthy status if the service is running.

**Use Case:** Kubernetes liveness probe, load balancer health checks

**Request:**
```bash
curl http://localhost:8000/healthz
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "data": {
    "status": "healthy"
  },
  "error": null,
  "requestId": "01JCEX100"
}
```

**Error Responses:** None (always returns 200 if service is running)

---

#### GET /readyz

Readiness probe with dependency validation. Checks if required services are configured.

**Use Case:** Kubernetes readiness probe, deployment validation

**Request:**
```bash
curl http://localhost:8000/readyz
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "data": {
    "ready": true,
    "checks": {
      "llm": "configured",
      "clockify": "configured"
    }
  },
  "error": null,
  "requestId": "01JCEX101"
}
```

**Response Fields:**
- `ready` (boolean): `true` if all dependencies are configured, `false` otherwise
- `checks` (object): Status of each dependency
  - `llm`: `"configured"` or `"missing"` (based on `DEEPSEEK_API_KEY`)
  - `clockify`: `"configured"` or `"missing"` (based on `CLOCKIFY_API_KEY` or `CLOCKIFY_ADDON_TOKEN`)

**Example - Missing Dependencies:**
```json
{
  "ok": true,
  "data": {
    "ready": false,
    "checks": {
      "llm": "missing",
      "clockify": "configured"
    }
  },
  "error": null,
  "requestId": "01JCEX102"
}
```

---

### Action Parser

#### POST /actions/parse

Parse text into a structured action using rule-based or LLM-based parsing.

**Request Body:**
```json
{
  "text": "clockify.get_user"
}
```

**Query Parameters:**
- `llm` (boolean, optional): Use LLM parser if `true`, rule-based parser if `false` (default: `false`)

**Examples:**

##### Rule-Based Parsing

```bash
curl -X POST http://localhost:8000/actions/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "clockify.get_user"}'
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "data": {
    "integration": "clockify",
    "operation": "get_user",
    "params": {},
    "parser": "rule"
  },
  "error": null,
  "requestId": "01JCEX200"
}
```

##### LLM-Based Parsing

```bash
curl -X POST "http://localhost:8000/actions/parse?llm=true" \
  -H "Content-Type: application/json" \
  -d '{"text": "Get my Clockify user information"}'
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "data": {
    "integration": "clockify",
    "operation": "get_user",
    "params": {},
    "parser": "llm"
  },
  "error": null,
  "requestId": "01JCEX201"
}
```

**Parser Types:**
- `"rule"`: Rule-based parser (pattern matching on `integration.operation`)
- `"llm"`: LLM successfully parsed the natural language
- `"fallback"`: LLM failed or unavailable, fell back to rule parser

##### LLM Fallback Example

If LLM is not configured or fails:
```json
{
  "ok": true,
  "data": {
    "integration": "clockify",
    "operation": "get_user",
    "params": {},
    "parser": "fallback"
  },
  "error": null,
  "requestId": "01JCEX202"
}
```

**Error Responses:**

##### Validation Error
```json
{
  "ok": false,
  "error": {
    "code": "validation_error",
    "message": "Unable to parse action from text"
  },
  "requestId": "01JCEX203"
}
```

---

### Action Runner

#### POST /actions/run

Execute an action against an integration.

**Request Body:**
```json
{
  "integration": "clockify",
  "operation": "get_user",
  "params": {}
}
```

**Fields:**
- `integration` (string): Integration name (e.g., `"clockify"`)
- `operation` (string): Operation name (e.g., `"get_user"`)
- `params` (object): Operation-specific parameters

**Examples:**

##### Get User

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "get_user",
    "params": {}
  }'
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "id": "user123abc",
  "email": "user@example.com",
  "name": "John Doe",
  "activeWorkspace": "workspace123",
  "defaultWorkspace": "workspace123",
  "settings": {
    "timeZone": "America/New_York"
  },
  "requestId": "01JCEX300"
}
```

##### List Workspaces

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "list_workspaces",
    "params": {}
  }'
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "workspaces": [
    {
      "id": "workspace123",
      "name": "My Workspace",
      "imageUrl": ""
    }
  ],
  "requestId": "01JCEX301"
}
```

##### Get Workspace

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "get_workspace",
    "params": {
      "workspaceId": "workspace123"
    }
  }'
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "id": "workspace123",
  "name": "My Workspace",
  "imageUrl": "",
  "requestId": "01JCEX302"
}
```

##### List Clients

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "list_clients",
    "params": {
      "workspaceId": "workspace123"
    }
  }'
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "clients": [
    {
      "id": "client123",
      "name": "Acme Corp",
      "archived": false,
      "workspaceId": "workspace123"
    }
  ],
  "requestId": "01JCEX303"
}
```

##### Create Client

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "create_client",
    "params": {
      "workspaceId": "workspace123",
      "body": {
        "name": "New Client Inc",
        "archived": false
      }
    }
  }'
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "id": "client456",
  "name": "New Client Inc",
  "archived": false,
  "workspaceId": "workspace123",
  "requestId": "01JCEX304"
}
```

##### List Projects

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "list_projects",
    "params": {
      "workspaceId": "workspace123"
    }
  }'
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "projects": [
    {
      "id": "project123",
      "name": "Website Redesign",
      "clientId": "client123",
      "workspaceId": "workspace123",
      "billable": true,
      "color": "#FF5733",
      "archived": false
    }
  ],
  "requestId": "01JCEX305"
}
```

##### Create Project

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "create_project",
    "params": {
      "workspaceId": "workspace123",
      "body": {
        "name": "Mobile App Development",
        "clientId": "client123",
        "isPublic": false,
        "color": "#3498DB"
      }
    }
  }'
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "id": "project456",
  "name": "Mobile App Development",
  "clientId": "client123",
  "workspaceId": "workspace123",
  "billable": true,
  "color": "#3498DB",
  "archived": false,
  "requestId": "01JCEX306"
}
```

##### Create Time Entry

```bash
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d '{
    "integration": "clockify",
    "operation": "create_time_entry",
    "params": {
      "workspaceId": "workspace123",
      "body": {
        "start": "2024-01-15T10:00:00Z",
        "end": "2024-01-15T12:00:00Z",
        "description": "API integration work",
        "projectId": "project123",
        "billable": true
      }
    }
  }'
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "id": "entry789",
  "description": "API integration work",
  "userId": "user123",
  "workspaceId": "workspace123",
  "projectId": "project123",
  "timeInterval": {
    "start": "2024-01-15T10:00:00Z",
    "end": "2024-01-15T12:00:00Z"
  },
  "billable": true,
  "requestId": "01JCEX307"
}
```

**Error Responses:**

##### Unauthorized (Missing Credentials)
```json
{
  "ok": false,
  "error": {
    "code": "unauthorized",
    "message": "Clockify API key or token not configured"
  },
  "requestId": "01JCEX308"
}
```

##### Validation Error (Missing Required Parameter)
```json
{
  "ok": false,
  "error": {
    "code": "validation_error",
    "message": "workspaceId required"
  },
  "requestId": "01JCEX309"
}
```

##### Not Found (Unknown Operation)
```json
{
  "ok": false,
  "error": {
    "code": "not_found",
    "message": "Unknown operation: invalid_operation"
  },
  "requestId": "01JCEX310"
}
```

##### Rate Limited (Clockify API)
```json
{
  "ok": false,
  "error": {
    "code": "rate_limited",
    "message": "Clockify API rate limit exceeded",
    "status_code": 429
  },
  "requestId": "01JCEX311"
}
```

---

### Webhook Receiver

#### POST /webhooks/clockify

Receive and process Clockify webhooks with idempotency guarantees.

**Features:**
- IP allowlist validation (if configured)
- Secret validation (if configured)
- Duplicate detection via event ID
- Automatic event type detection
- Event normalization

**Request Headers:**
```
Content-Type: application/json
X-Webhook-Secret: your_secret (required if WEBHOOK_SHARED_SECRET is set)
X-Clockify-Event-Id: unique_event_id (recommended for idempotency)
```

**Request Body:** Raw Clockify webhook payload (varies by event type)

**Examples:**

##### Time Entry Webhook

```bash
curl -X POST http://localhost:8000/webhooks/clockify \
  -H "Content-Type: application/json" \
  -H "X-Clockify-Event-Id: evt_12345" \
  -d '{
    "id": "entry123",
    "userId": "user123",
    "workspaceId": "ws123",
    "description": "Development work",
    "timeInterval": {
      "start": "2024-01-15T10:00:00Z",
      "end": "2024-01-15T12:00:00Z"
    },
    "projectId": "project123"
  }'
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "data": {
    "received": true,
    "duplicate": false,
    "eventId": "evt_12345",
    "event": {
      "eventType": "TIME_ENTRY",
      "id": "entry123",
      "workspaceId": "ws123",
      "userId": "user123",
      "rawPayload": {
        "id": "entry123",
        "userId": "user123",
        "workspaceId": "ws123",
        "description": "Development work",
        "timeInterval": {
          "start": "2024-01-15T10:00:00Z",
          "end": "2024-01-15T12:00:00Z"
        },
        "projectId": "project123"
      }
    }
  },
  "error": null,
  "requestId": "01JCEX400"
}
```

##### Duplicate Event (Idempotency)

Sending the same event ID again:

```bash
curl -X POST http://localhost:8000/webhooks/clockify \
  -H "Content-Type: application/json" \
  -H "X-Clockify-Event-Id: evt_12345" \
  -d '{...same payload...}'
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "data": {
    "received": true,
    "duplicate": true,
    "eventId": "evt_12345",
    "event": {...}
  },
  "error": null,
  "requestId": "01JCEX401"
}
```

##### Project Event

```bash
curl -X POST http://localhost:8000/webhooks/clockify \
  -H "Content-Type: application/json" \
  -H "X-Clockify-Event-Id: evt_67890" \
  -d '{
    "id": "project123",
    "name": "New Project",
    "workspaceId": "ws123",
    "clientId": "client123",
    "tasks": []
  }'
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "data": {
    "received": true,
    "duplicate": false,
    "eventId": "evt_67890",
    "event": {
      "eventType": "PROJECT",
      "id": "project123",
      "workspaceId": "ws123",
      "userId": null,
      "rawPayload": {...}
    }
  },
  "error": null,
  "requestId": "01JCEX402"
}
```

**Event Types:**

Clankerbot automatically detects event types based on payload structure:

- `TIME_ENTRY` - Time entry created/updated
- `NEW_TIMER_STARTED` - Timer started (no end time)
- `PROJECT` - Project created/updated
- `CLIENT` - Client created/updated
- `TAG` - Tag created/updated
- `USER` - User created/updated
- `EXPENSE` - Expense created/updated
- `APPROVAL_REQUEST` - Approval request created/updated
- `UNKNOWN` - Cannot determine type from structure

**Error Responses:**

##### Unauthorized (Missing Secret)
```json
{
  "ok": false,
  "error": {
    "code": "unauthorized",
    "message": "Missing X-Webhook-Secret header"
  },
  "requestId": "01JCEX403"
}
```

##### Unauthorized (Invalid Secret)
```json
{
  "ok": false,
  "error": {
    "code": "unauthorized",
    "message": "Invalid webhook secret"
  },
  "requestId": "01JCEX404"
}
```

##### Forbidden (IP Not Allowed)
```json
{
  "ok": false,
  "error": {
    "code": "forbidden",
    "message": "IP address 203.0.113.50 not in allowlist"
  },
  "requestId": "01JCEX405"
}
```

##### Validation Error (Invalid JSON)
```json
{
  "ok": false,
  "error": {
    "code": "validation_error",
    "message": "Invalid JSON payload"
  },
  "requestId": "01JCEX406"
}
```

---

### Metrics

#### GET /metrics

Prometheus metrics endpoint (if `METRICS_ENABLED=true`).

**Use Case:** Prometheus scraping, monitoring dashboards

**Request:**
```bash
curl http://localhost:8000/metrics
```

**Response:** `200 OK` (Prometheus exposition format)
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/healthz",status="200"} 42

# HELP http_request_duration_seconds HTTP request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.005",method="GET",path="/healthz"} 40
http_request_duration_seconds_bucket{le="0.01",method="GET",path="/healthz"} 42
...
```

**Configuration:**
```bash
METRICS_ENABLED=true
```

If `METRICS_ENABLED` is not set or `false`, this endpoint is not exposed.

---

## Complete Examples

### Parse and Execute Workflow

```bash
# 1. Parse natural language to action
PARSE_RESPONSE=$(curl -s -X POST "http://localhost:8000/actions/parse?llm=true" \
  -H "Content-Type: application/json" \
  -d '{"text": "Get my Clockify user info"}')

echo "Parse Response: $PARSE_RESPONSE"

# 2. Extract action details
INTEGRATION=$(echo $PARSE_RESPONSE | jq -r '.data.integration')
OPERATION=$(echo $PARSE_RESPONSE | jq -r '.data.operation')

# 3. Execute the action
curl -X POST http://localhost:8000/actions/run \
  -H "Content-Type: application/json" \
  -d "{\"integration\":\"$INTEGRATION\",\"operation\":\"$OPERATION\",\"params\":{}}"
```

### Webhook Setup

**1. Configure webhook secret:**
```bash
# Generate secret
openssl rand -hex 32

# Add to .env
echo "WEBHOOK_SHARED_SECRET=your_generated_secret" >> .env

# Restart service
docker compose restart
```

**2. Configure Clockify webhook:**

In Clockify workspace settings:
- Webhook URL: `https://clankerbot.example.com/webhooks/clockify`
- Custom headers: `X-Webhook-Secret: your_generated_secret`
- Events: Select desired events (time entries, projects, etc.)

**3. Test webhook:**
```bash
curl -X POST https://clankerbot.example.com/webhooks/clockify \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your_generated_secret" \
  -H "X-Clockify-Event-Id: test_event_$(date +%s)" \
  -d '{
    "id": "test_entry",
    "userId": "test_user",
    "workspaceId": "test_workspace",
    "timeInterval": {
      "start": "2024-01-15T10:00:00Z",
      "end": "2024-01-15T11:00:00Z"
    }
  }'
```

### Monitoring Health

```bash
#!/bin/bash
# health-check.sh

# Check liveness
HEALTH=$(curl -s http://localhost:8000/healthz | jq -r '.ok')
if [ "$HEALTH" != "true" ]; then
  echo "Service is not healthy!"
  exit 1
fi

# Check readiness
READY=$(curl -s http://localhost:8000/readyz | jq -r '.data.ready')
if [ "$READY" != "true" ]; then
  echo "Service is not ready!"
  echo "Dependency status:"
  curl -s http://localhost:8000/readyz | jq '.data.checks'
  exit 1
fi

echo "Service is healthy and ready"
```

---

## Best Practices

### Error Handling

```javascript
async function callClankerbot(endpoint, payload) {
  const response = await fetch(`http://localhost:8000${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Request-ID': generateULID(), // Optional but recommended
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!data.ok) {
    const { code, message } = data.error;

    switch (code) {
      case 'rate_limited':
        // Implement exponential backoff
        await sleep(2000);
        return callClankerbot(endpoint, payload);

      case 'unauthorized':
        // Re-authenticate or alert admin
        throw new Error('Authentication required');

      case 'validation_error':
        // Fix request and retry
        console.error('Validation error:', message);
        throw new Error(message);

      default:
        throw new Error(`API error: ${message}`);
    }
  }

  return data.data;
}
```

### Request Tracing

```python
import requests
from ulid import ULID

def make_request(endpoint, payload):
    request_id = str(ULID())

    response = requests.post(
        f"http://localhost:8000{endpoint}",
        json=payload,
        headers={"X-Request-ID": request_id}
    )

    data = response.json()

    # Log with request ID for correlation
    print(f"[{request_id}] Response: {data}")

    return data
```

### Rate Limit Handling

```go
package main

import (
    "time"
    "math"
)

func callWithRetry(endpoint string, payload map[string]interface{}) error {
    maxRetries := 5

    for attempt := 0; attempt < maxRetries; attempt++ {
        resp, err := makeRequest(endpoint, payload)

        if err == nil {
            return nil
        }

        if isRateLimited(err) {
            // Exponential backoff
            backoff := time.Duration(math.Pow(2, float64(attempt))) * time.Second
            time.Sleep(backoff)
            continue
        }

        return err
    }

    return errors.New("max retries exceeded")
}
```

---

## Support

- **GitHub Issues:** https://github.com/your-org/clankerbot/issues
- **Documentation:** https://github.com/your-org/clankerbot/blob/main/README.md
- **Clockify API:** https://clockify.me/developers-api
- **DeepSeek API:** https://platform.deepseek.com/

---

**Last Updated:** 2025-11-08
**Version:** 0.2.1
