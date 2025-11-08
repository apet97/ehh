
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class HumanCommand(BaseModel):
    text: str


class Action(BaseModel):
    integration: str
    operation: str
    params: Dict[str, Any] = Field(default_factory=dict)


class RunActionRequest(Action):
    pass


class CronSpec(BaseModel):
    year: Optional[str] = None
    month: Optional[str] = None
    day: Optional[str] = None
    week: Optional[str] = None
    day_of_week: Optional[str] = None
    hour: Optional[str] = None
    minute: Optional[str] = None
    second: Optional[str] = None


class ScheduleRequest(Action):
    cron: CronSpec


class WebhookEnvelope(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)


# API Response Envelopes
class ApiError(BaseModel):
    """Structured error response."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ApiResponse(BaseModel):
    """Standard API response envelope."""
    ok: bool
    data: Optional[Any] = None
    error: Optional[ApiError] = None
    requestId: str = ""

    @classmethod
    def success(cls, data: Any = None, request_id: str = "") -> "ApiResponse":
        """Create a success response."""
        return cls(ok=True, data=data, requestId=request_id)

    @classmethod
    def failure(
        cls,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: str = "",
    ) -> "ApiResponse":
        """Create an error response."""
        return cls(
            ok=False,
            error=ApiError(code=code, message=message, details=details),
            requestId=request_id,
        )
