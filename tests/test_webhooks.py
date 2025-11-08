"""
Tests for webhook handling and idempotency.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_webhook_idempotency():
    """Test webhook idempotency with X-Clockify-Event-Id."""
    payload = {
        "id": "entry123",
        "userId": "user123",
        "workspaceId": "ws123",
        "timeInterval": {"start": "2024-01-01T10:00:00Z", "end": "2024-01-01T11:00:00Z"},
    }

    event_id = "evt_12345"

    # First request
    response1 = client.post(
        "/webhooks/clockify",
        json=payload,
        headers={"X-Clockify-Event-Id": event_id},
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["ok"] is True
    assert data1["data"]["duplicate"] is False

    # Second request with same event ID
    response2 = client.post(
        "/webhooks/clockify",
        json=payload,
        headers={"X-Clockify-Event-Id": event_id},
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["ok"] is True
    assert data2["data"]["duplicate"] is True


def test_webhook_secret_validation(monkeypatch):
    """Test webhook secret validation."""
    monkeypatch.setenv("WEBHOOK_SHARED_SECRET", "my_secret")

    # Reload settings after monkeypatch
    from app.config import settings
    settings.WEBHOOK_SHARED_SECRET = "my_secret"

    payload = {"id": "entry123"}

    # Without secret
    response = client.post("/webhooks/clockify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "unauthorized"

    # With wrong secret
    response = client.post(
        "/webhooks/clockify",
        json=payload,
        headers={"X-Webhook-Secret": "wrong_secret"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False

    # With correct secret
    response = client.post(
        "/webhooks/clockify",
        json=payload,
        headers={"X-Webhook-Secret": "my_secret"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True

    # Clean up
    settings.WEBHOOK_SHARED_SECRET = None


def test_webhook_event_normalization():
    """Test webhook event normalization."""
    # Time entry payload
    time_entry_payload = {
        "id": "entry123",
        "userId": "user123",
        "workspaceId": "ws123",
        "timeInterval": {
            "start": "2024-01-01T10:00:00Z",
            "end": "2024-01-01T11:00:00Z",
        },
    }

    response = client.post("/webhooks/clockify", json=time_entry_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["data"]["event"]["eventType"] == "TIME_ENTRY"

    # Project payload
    project_payload = {
        "id": "proj123",
        "name": "Test Project",
        "workspaceId": "ws123",
        "tasks": [],
    }

    response = client.post("/webhooks/clockify", json=project_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["data"]["event"]["eventType"] == "PROJECT"
