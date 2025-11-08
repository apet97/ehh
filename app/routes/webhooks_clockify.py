"""
Dedicated Clockify webhook router with validation, idempotency, and normalization.
"""
from fastapi import APIRouter, Request, Header
from typing import Optional, Dict, Any
from collections import OrderedDict
import logging
import ipaddress
from app.models import ApiResponse
from app.config import settings
from app.utils.ids import request_id as get_request_id

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory LRU cache for webhook event IDs (idempotency)
# In production, consider Redis or similar
MAX_EVENT_CACHE = 1000
_event_cache: OrderedDict[str, bool] = OrderedDict()


def _check_and_record_event(event_id: str) -> bool:
    """
    Check if event has been seen before and record it.
    Returns True if duplicate, False if new.
    """
    global _event_cache
    if event_id in _event_cache:
        return True

    # Add to cache
    _event_cache[event_id] = True

    # Evict oldest if cache is full
    if len(_event_cache) > MAX_EVENT_CACHE:
        _event_cache.popitem(last=False)

    return False


def _get_client_ip(request: Request) -> str:
    """
    Extract the real client IP from request headers or client object.
    Checks X-Forwarded-For and X-Real-IP headers first.
    """
    # Check X-Forwarded-For (may contain multiple IPs, take the first one)
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        # Take the first IP from the list
        ip = x_forwarded_for.split(",")[0].strip()
        return ip

    # Check X-Real-IP
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()

    # Fall back to direct client IP
    if request.client:
        return request.client.host

    return "unknown"


def _validate_ip_allowlist(client_ip: str, allowlist: str) -> bool:
    """
    Validate if client IP is in the CIDR allowlist.

    Args:
        client_ip: Client IP address as string
        allowlist: Comma-separated list of CIDR ranges (e.g., "192.168.1.0/24,10.0.0.0/8")

    Returns:
        True if IP is allowed or allowlist is empty, False otherwise
    """
    if not allowlist or not allowlist.strip():
        # No allowlist configured, allow all
        return True

    try:
        client_addr = ipaddress.ip_address(client_ip)
    except ValueError:
        logger.warning(f"Invalid client IP address: {client_ip}")
        return False

    # Parse CIDR ranges
    allowed_networks = []
    for cidr in allowlist.split(","):
        cidr = cidr.strip()
        if not cidr:
            continue
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            allowed_networks.append(network)
        except ValueError:
            logger.warning(f"Invalid CIDR in allowlist: {cidr}")
            continue

    # Check if client IP is in any allowed network
    for network in allowed_networks:
        if client_addr in network:
            return True

    return False


def _normalize_clockify_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize Clockify webhook payload to a standard event format.
    """
    # Try to infer event type from payload structure
    event_type = "UNKNOWN"

    # Time entry events
    if "timeInterval" in payload and "userId" in payload:
        if payload.get("timeInterval", {}).get("end") is None:
            event_type = "NEW_TIMER_STARTED"
        else:
            event_type = "TIME_ENTRY"

    # Project events
    elif "name" in payload and "tasks" in payload and "workspaceId" in payload:
        event_type = "PROJECT"

    # Approval request events
    elif "status" in payload and "owner" in payload and "dateRange" in payload:
        event_type = "APPROVAL_REQUEST"

    # Client events
    elif "name" in payload and "archived" in payload and "tasks" not in payload:
        event_type = "CLIENT"

    # Tag events
    elif "name" in payload and "archived" in payload and "workspaceId" in payload and len(payload.keys()) <= 5:
        event_type = "TAG"

    # User events
    elif "email" in payload and "settings" in payload:
        event_type = "USER"

    # Expense events
    elif "categoryId" in payload and "quantity" in payload and "billable" in payload:
        event_type = "EXPENSE"

    return {
        "eventType": event_type,
        "id": payload.get("id"),
        "workspaceId": payload.get("workspaceId"),
        "userId": payload.get("userId"),
        "rawPayload": payload,
    }


@router.post("/webhooks/clockify")
async def clockify_webhook(
    request: Request,
    x_webhook_secret: Optional[str] = Header(None),
    x_clockify_event_id: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None),
):
    """
    Receive and process Clockify webhooks with:
    - IP allowlist validation (if WEBHOOK_IP_ALLOWLIST is set)
    - Secret validation (if WEBHOOK_SHARED_SECRET is set)
    - Idempotency via X-Clockify-Event-Id
    - Event normalization
    - Structured response
    """
    req_id = get_request_id(x_request_id)

    # Validate IP allowlist if configured
    if settings.WEBHOOK_IP_ALLOWLIST:
        client_ip = _get_client_ip(request)
        if not _validate_ip_allowlist(client_ip, settings.WEBHOOK_IP_ALLOWLIST):
            logger.warning(
                f"Webhook from unauthorized IP {client_ip} blocked (request {req_id})"
            )
            return ApiResponse.failure(
                code="forbidden",
                message=f"IP address {client_ip} not in allowlist",
                request_id=req_id,
            )
        logger.debug(f"Webhook from authorized IP {client_ip}")

    # Validate webhook secret if configured
    if settings.WEBHOOK_SHARED_SECRET:
        if not x_webhook_secret:
            logger.warning(f"Webhook secret missing in request {req_id}")
            return ApiResponse.failure(
                code="unauthorized",
                message="Missing X-Webhook-Secret header",
                request_id=req_id,
            )

        if x_webhook_secret != settings.WEBHOOK_SHARED_SECRET:
            logger.warning(f"Invalid webhook secret in request {req_id}")
            return ApiResponse.failure(
                code="unauthorized",
                message="Invalid webhook secret",
                request_id=req_id,
            )

    # Parse payload
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        return ApiResponse.failure(
            code="validation_error",
            message="Invalid JSON payload",
            request_id=req_id,
        )

    # Check idempotency
    is_duplicate = False
    if x_clockify_event_id:
        is_duplicate = _check_and_record_event(x_clockify_event_id)
        if is_duplicate:
            logger.info(
                f"Duplicate webhook event {x_clockify_event_id} in request {req_id}"
            )

    # Normalize event
    try:
        normalized = _normalize_clockify_event(payload)
    except Exception as e:
        logger.error(f"Failed to normalize webhook: {e}")
        return ApiResponse.failure(
            code="internal_error",
            message="Failed to process webhook",
            request_id=req_id,
        )

    # Build response
    response_data = {
        "received": True,
        "duplicate": is_duplicate,
        "eventId": x_clockify_event_id,
        "event": normalized,
    }

    logger.info(
        f"Processed Clockify webhook: type={normalized['eventType']}, "
        f"id={normalized.get('id')}, duplicate={is_duplicate}"
    )

    return ApiResponse.success(data=response_data, request_id=req_id)
