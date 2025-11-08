
from __future__ import annotations
from typing import Dict, Any, List, Optional
import httpx
import asyncio
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 20.0,
        max_retries: int = 3,
    ):
        self.base_url = (base_url or settings.LLM_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.model = model or settings.LLM_MODEL
        self.timeout = timeout
        self.max_retries = max_retries

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Call LLM with exponential backoff retry on 429/5xx errors.
        Raises RuntimeError on missing API key or persistent failures.
        """
        if not self.api_key:
            raise RuntimeError("LLM API key missing")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }

        last_exception = None
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    r = await client.post(url, headers=headers, json=payload)

                    # Retry on 429 (rate limit) or 5xx (server errors)
                    if r.status_code == 429 or r.status_code >= 500:
                        delay = (2 ** attempt) * 0.5  # 0.5s, 1s, 2s
                        logger.warning(
                            f"LLM returned {r.status_code}, retrying in {delay}s (attempt {attempt + 1}/{self.max_retries})"
                        )
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(delay)
                            continue

                    r.raise_for_status()
                    return r.json()

            except httpx.TimeoutException as e:
                last_exception = e
                logger.warning(
                    f"LLM timeout on attempt {attempt + 1}/{self.max_retries}"
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep((2 ** attempt) * 0.5)
                    continue
            except httpx.HTTPStatusError as e:
                # Non-retriable errors (4xx except 429)
                if e.response.status_code < 500 and e.response.status_code != 429:
                    raise RuntimeError(f"LLM API error: {e.response.status_code}") from e
                last_exception = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep((2 ** attempt) * 0.5)
                    continue
            except Exception as e:
                last_exception = e
                logger.error(f"LLM call failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep((2 ** attempt) * 0.5)
                    continue

        # All retries exhausted
        raise RuntimeError(
            f"LLM call failed after {self.max_retries} attempts"
        ) from last_exception


client = LLMClient()
