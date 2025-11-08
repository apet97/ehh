
from fastapi import APIRouter, HTTPException, Query, Request
from app.models import HumanCommand, RunActionRequest, ScheduleRequest, ApiResponse
from app.actions import parse_human, parse_with_llm
from app.integrations.base import get_integration
from app.utils.ids import request_id as get_request_id
from app import scheduler as sched

router = APIRouter()


@router.post("/actions/parse")
async def parse(request: Request, cmd: HumanCommand, llm: bool = Query(False)):
    """Parse human command to action, optionally using LLM with fallback."""
    req_id = get_request_id(request.headers.get("x-request-id"))

    try:
        if not llm:
            action = parse_human(cmd.text)
            data = {**action.model_dump(), "parser": "rule"}
        else:
            action, parser_type = await parse_with_llm(cmd.text)
            data = {**action.model_dump(), "parser": parser_type}

        return ApiResponse.success(data=data, request_id=req_id)

    except Exception as e:
        return ApiResponse.failure(
            code="validation_error",
            message=str(e),
            request_id=req_id,
        )


@router.post("/actions/run")
async def run_action(request: Request, req: RunActionRequest):
    """Execute an action via integration."""
    req_id = get_request_id(request.headers.get("x-request-id"))

    try:
        integ = get_integration(req.integration)
        result = await integ.execute(req.operation, req.params)

        # Integrations already return structured responses
        # Wrap in ApiResponse if needed
        if isinstance(result, dict) and "ok" in result:
            # Already structured, add request ID
            result["requestId"] = req_id
            return result
        else:
            return ApiResponse.success(data=result, request_id=req_id)

    except ValueError as e:
        return ApiResponse.failure(
            code="not_found",
            message=str(e),
            request_id=req_id,
        )
    except Exception as e:
        return ApiResponse.failure(
            code="internal_error",
            message=str(e),
            request_id=req_id,
        )


@router.post("/schedules")
async def create_schedule(request: Request, req: ScheduleRequest):
    """Schedule a recurring action."""
    req_id = get_request_id(request.headers.get("x-request-id"))

    try:
        cron = req.cron.model_dump()
        sched.schedule_action(req.integration, req.operation, req.params, cron)
        return ApiResponse.success(
            data={"scheduled": True, "cron": cron},
            request_id=req_id,
        )
    except Exception as e:
        return ApiResponse.failure(
            code="internal_error",
            message=str(e),
            request_id=req_id,
        )
