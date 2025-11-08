# Changelog

All notable changes to Clankerbot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-08

### Added

#### Core Features
- **LLM-powered natural language parser** using DeepSeek API
  - Converts natural language to structured actions (e.g., "Get my Clockify user info" → `clockify.get_user`)
  - Automatic fallback to rule-based parser on LLM failure
  - Parser selection via `llm=true` query parameter
  - Timeout protection (20s) with graceful degradation

- **Comprehensive Clockify integration**
  - Typed async Clockify client with retry logic and error mapping
  - Support for users, workspaces, clients, time entries, and projects
  - Exponential backoff on 429 (rate limit) and 5xx errors (3 retries)
  - Structured error responses (unauthorized, validation_error, rate_limited, upstream_error, forbidden, not_found)
  - Both API key and addon token authentication modes

- **Clockify webhook receiver** with production features
  - Dedicated `/webhooks/clockify` endpoint
  - Idempotent processing via LRU cache (event ID deduplication)
  - Optional shared secret validation (WEBHOOK_SHARED_SECRET)
  - Support for TIME_ENTRY, PROJECT, and APPROVAL_REQUEST events
  - Automatic event type detection from payload structure

- **Enterprise-grade rate limiting**
  - Token bucket algorithm per IP + path combination
  - Configurable limits via RATE_LIMIT_PER_MINUTE (default: 60)
  - 429 responses with error code "rate_limited"
  - Memory-efficient bucket cleanup

#### Reliability & Observability
- **Request tracing with ULID-based request IDs**
  - Unique IDs in all logs and responses
  - X-Request-ID header support (accepts or generates)
  - Correlation across middleware, handlers, and integrations

- **Structured health endpoints**
  - `/healthz` - Liveness check (always returns ok if running)
  - `/readyz` - Readiness check with dependency validation (LLM, Clockify)
  - Standard response format via ApiResponse model

- **Production logging**
  - Structured logging with request_id, path, status, duration_ms
  - JSON log mode (LOG_JSON=true) for log aggregation
  - Request start/end logging with timing
  - Error logging with stack traces

- **OpenTelemetry instrumentation** (optional)
  - OTLP export support via OTEL_EXPORTER_OTLP_ENDPOINT
  - Distributed tracing ready
  - Feature-flagged for zero overhead when disabled

#### DevOps & Deployment
- **Kubernetes manifests** in `/deploy/k8s/`
  - Deployment with health probes (livenessProbe on /healthz, readinessProbe on /readyz)
  - Service (ClusterIP type)
  - Ingress with TLS support
  - ConfigMap for non-sensitive configuration

- **Helm chart** in `/deploy/helm/clankerbot/`
  - Production-ready with templated resources
  - Configurable replica count, resources, HPA
  - HPA disabled by default (enable in values.yaml)
  - Ingress disabled by default (enable in production)
  - Secret management for API keys
  - Liveness and readiness probes
  - Rolling update strategy
  - Service account support

- **Multi-architecture Docker builds**
  - Support for amd64 and arm64 architectures
  - Multi-stage Dockerfile for minimal image size
  - Non-root user (clankerbot, UID 1000)
  - Health check built into image

- **Enhanced CI/CD pipeline** in `.github/workflows/ci.yml`
  - Secrets scanning with gitleaks
  - Smoke tests using Docker Compose
  - Multi-architecture Docker builds (amd64, arm64)
  - Lint, test, and build jobs
  - Coverage reporting

#### Testing & Development Tools
- **Comprehensive test suite**
  - Unit tests for parser, Clockify client, webhooks, rate limiting
  - Mocked external dependencies
  - Pytest fixtures for common setup
  - Coverage reporting via pytest-cov

- **Smoke test script** (`scripts/smoke_test.sh`)
  - Validates health endpoints
  - Tests action parsing (rule-based and LLM)
  - Tests action execution (Clockify operations)
  - Tests webhook endpoint
  - Exit code 0 on success, 1 on failure

- **Manual testing UI** (`tools/manual.html`)
  - Standalone HTML interface for API testing
  - Three sections: Parser, Action Runner, Webhook Sender
  - Fetch-based API calls with JSON response display
  - No build system dependencies (pure HTML/JS)

- **Postman collection** (`postman/clankerbot.postman_collection.json`)
  - Pre-configured requests for all endpoints
  - Environment variables for host and API keys
  - Example payloads for each operation

- **REST Client files** (`http/*.http`)
  - VS Code REST Client compatible
  - Examples for health, parse, run, webhooks
  - Variable substitution support

#### Security
- **Webhook authentication**
  - Optional shared secret via WEBHOOK_SHARED_SECRET
  - X-Webhook-Secret header validation
  - 401 unauthorized on missing/invalid secret

- **CORS configuration**
  - Configurable allowed origins via CORS_ORIGINS
  - Wildcard support for development
  - Credentials support

- **Input validation**
  - Pydantic models for all request/response types
  - Type coercion and validation errors
  - Structured error responses

- **Secrets management**
  - Environment-only secrets (never hardcoded)
  - .env.example template for documentation
  - .gitignore protection for .env files
  - Gitleaks configuration for CI scanning

