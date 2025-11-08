"""
Async Clockify API client with retry logic and error mapping.
"""
import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
import httpx
from app.utils.http import create_http_client
from app.integrations.clockify_types import (
    ClockifyUser,
    ClockifyWorkspace,
    ClockifyClient,
    ClientCreate,
    TimeEntryCreate,
    ClockifyTimeEntry,
)
from app.config import settings

logger = logging.getLogger(__name__)


class ClockifyAPIError(Exception):
    """Base exception for Clockify API errors."""
    def __init__(self, code: str, message: str, status_code: int = 500):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ClockifyClient:
    """Async Clockify API client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        addon_token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 20.0,
        max_retries: int = 3,
    ):
        self.base_url = (base_url or settings.CLOCKIFY_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.CLOCKIFY_API_KEY
        self.addon_token = addon_token or settings.CLOCKIFY_ADDON_TOKEN
        self.timeout = timeout
        self.max_retries = max_retries

        if not self.api_key and not self.addon_token:
            raise ValueError("Either CLOCKIFY_API_KEY or CLOCKIFY_ADDON_TOKEN must be set")

    def _auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        if self.api_key:
            return {"X-Api-Key": self.api_key}
        if self.addon_token:
            return {"X-Addon-Token": self.addon_token}
        return {}

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Any] = None,
    ) -> Any:
        """
        Make HTTP request with retry logic.
        Maps errors to ClockifyAPIError with appropriate codes.
        """
        url = f"{self.base_url}{path}"
        headers = self._auth_headers()
        headers["Content-Type"] = "application/json"

        last_exception = None
        for attempt in range(self.max_retries):
            try:
                async with create_http_client(timeout=self.timeout) as client:
                    response = await client.request(
                        method.upper(),
                        url,
                        headers=headers,
                        params=params,
                        json=json_body,
                    )

                    # Retry on 429 (rate limit) or 5xx
                    if response.status_code == 429:
                        delay = (2 ** attempt) * 0.5
                        logger.warning(
                            f"Clockify rate limit hit, retrying in {delay}s (attempt {attempt + 1}/{self.max_retries})"
                        )
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(delay)
                            continue
                        raise ClockifyAPIError(
                            "rate_limited",
                            "Clockify API rate limit exceeded",
                            429,
                        )

                    if response.status_code >= 500:
                        delay = (2 ** attempt) * 0.5
                        logger.warning(
                            f"Clockify server error {response.status_code}, retrying in {delay}s"
                        )
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(delay)
                            continue
                        raise ClockifyAPIError(
                            "upstream_error",
                            f"Clockify server error: {response.status_code}",
                            response.status_code,
                        )

                    # Handle errors
                    if response.status_code == 401:
                        raise ClockifyAPIError(
                            "unauthorized",
                            "Invalid Clockify API key or token",
                            401,
                        )

                    if response.status_code == 403:
                        raise ClockifyAPIError(
                            "forbidden",
                            "Insufficient permissions for this operation",
                            403,
                        )

                    if response.status_code == 400:
                        try:
                            error_data = response.json()
                        except Exception:
                            error_data = {"message": response.text}
                        raise ClockifyAPIError(
                            "validation_error",
                            f"Bad request: {error_data.get('message', 'Unknown error')}",
                            400,
                        )

                    if response.status_code == 404:
                        raise ClockifyAPIError(
                            "not_found",
                            "Resource not found",
                            404,
                        )

                    # Success
                    if response.status_code == 204:
                        return None

                    return response.json()

            except ClockifyAPIError:
                raise
            except httpx.TimeoutException as e:
                last_exception = e
                logger.warning(
                    f"Clockify timeout on attempt {attempt + 1}/{self.max_retries}"
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep((2 ** attempt) * 0.5)
                    continue
            except Exception as e:
                last_exception = e
                logger.error(f"Clockify API call failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep((2 ** attempt) * 0.5)
                    continue

        raise ClockifyAPIError(
            "upstream_error",
            f"Request failed after {self.max_retries} attempts",
            500,
        ) from last_exception

    async def get_user(self) -> ClockifyUser:
        """Get current user."""
        data = await self._request("GET", "/v1/user")
        return ClockifyUser(**data)

    async def list_workspaces(self) -> List[ClockifyWorkspace]:
        """List all workspaces."""
        data = await self._request("GET", "/v1/workspaces")
        return [ClockifyWorkspace(**w) for w in data]

    async def get_workspace(self, workspace_id: str) -> ClockifyWorkspace:
        """Get workspace by ID."""
        data = await self._request("GET", f"/v1/workspaces/{workspace_id}")
        return ClockifyWorkspace(**data)

    async def create_client(
        self, workspace_id: str, body: ClientCreate
    ) -> ClockifyClient:
        """Create a client in workspace."""
        data = await self._request(
            "POST",
            f"/v1/workspaces/{workspace_id}/clients",
            json_body=body.model_dump(),
        )
        return ClockifyClient(**data)

    async def list_clients(self, workspace_id: str) -> List[ClockifyClient]:
        """List clients in workspace."""
        data = await self._request("GET", f"/v1/workspaces/{workspace_id}/clients")
        return [ClockifyClient(**c) for c in data]

    async def create_time_entry(
        self, workspace_id: str, body: TimeEntryCreate
    ) -> ClockifyTimeEntry:
        """Create a time entry."""
        data = await self._request(
            "POST",
            f"/v1/workspaces/{workspace_id}/time-entries",
            json_body=body.model_dump(exclude_none=True),
        )
        return ClockifyTimeEntry(**data)
