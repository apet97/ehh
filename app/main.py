
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
import time
import logging
from app.utils.logging import configure_logging
from app.utils.ids import request_id as get_request_id
from app.config import settings
from app import scheduler as sched
from app.routes import actions as actions_routes
from app.routes import webhooks_clockify
from app.integrations import slack  # populate registry
from app.integrations import clockify  # populate registry
from app.integrations.base import get_integration
from app.models import WebhookEnvelope, ApiResponse
from app.middleware.ratelimit import RateLimitMiddleware

load_dotenv()
configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI(title="Clankerbot", version="0.2")


# Request ID and logging middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID to all requests and responses, log request/response."""

    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        req_id = get_request_id(request.headers.get("x-request-id"))
        request.state.request_id = req_id

        # Log request start
        start_time = time.time()
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={"request_id": req_id, "path": request.url.path},
        )

        # Process request
        response = await call_next(request)

        # Log request finish
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Request completed: {request.method} {request.url.path} status={response.status_code}",
            extra={
                "request_id": req_id,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = req_id

        return response


# Add middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    capacity=settings.RATE_LIMIT_PER_MINUTE,
)

# CORS
origins = [s.strip() for s in settings.CORS_ORIGINS.split(",") if s.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _startup():
    sched.start_scheduler()
    logger.info("Clankerbot started successfully")


# Health endpoints
@app.get("/healthz")
async def health(request: Request):
    """Basic health check."""
    req_id = get_request_id(request.headers.get("x-request-id"))
    return ApiResponse.success(data={"status": "healthy"}, request_id=req_id)


@app.get("/readyz")
async def readiness(request: Request):
    """Readiness check with dependency validation."""
    req_id = get_request_id(request.headers.get("x-request-id"))

    checks = {}

    # Check LLM configuration
    if settings.DEEPSEEK_API_KEY:
        checks["llm"] = "configured"
    else:
        checks["llm"] = "missing"

    # Check Clockify configuration
    if settings.CLOCKIFY_API_KEY or settings.CLOCKIFY_ADDON_TOKEN:
        checks["clockify"] = "configured"
    else:
        checks["clockify"] = "missing"

    # Overall status
    all_ready = all(v == "configured" for v in checks.values())

    return ApiResponse.success(
        data={
            "ready": all_ready,
            "checks": checks,
        },
        request_id=req_id,
    )


# Routes
app.include_router(actions_routes.router)
app.include_router(webhooks_clockify.router)


# Legacy webhook endpoint for backward compatibility
@app.post("/webhooks/{provider}")
async def webhook(request: Request, provider: str, env: WebhookEnvelope):
    """
    Legacy webhook endpoint.
    For Clockify, prefer the dedicated /webhooks/clockify endpoint.
    """
    req_id = get_request_id(request.headers.get("x-request-id"))

    try:
        # Delegate to specific router if clockify
        if provider == "clockify":
            # Redirect to dedicated endpoint
            logger.info(
                f"Redirecting legacy webhook to dedicated Clockify endpoint"
            )

        integ = get_integration(provider)
        result = await integ.handle_webhook(env.payload)

        # Add request ID
        if isinstance(result, dict):
            result["requestId"] = req_id

        return JSONResponse(result)

    except ValueError as e:
        return ApiResponse.failure(
            code="not_found",
            message=str(e),
            request_id=req_id,
        )
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}", exc_info=True)
        return ApiResponse.failure(
            code="internal_error",
            message=str(e),
            request_id=req_id,
        )
