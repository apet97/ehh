
from __future__ import annotations
from typing import Dict, Any
import httpx
from .base import Integration, register_integration
from app.config import settings

SLACK_API = "https://slack.com/api"

@register_integration("slack")
class SlackIntegration(Integration):
    async def execute(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        token = settings.SLACK_BOT_TOKEN
        if not token:
            return {"ok": False, "error": "SLACK_BOT_TOKEN missing"}
        if operation == "post_message":
            channel = params.get("channel")
            text = params.get("text")
            if not channel or not text:
                return {"ok": False, "error": "channel and text required"}
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    f"{SLACK_API}/chat.postMessage",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"channel": channel, "text": text},
                )
                try:
                    return r.json()
                except Exception:
                    return {"status_code": r.status_code, "text": r.text}
        return {"ok": False, "error": f"unknown operation {operation}"}

    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if payload.get("type") == "url_verification" and "challenge" in payload:
            return {"challenge": payload["challenge"]}
        return {"ok": True, "received": True}
