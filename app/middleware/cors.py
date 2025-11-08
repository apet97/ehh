"""
CORS middleware configuration with sensible defaults.
"""
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def setup_cors(app):
    """
    Setup CORS middleware with configuration from settings.

    If CORS_ORIGINS is not set or empty, defaults to localhost:3000,localhost:8080
    for development convenience.

    Args:
        app: FastAPI application instance
    """
    cors_origins = settings.CORS_ORIGINS.strip()

    if not cors_origins:
        # Default to common development ports
        origins = ["http://localhost:3000", "http://localhost:8080"]
        logger.info("CORS_ORIGINS not set, using defaults: localhost:3000, localhost:8080")
    else:
        # Parse comma-separated origins
        origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
        logger.info(f"CORS configured with origins: {origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return origins
