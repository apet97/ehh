"""
Simple in-memory token bucket rate limiter.
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class TokenBucket:
    """Token bucket for rate limiting with burst support."""

    def __init__(self, capacity: int, refill_rate: float, burst: int = None):
        self.capacity = capacity
        self.burst = burst if burst is not None else capacity
        self.tokens = self.burst  # Start with burst capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens. Returns True if allowed."""
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self):
        """Refill tokens based on elapsed time up to burst capacity."""
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.burst, self.tokens + new_tokens)
        self.last_refill = now


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limit middleware using in-memory token bucket with burst capacity.
    Keyed by (client_ip, path).
    """

    def __init__(self, app, capacity: int = 60, burst: int = None):
        super().__init__(app)
        self.capacity = capacity
        self.burst = burst if burst is not None else capacity
        self.refill_rate = capacity / 60.0  # refill rate per second
        self.buckets: Dict[Tuple[str, str], TokenBucket] = defaultdict(
            lambda: TokenBucket(self.capacity, self.refill_rate, self.burst)
        )

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Create bucket key
        path = request.url.path
        key = (client_ip, path)

        # Check rate limit
        bucket = self.buckets[key]
        if not bucket.consume():
            return JSONResponse(
                status_code=429,
                content={
                    "ok": False,
                    "error": {
                        "code": "rate_limited",
                        "message": f"Rate limit exceeded. Max {self.capacity} requests per minute.",
                    },
                },
            )

        response = await call_next(request)
        return response
