"""
Request size limit middleware for security.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit request body size to prevent DoS attacks.
    Checks Content-Length header before reading the body.
    """

    def __init__(self, app, max_size_bytes: int = None):
        super().__init__(app)
        if max_size_bytes is None:
            max_size_bytes = settings.MAX_REQUEST_SIZE_MB * 1024 * 1024
        self.max_size_bytes = max_size_bytes

    async def dispatch(self, request: Request, call_next):
        # Check Content-Length header
        content_length = request.headers.get("content-length")

        if content_length:
            try:
                content_length_int = int(content_length)
                if content_length_int > self.max_size_bytes:
                    logger.warning(
                        f"Request rejected: body size {content_length_int} bytes "
                        f"exceeds limit of {self.max_size_bytes} bytes"
                    )
                    return JSONResponse(
                        status_code=413,
                        content={
                            "ok": False,
                            "error": {
                                "code": "payload_too_large",
                                "message": f"Request body too large. Maximum size is {self.max_size_bytes / (1024 * 1024):.1f}MB",
                            },
                        },
                    )
            except ValueError:
                # Invalid Content-Length header, let the framework handle it
                pass

        response = await call_next(request)
        return response
