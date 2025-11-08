"""
E2E tests for webhook handling with secret validation and idempotency.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_webhook_secret():
    """Reset webhook secret after each test."""
    original_secret = settings.WEBHOOK_SHARED_SECRET
    yield
    settings.WEBHOOK_SHARED_SECRET = original_secret


def test_webhook_with_secret_valid(client, monkeypatch):
    """Test webhook with valid secret."""
    # Configure secret
    monkeypatch.setenv("WEBHOOK_SHARED_SECRET", "test_secret_key_123")
    settings.WEBHOOK_SHARED_SECRET = "test_secret_key_123"

    payload = {
        "id": "entry_001",
        "userId": "user_123",
        "workspaceId": "ws_456",
        "timeInterval": {
            "start": "2024-01-15T09:00:00Z",
            "end": "2024-01-15T10:00:00Z",
        },
    }

    response = client.post(
        "/webhooks/clockify",
        json=payload,
        headers={
            "X-Webhook-Secret": "test_secret_key_123",
            "X-Clockify-Event-Id": "evt_valid_001",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["data"]["received"] is True
    assert data["data"]["duplicate"] is False
    assert data["data"]["event"]["eventType"] == "TIME_ENTRY"


def test_webhook_with_secret_invalid(client, monkeypatch):
    """Test webhook with invalid secret returns 200 with error."""
    monkeypatch.setenv("WEBHOOK_SHARED_SECRET", "correct_secret")
    settings.WEBHOOK_SHARED_SECRET = "correct_secret"

    payload = {"id": "entry_002", "userId": "user_123"}

    response = client.post(
        "/webhooks/clockify",
        json=payload,
        headers={"X-Webhook-Secret": "wrong_secret"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "unauthorized"
    assert "Invalid webhook secret" in data["error"]["message"]


def test_webhook_without_secret_when_required(client, monkeypatch):
    """Test webhook without secret when secret is required."""
    monkeypatch.setenv("WEBHOOK_SHARED_SECRET", "required_secret")
    settings.WEBHOOK_SHARED_SECRET = "required_secret"

    payload = {"id": "entry_003", "userId": "user_123"}

    response = client.post("/webhooks/clockify", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "unauthorized"
    assert "Missing X-Webhook-Secret header" in data["error"]["message"]


def test_webhook_idempotency_first_delivery(client):
    """Test first webhook delivery is not marked as duplicate."""
    # Reset secret for this test
    settings.WEBHOOK_SHARED_SECRET = None

    payload = {
        "id": "entry_unique_001",
        "userId": "user_123",
        "workspaceId": "ws_456",
        "timeInterval": {
            "start": "2024-01-15T11:00:00Z",
            "end": "2024-01-15T12:00:00Z",
        },
    }

    response = client.post(
        "/webhooks/clockify",
        json=payload,
        headers={"X-Clockify-Event-Id": "evt_first_delivery"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["data"]["duplicate"] is False
    assert data["data"]["eventId"] == "evt_first_delivery"


def test_webhook_idempotency_duplicate(client):
    """Test duplicate webhook delivery is detected."""
    settings.WEBHOOK_SHARED_SECRET = None

    payload = {
        "id": "entry_duplicate_001",
        "userId": "user_123",
        "workspaceId": "ws_456",
        "timeInterval": {
            "start": "2024-01-15T13:00:00Z",
            "end": "2024-01-15T14:00:00Z",
        },
    }

    event_id = "evt_duplicate_test"

    # First delivery
    response1 = client.post(
        "/webhooks/clockify",
        json=payload,
        headers={"X-Clockify-Event-Id": event_id},
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["data"]["duplicate"] is False

    # Second delivery (duplicate)
    response2 = client.post(
        "/webhooks/clockify",
        json=payload,
        headers={"X-Clockify-Event-Id": event_id},
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["data"]["duplicate"] is True
    assert data2["data"]["eventId"] == event_id

    # Third delivery (still duplicate)
    response3 = client.post(
        "/webhooks/clockify",
        json=payload,
        headers={"X-Clockify-Event-Id": event_id},
    )
    assert response3.status_code == 200
    data3 = response3.json()
    assert data3["data"]["duplicate"] is True


def test_webhook_event_normalization(client):
    """Test different webhook event types are normalized correctly."""
    settings.WEBHOOK_SHARED_SECRET = None

    # Test TIME_ENTRY event
    time_entry_payload = {
        "id": "entry_norm_001",
        "userId": "user_123",
        "workspaceId": "ws_456",
        "timeInterval": {
            "start": "2024-01-15T09:00:00Z",
            "end": "2024-01-15T10:00:00Z",
        },
    }

    response = client.post(
        "/webhooks/clockify",
        json=time_entry_payload,
        headers={"X-Clockify-Event-Id": "evt_time_entry"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["event"]["eventType"] == "TIME_ENTRY"
    assert data["data"]["event"]["id"] == "entry_norm_001"
    assert data["data"]["event"]["workspaceId"] == "ws_456"

    # Test PROJECT event
    project_payload = {
        "id": "proj_norm_001",
        "name": "Project Alpha",
        "workspaceId": "ws_456",
        "tasks": [],
        "clientId": "client_001",
    }

    response = client.post(
        "/webhooks/clockify",
        json=project_payload,
        headers={"X-Clockify-Event-Id": "evt_project"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["event"]["eventType"] == "PROJECT"
    assert data["data"]["event"]["id"] == "proj_norm_001"

    # Test CLIENT event
    client_payload = {
        "id": "client_norm_001",
        "name": "Acme Corp",
        "workspaceId": "ws_456",
        "archived": False,
    }

    response = client.post(
        "/webhooks/clockify",
        json=client_payload,
        headers={"X-Clockify-Event-Id": "evt_client"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["event"]["eventType"] == "CLIENT"
    assert data["data"]["event"]["id"] == "client_norm_001"

    # Test NEW_TIMER_STARTED event (no end time)
    timer_payload = {
        "id": "entry_timer_001",
        "userId": "user_123",
        "workspaceId": "ws_456",
        "timeInterval": {
            "start": "2024-01-15T15:00:00Z",
            "end": None,
        },
    }

    response = client.post(
        "/webhooks/clockify",
        json=timer_payload,
        headers={"X-Clockify-Event-Id": "evt_timer"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["event"]["eventType"] == "NEW_TIMER_STARTED"
    assert data["data"]["event"]["id"] == "entry_timer_001"