### Changed
- **Improved error handling**
  - Consistent error response format across all endpoints
  - ApiResponse.success() and ApiResponse.failure() helpers
  - Request ID included in all error responses
  - HTTP status codes aligned with error types

- **Enhanced middleware stack**
  - Request ID middleware for tracing
  - Rate limit middleware with token bucket
  - CORS middleware with configurable origins
  - Middleware execution order optimized

- **Refactored integration architecture**
  - Base Integration interface in `app/integrations/base.py`
  - Registry pattern for integration discovery
  - Typed operation parameters and responses
  - Consistent error mapping across integrations

### Fixed
- **Clockify client reliability**
  - Proper handling of 429 rate limit responses
  - Retry logic for transient failures
  - Timeout handling with graceful fallback
  - Error code mapping for all HTTP status codes

- **Webhook idempotency**
  - Duplicate event detection via X-Clockify-Event-Id
  - LRU cache with max 1000 entries
  - Memory leak prevention via bounded cache

### Documentation
- **Comprehensive guides** in `/docs/`
  - ARCH.md - Architecture documentation with diagrams
  - RUNBOOK.md - Operations guide for production
  - QUICKSTART.md - Quick start guide for new users
  - CHANGELOG.md - This file

- **Improved README.md**
  - Updated API examples
  - Environment variable documentation
  - Testing instructions
  - Security best practices

### Dependencies
- **Core framework**
  - FastAPI 0.104.1 - Web framework
  - uvicorn 0.24.0 - ASGI server
  - Pydantic 2.5.0 - Data validation

- **HTTP client**
  - httpx 0.25.1 - Async HTTP client

- **Integrations**
  - openai 1.3.0 - LLM client (DeepSeek compatible)

- **Utilities**
  - APScheduler 3.10.4 - Task scheduling
  - python-dotenv 1.0.0 - Environment configuration
  - python-ulid 1.1.0 - Request ID generation

- **Testing**
  - pytest 7.4.3 - Test framework
  - pytest-asyncio 0.21.1 - Async test support
  - pytest-cov 4.1.0 - Coverage reporting
  - pytest-mock 3.12.0 - Mocking utilities

### Deployment
- **Docker Compose** (`compose.yaml`)
  - Single-service deployment
  - Environment file support
  - Health check configuration
  - Auto-restart policy

- **Dockerfile improvements**
  - Multi-stage build for smaller images
  - Non-root user for security
  - Health check integrated
  - Python bytecode optimization

### Operations
- **Monitoring recommendations**
  - Request rate tracking via X-Request-ID
  - Error rate monitoring (ok=false responses)
  - LLM fallback rate (parser="fallback")
  - Webhook duplicate rate (duplicate=true)
  - 429 error rate (rate limiting)

- **Scaling considerations**
  - Horizontal scaling supported (stateless)
  - For multi-instance: migrate webhook cache to Redis
  - For multi-instance: migrate rate limiter to Redis
  - Load balancer should preserve client IP for rate limiting

## [0.1.0] - 2025-11-01

### Added
- Initial release
- Basic Clockify integration
- Rule-based action parser
- FastAPI web framework
- Docker support
- Basic health endpoints
- Environment-based configuration

---

## Upgrade Guide

### 0.1.x to 0.2.0

#### Breaking Changes
None. Version 0.2.0 is fully backward compatible with 0.1.x.

#### New Environment Variables (Optional)
```bash
# LLM parsing (optional)
DEEPSEEK_API_KEY=sk_xxx

# Security (recommended for production)
WEBHOOK_SHARED_SECRET=random_secret
RATE_LIMIT_PER_MINUTE=60

# Observability (optional)
LOG_JSON=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
```

#### Migration Steps
1. Update Docker image to v0.2.0
2. Add new environment variables (optional)
3. Restart service
4. Verify health: `curl /healthz && curl /readyz`
5. Test LLM parsing: `curl /actions/parse?llm=true -d '{"text":"Get my user info"}'`

#### Helm Chart Installation (New)
```bash
# Install with default values
helm install clankerbot ./deploy/helm/clankerbot \
  --set secrets.clockifyApiKey=your_key \
  --set secrets.deepseekApiKey=your_key

# Or use custom values.yaml
helm install clankerbot ./deploy/helm/clankerbot -f production-values.yaml
```

#### Kubernetes Deployment (New)
```bash
# Create secret first
kubectl create secret generic clankerbot-secrets \
  --from-literal=clockify-api-key=your_key \
  --from-literal=deepseek-api-key=your_key

# Apply manifests
kubectl apply -f deploy/k8s/
```

---

## Roadmap

### Planned for 0.3.0
- Additional Clockify operations (tags, tasks, reports)
- Slack integration enhancements
- GraphQL API support
- Webhook transformation rules
- Redis-backed caching and rate limiting
- Prometheus metrics endpoint
- Admin UI dashboard

### Under Consideration
- Multiple LLM provider support (OpenAI, Anthropic, local models)
- Workflow engine for multi-step automations
- Event-driven architecture with message queue
- Multi-tenancy support
- API key management UI
- Audit log export
