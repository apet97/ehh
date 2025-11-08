"""
Tests for Clockify client.
"""
import pytest
import respx
import httpx
from app.integrations.clockify_client import ClockifyClient, ClockifyAPIError
from app.integrations.clockify_types import ClientCreate


@pytest.fixture
def clockify_client():
    """Create a test Clockify client."""
    return ClockifyClient(
        api_key="test_key",
        base_url="https://api.clockify.test",
        timeout=5.0,
        max_retries=2,
    )


@pytest.mark.asyncio
@respx.mock
async def test_get_user_success(clockify_client):
    """Test successful user retrieval."""
    mock_user = {
        "id": "user123",
        "email": "test@example.com",
        "name": "Test User",
        "activeWorkspace": "ws123",
    }

    respx.get("https://api.clockify.test/v1/user").mock(
        return_value=httpx.Response(200, json=mock_user)
    )

    user = await clockify_client.get_user()
    assert user.id == "user123"
    assert user.email == "test@example.com"


@pytest.mark.asyncio
@respx.mock
async def test_unauthorized_error(clockify_client):
    """Test 401 unauthorized error mapping."""
    respx.get("https://api.clockify.test/v1/user").mock(
        return_value=httpx.Response(401, json={"message": "Unauthorized"})
    )

    with pytest.raises(ClockifyAPIError) as exc_info:
        await clockify_client.get_user()

    assert exc_info.value.code == "unauthorized"
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
@respx.mock
async def test_rate_limit_retry(clockify_client):
    """Test rate limit retry logic."""
    respx.get("https://api.clockify.test/v1/user").mock(
        side_effect=[
            httpx.Response(429, json={"message": "Rate limit"}),
            httpx.Response(200, json={"id": "user123", "email": "test@example.com", "name": "Test"}),
        ]
    )

    # Should succeed after retry
    user = await clockify_client.get_user()
    assert user.id == "user123"


@pytest.mark.asyncio
@respx.mock
async def test_create_client_success(clockify_client):
    """Test successful client creation."""
    client_data = {"name": "Test Client", "archived": False}
    mock_response = {
        "id": "client123",
        "name": "Test Client",
        "workspaceId": "ws123",
        "archived": False,
    }

    respx.post("https://api.clockify.test/v1/workspaces/ws123/clients").mock(
        return_value=httpx.Response(201, json=mock_response)
    )

    client = await clockify_client.create_client(
        "ws123", ClientCreate(**client_data)
    )
    assert client.id == "client123"
    assert client.name == "Test Client"
