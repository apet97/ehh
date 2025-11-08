# Changelog

All notable changes to Clankerbot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-11-08

### Added

#### Core Features
- **LLM Parser with Fallback**: DeepSeek integration with automatic fallback to rule-based parser
- **Typed Clockify Client**: Fully typed async client with Pydantic models
- **Webhook Idempotency**: LRU cache-based duplicate detection via X-Clockify-Event-Id
- **Rate Limiting**: Token bucket middleware (60 req/min default, configurable)
- **Request Tracing**: ULID-based request IDs in all logs and response headers
- **Structured Responses**: ApiResponse envelope for all endpoints
- **Health Endpoints**: `/healthz` (liveness) and `/readyz` (dependency checks)

#### Reliability & Security
- Configurable 20s timeouts with 3 retries + exponential backoff
- Webhook secret validation (WEBHOOK_SHARED_SECRET)
- Comprehensive error mapping (unauthorized, validation_error, rate_limited, upstream_error)
- Non-root Docker container (runs as user `clankerbot`, UID 1000)
- Input validation via Pydantic models
- Rate limiting per IP+path

#### Observability
- JSON logging option (LOG_JSON=true)
- Structured logs: timestamp, level, message, request_id, path, status, duration_ms
- OpenTelemetry ready (OTEL_EXPORTER_OTLP_ENDPOINT)
- Request/response logging middleware

#### Testing & Quality
- Comprehensive test suite (parsers, Clockify client, webhooks, rate limiting)
- Smoke test script (`scripts/smoke.sh`)
- GitHub Actions CI: lint (ruff/black), test (pytest), build (Docker), smoke tests
- Gitleaks integration for secret scanning
- Multi-arch Docker builds (amd64, arm64)

#### Tooling & Developer Experience
- Postman collection (`postman/Clankerbot.postman_collection.json`)
- VS Code REST Client file (`http/requests.http`)
- Manual HTML UI at `/tools/manual.html`
- Quickstart documentation (`docs/QUICKSTART.md`)
- Architecture documentation (`docs/ARCH.md`)
- Operations runbook (`docs/RUNBOOK.md`)

#### Infrastructure
- Multi-stage Dockerfile with health checks
- Docker Compose configuration with all env vars
- Kubernetes deployment files (`deploy/k8s/`)
- Helm chart (`deploy/helm/clankerbot/`)
- CI/CD pipeline with multi-arch builds

#### Clockify Integration
- Operations: get_user, list_workspaces, get_workspace, list_clients, create_client, create_time_entry, list_projects, create_project
- Dedicated webhook router (`/webhooks/clockify`)
- Event normalization (TIME_ENTRY, PROJECT, APPROVAL_REQUEST, etc.)
- Retry logic for 429/5xx errors
- Typed request/response models

### Changed
- Refactored Clockify integration to use async typed client
- Updated all endpoints to return ApiResponse envelope
- Enhanced configuration with new security and observability options
- Improved error handling and validation

### Fixed
- Module import errors (added `__init__.py` to all packages)
- Lint warnings (removed unused imports)

## [0.1.0] - Initial Release

### Added
- Basic FastAPI application structure
- Rule-based action parser
- Slack integration
- Basic Clockify support
- Scheduler for cron jobs
- Webhook endpoint

---

[0.2.0]: https://github.com/apet97/ehh/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/apet97/ehh/releases/tag/v0.1.0
