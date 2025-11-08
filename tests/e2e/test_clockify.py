"""
E2E tests for Clockify integration with respx mocks.
"""
import pytest
import respx
import httpx
from app.integrations.clockify_client import ClockifyClient, ClockifyAPIError
from app.integrations.clockify_types import (
    ClientCreate,
    TimeEntryCreate,
)


@pytest.fixture
def clockify_client():
    """Create a test Clockify client."""
    return ClockifyClient(
        api_key="test_api_key",
        base_url="https://api.clockify.test",
        timeout=5.0,
        max_retries=3,
    )


@pytest.mark.asyncio
@respx.mock
async def test_run_get_user_success(clockify_client):
    """Test successful user retrieval in E2E flow."""
    mock_user_response = {
        "id": "user_12345",
        "email": "developer@clankerbot.com",
        "name": "Clankerbot Developer",
        "activeWorkspace": "ws_67890",
        "settings": {
            "timeZone": "America/New_York",
            "timeFormat": "HOUR12",
        },
    }

    respx.get("https://api.clockify.test/v1/user").mock(
        return_value=httpx.Response(200, json=mock_user_response)
    )

    user = await clockify_client.get_user()

    assert user.id == "user_12345"
    assert user.email == "developer@clankerbot.com"
    assert user.name == "Clankerbot Developer"
    assert user.activeWorkspace == "ws_67890"


@pytest.mark.asyncio
@respx.mock
async def test_run_list_workspaces_success(clockify_client):
    """Test successful workspace listing in E2E flow."""
    mock_workspaces_response = [
        {
            "id": "ws_001",
            "name": "Engineering Team",
            "imageUrl": "",
            "hourlyRate": {"amount": 5000, "currency": "USD"},
        },
        {
            "id": "ws_002",
            "name": "Product Team",
            "imageUrl": "",
            "hourlyRate": {"amount": 6000, "currency": "USD"},
        },
    ]

    respx.get("https://api.clockify.test/v1/workspaces").mock(
        return_value=httpx.Response(200, json=mock_workspaces_response)
    )

    workspaces = await clockify_client.list_workspaces()

    assert len(workspaces) == 2
    assert workspaces[0].id == "ws_001"
    assert workspaces[0].name == "Engineering Team"
    assert workspaces[1].id == "ws_002"
    assert workspaces[1].name == "Product Team"


@pytest.mark.asyncio
@respx.mock
async def test_run_create_client_success(clockify_client):
    """Test successful client creation in E2E flow."""
    client_data = ClientCreate(
        name="Acme Corporation",
        archived=False,
    )

    mock_client_response = {
        "id": "client_abc123",
        "name": "Acme Corporation",
        "workspaceId": "ws_001",
        "archived": False,
    }

    respx.post("https://api.clockify.test/v1/workspaces/ws_001/clients").mock(
        return_value=httpx.Response(201, json=mock_client_response)
    )

    client = await clockify_client.create_client("ws_001", client_data)

    assert client.id == "client_abc123"
    assert client.name == "Acme Corporation"
    assert client.workspaceId == "ws_001"
    assert client.archived is False


@pytest.mark.asyncio
@respx.mock
async def test_run_create_time_entry_success(clockify_client):
    """Test successful time entry creation in E2E flow."""
    time_entry_data = TimeEntryCreate(
        start="2024-01-15T09:00:00Z",
        end="2024-01-15T10:30:00Z",
        billable=True,
        description="Working on E2E tests",
        projectId="proj_123",
        taskId=None,
    )

    mock_time_entry_response = {
        "id": "entry_xyz789",
        "description": "Working on E2E tests",
        "userId": "user_12345",
        "billable": True,
        "projectId": "proj_123",
        "timeInterval": {
            "start": "2024-01-15T09:00:00Z",
            "end": "2024-01-15T10:30:00Z",
            "duration": "PT1H30M",
        },
        "workspaceId": "ws_001",
    }

    respx.post("https://api.clockify.test/v1/workspaces/ws_001/time-entries").mock(
        return_value=httpx.Response(201, json=mock_time_entry_response)
    )

    time_entry = await clockify_client.create_time_entry("ws_001", time_entry_data)

    assert time_entry.id == "entry_xyz789"
    assert time_entry.description == "Working on E2E tests"
    assert time_entry.billable is True
    assert time_entry.projectId == "proj_123"
    assert time_entry.timeInterval.start == "2024-01-15T09:00:00Z"
    assert time_entry.timeInterval.end == "2024-01-15T10:30:00Z"


@pytest.mark.asyncio
@respx.mock
async def test_error_mapping_unauthorized(clockify_client):
    """Test 401 unauthorized error mapping in E2E flow."""
    respx.get("https://api.clockify.test/v1/user").mock(
        return_value=httpx.Response(
            401,
            json={"message": "Invalid API key"}
        )
    )

    with pytest.raises(ClockifyAPIError) as exc_info:
        await clockify_client.get_user()

    assert exc_info.value.code == "unauthorized"
    assert exc_info.value.status_code == 401
    assert "Invalid Clockify API key or token" in exc_info.value.message


@pytest.mark.asyncio
@respx.mock
async def test_error_mapping_rate_limited(clockify_client):
    """Test 429 rate limit error mapping and retry logic in E2E flow."""
    # First two requests return 429, third succeeds
    respx.get("https://api.clockify.test/v1/user").mock(
        side_effect=[
            httpx.Response(429, json={"message": "Rate limit exceeded"}),
            httpx.Response(429, json={"message": "Rate limit exceeded"}),
            httpx.Response(
                200,
                json={
                    "id": "user_12345",
                    "email": "test@example.com",
                    "name": "Test User",
                    "activeWorkspace": "ws_001",
                },
            ),
        ]
    )

    # Should succeed after retries
    user = await clockify_client.get_user()
    assert user.id == "user_12345"


@pytest.mark.asyncio
@respx.mock
async def test_error_mapping_validation_error(clockify_client):
    """Test 400 validation error mapping in E2E flow."""
    client_data = ClientCreate(name="", archived=False)  # Invalid: empty name

    respx.post("https://api.clockify.test/v1/workspaces/ws_001/clients").mock(
        return_value=httpx.Response(
            400,
            json={
                "message": "Client name cannot be empty",
                "code": 1003,
            }
        )
    )

    with pytest.raises(ClockifyAPIError) as exc_info:
        await clockify_client.create_client("ws_001", client_data)

    assert exc_info.value.code == "validation_error"
    assert exc_info.value.status_code == 400
    assert "Client name cannot be empty" in exc_info.value.message
