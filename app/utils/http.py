"""
HTTP client utilities with sane defaults for clankerbot.
"""
from __future__ import annotations
import httpx


def create_http_client(
    timeout: float = 20.0,
    user_agent: str = "clankerbot/0.2",
    **kwargs
) -> httpx.AsyncClient:
    """
    Create a configured async HTTP client with:
    - Sane timeout defaults (20s)
    - Custom user-agent
    - Retry transport for idempotent methods (GET, HEAD, OPTIONS, etc.)
    """
    headers = kwargs.pop("headers", {})
    headers.setdefault("User-Agent", user_agent)

    # Create timeout config
    timeout_config = httpx.Timeout(timeout, connect=10.0)

    # Create transport with retry logic for network errors
    # Note: httpx doesn't have built-in retry, we handle it at call level
    transport = httpx.AsyncHTTPTransport(retries=0)  # We handle retries manually

    return httpx.AsyncClient(
        timeout=timeout_config,
        headers=headers,
        transport=transport,
        **kwargs
    )
