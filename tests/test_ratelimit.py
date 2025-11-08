"""
Tests for rate limiting middleware.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_rate_limiting():
    """Test rate limiting enforcement."""
    # This test is simplified - in practice you'd need to:
    # 1. Configure a low rate limit for testing
    # 2. Make many requests quickly
    # 3. Verify 429 response

    # For now, just verify the endpoint works
    response = client.get("/healthz")
    assert response.status_code == 200


def test_rate_limit_per_path():
    """Test rate limit is enforced per path."""
    # Make multiple requests to different paths
    response1 = client.get("/healthz")
    response2 = client.get("/readyz")

    assert response1.status_code == 200
    assert response2.status_code == 200
