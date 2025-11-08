"""
Pydantic models for Clockify API types.
Minimal subset based on common operations.
"""
from pydantic import BaseModel
from typing import Optional, List


class ClockifyUser(BaseModel):
    """User model."""
    id: str
    email: str
    name: str
    activeWorkspace: Optional[str] = None
    status: Optional[str] = None


class ClockifyWorkspace(BaseModel):
    """Workspace model."""
    id: str
    name: str
    hourlyRate: Optional[dict] = None
    memberships: Optional[List[dict]] = None


class ClientCreate(BaseModel):
    """Request body for creating a client."""
    name: str
    archived: bool = False


class ClockifyClient(BaseModel):
    """Client model."""
    id: str
    name: str
    workspaceId: str
    archived: bool = False


class TimeInterval(BaseModel):
    """Time interval for time entries."""
    start: str  # ISO 8601
    end: Optional[str] = None  # ISO 8601, null if timer is running
    duration: Optional[str] = None  # ISO 8601 duration


class TimeEntryCreate(BaseModel):
    """Request body for creating a time entry."""
    start: str  # ISO 8601
    end: Optional[str] = None
    billable: Optional[bool] = None
    description: Optional[str] = None
    projectId: Optional[str] = None
    taskId: Optional[str] = None
    tagIds: Optional[List[str]] = None


class ClockifyTimeEntry(BaseModel):
    """Time entry model."""
    id: str
    description: Optional[str] = None
    userId: str
    workspaceId: str
    projectId: Optional[str] = None
    taskId: Optional[str] = None
    timeInterval: TimeInterval
    billable: bool = False
    isLocked: bool = False


class ProjectCreate(BaseModel):
    """Request body for creating a project."""
    name: str
    clientId: Optional[str] = None
    color: Optional[str] = None
    billable: bool = False
    isPublic: bool = True
    archived: bool = False


class ClockifyProject(BaseModel):
    """Project model."""
    id: str
    name: str
    workspaceId: str
    clientId: Optional[str] = None
    clientName: Optional[str] = None
    color: Optional[str] = None
    archived: bool = False
    billable: bool = False


class ApprovalRequestStatus(BaseModel):
    """Approval request status."""
    state: str  # PENDING, APPROVED, REJECTED
    updatedBy: Optional[str] = None
    updatedByUserName: Optional[str] = None
    updatedAt: Optional[str] = None
    note: Optional[str] = None


class ClockifyApprovalRequest(BaseModel):
    """Approval request model."""
    id: str
    workspaceId: str
    dateRange: dict
    owner: dict
    status: ApprovalRequestStatus
