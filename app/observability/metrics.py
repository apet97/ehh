"""
Prometheus metrics configuration for Clankerbot.
"""
import os
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator


# Custom metrics
webhook_duplicates_total = Counter(
    "webhook_duplicates_total",
    "Total number of duplicate webhook events detected",
    ["service"],
)

rate_limits_total = Counter(
    "rate_limits_total",
    "Total number of rate limit hits (429 responses)",
    ["service"],
)

parser_fallbacks_total = Counter(
    "parser_fallbacks_total",
    "Total number of parser fallbacks from LLM to rule-based",
    ["service"],
)


def setup_metrics(app):
    """
    Setup Prometheus metrics for FastAPI app.
    Only enables if METRICS_ENABLED environment variable is set to true.

    Args:
        app: FastAPI application instance
    """
    metrics_enabled = os.getenv("METRICS_ENABLED", "").lower() in ("true", "1", "yes")

    if not metrics_enabled:
        return

    # Setup FastAPI instrumentator with service label
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=False,
        should_respect_env_var=False,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )

    # Add service label to all metrics
    instrumentator.add(
        lambda info: info.modified_duration,
        metric_name="http_request_duration_seconds",
        metric_doc="Duration of HTTP requests in seconds",
        labels={"service": "clankerbot"},
    )

    # Instrument the app
    instrumentator.instrument(app).expose(app, include_in_schema=True, tags=["observability"])
