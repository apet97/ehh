
from typing import Dict, Any, Tuple
from .models import Action
import json
import logging
from app.integrations.base import list_integrations
from app.llm import client as llm_client

logger = logging.getLogger(__name__)


def parse_human(text: str) -> Action:
    """
    Parse rule-based action format: integration.operation param1=value1 param2=value2
    """
    text = text.strip()
    head, *rest = text.split()
    if "." not in head:
        raise ValueError("Expected 'integration.operation' at start")
    integration, operation = head.split(".", 1)
    params: Dict[str, Any] = {}
    for token in rest:
        if "=" in token:
            k, v = token.split("=", 1)
            params[k] = v
    return Action(integration=integration, operation=operation, params=params)


async def parse_with_llm(text: str) -> Tuple[Action, str]:
    """
    Parse action using LLM with fallback to rule parser.
    Returns (Action, parser_type) where parser_type is "llm" or "fallback".
    """
    try:
        # Ask LLM to extract JSON with integration, operation, params.
        choices = ", ".join(list_integrations()) or "slack"
        sys = (
            "You turn a user instruction into a JSON action for an automation hub. "
            f"Allowed integrations: {choices}. "
            "Output JSON only with keys: integration, operation, params. No prose."
        )
        user = f"Instruction: {text}"
        resp = await llm_client.chat([
            {"role": "system", "content": sys},
            {"role": "user", "content": user},
        ], temperature=0)
        content = resp["choices"][0]["message"]["content"]

        # Try to locate and parse JSON
        start = content.find("{")
        end = content.rfind("}")
        if start >= 0 and end > start:
            obj = json.loads(content[start:end+1])
            # Validate required fields
            if "integration" in obj and "operation" in obj:
                action = Action(
                    integration=obj["integration"],
                    operation=obj["operation"],
                    params=obj.get("params", {})
                )
                return action, "llm"

        raise ValueError("LLM response missing required fields")

    except Exception as e:
        # Fallback to rule parser
        logger.warning(f"LLM parsing failed: {e}, falling back to rule parser")
        try:
            action = parse_human(text)
            return action, "fallback"
        except Exception as fallback_error:
            logger.error(f"Both LLM and rule parser failed: {fallback_error}")
            raise ValueError(
                f"Could not parse action. LLM error: {e}, Rule parser error: {fallback_error}"
            )
