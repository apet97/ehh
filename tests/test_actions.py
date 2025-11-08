"""
Tests for action parsing.
"""
import pytest
from app.actions import parse_human, parse_with_llm
from app.models import Action


def test_parse_human_basic():
    """Test basic rule-based parsing."""
    result = parse_human("clockify.get_user")
    assert result.integration == "clockify"
    assert result.operation == "get_user"
    assert result.params == {}


def test_parse_human_with_params():
    """Test rule-based parsing with parameters."""
    result = parse_human("clockify.create_client workspaceId=123 name=TestClient")
    assert result.integration == "clockify"
    assert result.operation == "create_client"
    assert result.params == {"workspaceId": "123", "name": "TestClient"}


def test_parse_human_invalid():
    """Test rule-based parsing with invalid input."""
    with pytest.raises(ValueError, match="Expected 'integration.operation'"):
        parse_human("invalid_command")


@pytest.mark.asyncio
async def test_parse_with_llm_fallback(monkeypatch):
    """Test LLM parsing fallback to rule parser on LLM failure."""
    from app.llm import client as llm_client

    # Mock LLM to raise an error
    async def mock_chat(*args, **kwargs):
        raise RuntimeError("LLM API error")

    monkeypatch.setattr(llm_client, "chat", mock_chat)

    # Should fall back to rule parser
    action, parser_type = await parse_with_llm("clockify.get_user")
    assert action.integration == "clockify"
    assert action.operation == "get_user"
    assert parser_type == "fallback"


@pytest.mark.asyncio
async def test_parse_with_llm_success(monkeypatch):
    """Test successful LLM parsing."""
    from app.llm import client as llm_client

    # Mock LLM to return valid JSON
    async def mock_chat(*args, **kwargs):
        return {
            "choices": [
                {
                    "message": {
                        "content": '{"integration": "clockify", "operation": "get_user", "params": {}}'
                    }
                }
            ]
        }

    monkeypatch.setattr(llm_client, "chat", mock_chat)

    action, parser_type = await parse_with_llm("Get my Clockify user info")
    assert action.integration == "clockify"
    assert action.operation == "get_user"
    assert parser_type == "llm"
