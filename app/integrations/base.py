
from __future__ import annotations
from typing import Dict, Any
from abc import ABC, abstractmethod

_registry: dict[str, 'Integration'] = {}

def register_integration(name: str):
    def deco(cls):
        _registry[name] = cls()
        return cls
    return deco

def get_integration(name: str) -> 'Integration':
    if name not in _registry:
        raise ValueError(f"Unknown integration: {name}")
    return _registry[name]

def list_integrations() -> list[str]:
    return sorted(_registry.keys())

class Integration(ABC):
    @abstractmethod
    async def execute(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        ...

    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"received": True, "payload": payload}
