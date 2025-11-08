
from __future__ import annotations
from typing import Dict, Any
import logging
from app.integrations.base import Integration, register_integration
from app.integrations.clockify_client import ClockifyClient, ClockifyAPIError
from app.integrations.clockify_types import ClientCreate, TimeEntryCreate, ProjectCreate

logger = logging.getLogger(__name__)


@register_integration("clockify")
class ClockifyIntegration(Integration):
    """
    Clockify integration using the typed async client.
    Maps operations to client methods and exceptions to structured errors.
    """

    def __init__(self):
        try:
            self.client = ClockifyClient()
        except ValueError as e:
            logger.warning(f"Clockify client initialization failed: {e}")
            self.client = None

    async def execute(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Clockify operation with error mapping."""
        if not self.client:
            return {
                "ok": False,
                "error": {
                    "code": "unauthorized",
                    "message": "Clockify API key or token not configured",
                },
            }

        try:
            if operation == "get_user":
                user = await self.client.get_user()
                return {"ok": True, **user.model_dump()}

            if operation == "list_workspaces":
                workspaces = await self.client.list_workspaces()
                return {"ok": True, "workspaces": [w.model_dump() for w in workspaces]}

            if operation == "get_workspace":
                workspace_id = params.get("workspaceId")
                if not workspace_id:
                    return {
                        "ok": False,
                        "error": {
                            "code": "validation_error",
                            "message": "workspaceId required",
                        },
                    }
                workspace = await self.client.get_workspace(workspace_id)
                return {"ok": True, **workspace.model_dump()}

            if operation == "create_client":
                workspace_id = params.get("workspaceId")
                body = params.get("body")
                if not workspace_id or not isinstance(body, dict):
                    return {
                        "ok": False,
                        "error": {
                            "code": "validation_error",
                            "message": "workspaceId and body required",
                        },
                    }
                client_create = ClientCreate(**body)
                client = await self.client.create_client(workspace_id, client_create)
                return {"ok": True, **client.model_dump()}

            if operation == "list_clients":
                workspace_id = params.get("workspaceId")
                if not workspace_id:
                    return {
                        "ok": False,
                        "error": {
                            "code": "validation_error",
                            "message": "workspaceId required",
                        },
                    }
                clients = await self.client.list_clients(workspace_id)
                return {"ok": True, "clients": [c.model_dump() for c in clients]}

            if operation == "list_projects":
                workspace_id = params.get("workspaceId")
                if not workspace_id:
                    return {
                        "ok": False,
                        "error": {
                            "code": "validation_error",
                            "message": "workspaceId required",
                        },
                    }
                projects = await self.client.list_projects(workspace_id)
                return {"ok": True, "projects": [p.model_dump() for p in projects]}

            if operation == "create_project":
                workspace_id = params.get("workspaceId")
                body = params.get("body")
                if not workspace_id or not isinstance(body, dict):
                    return {
                        "ok": False,
                        "error": {
                            "code": "validation_error",
                            "message": "workspaceId and body required",
                        },
                    }
                project_create = ProjectCreate(**body)
                project = await self.client.create_project(workspace_id, project_create)
                return {"ok": True, **project.model_dump()}

            if operation == "create_time_entry":
                workspace_id = params.get("workspaceId")
                body = params.get("body")
                if not workspace_id or not isinstance(body, dict):
                    return {
                        "ok": False,
                        "error": {
                            "code": "validation_error",
                            "message": "workspaceId and body required",
                        },
                    }
                entry_create = TimeEntryCreate(**body)
                entry = await self.client.create_time_entry(workspace_id, entry_create)
                return {"ok": True, **entry.model_dump()}

            return {
                "ok": False,
                "error": {
                    "code": "not_found",
                    "message": f"Unknown operation: {operation}",
                },
            }

        except ClockifyAPIError as e:
            return {
                "ok": False,
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "status_code": e.status_code,
                },
            }
        except Exception as e:
            logger.error(f"Clockify operation failed: {e}", exc_info=True)
            return {
                "ok": False,
                "error": {
                    "code": "internal_error",
                    "message": str(e),
                },
            }

    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Clockify webhook (legacy endpoint).
        Use the dedicated /webhooks/clockify router for production.
        """
        event_type = payload.get("event") or payload.get("type")
        # Normalize common samples
        if "NEW_TIME_ENTRY" in str(event_type) or (
            "timeInterval" in payload
            and "userId" in payload
            and "projectId" in payload
        ):
            return {
                "ok": True,
                "event": "TIME_ENTRY",
                "id": payload.get("id"),
                "userId": payload.get("userId"),
            }
        if "NEW_PROJECT" in str(event_type) or (
            "name" in payload and "clientId" in payload and "tasks" in payload
        ):
            return {
                "ok": True,
                "event": "PROJECT",
                "id": payload.get("id"),
                "name": payload.get("name"),
            }
        if "APPROVAL" in str(event_type) or (
            "status" in payload and "owner" in payload and "dateRange" in payload
        ):
            return {
                "ok": True,
                "event": "APPROVAL_REQUEST",
                "id": payload.get("id"),
                "status": payload.get("status", {}),
            }
        # Fallback echo for other webhooks
        return {"ok": True, "received": True}
