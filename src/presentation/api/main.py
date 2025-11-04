"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from ...infrastructure.config import get_settings
from .middleware.correlation_id import CorrelationIdMiddleware
from .middleware.logging import StructuredLoggingMiddleware
from .schemas import ErrorResponse, HealthResponse
from .v1 import audio
from datetime import datetime

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan events.

    Demonstrates:
    - Startup/shutdown hooks
    - Resource initialization
    - Graceful shutdown
    """
    # Startup
    logger.info("application_starting", version=app.version)

    # TODO: Initialize database connection pool
    # TODO: Initialize ML models (load once)
    # TODO: Connect to message queue

    yield

    # Shutdown
    logger.info("application_shutting_down")

    # TODO: Close database connections
    # TODO: Close Redis connections
    # TODO: Cleanup resources


# Create FastAPI application
settings = get_settings()

app = FastAPI(
    title="Eloquent Transformers API",
    description=(
        "Enterprise-grade Audio Intelligence Platform using transformers "
        "for audio transcription, semantic search, and analysis."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(StructuredLoggingMiddleware)

# Mount Prometheus metrics
if settings.enable_metrics:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation Error",
            detail=str(exc.errors()),
            code="VALIDATION_ERROR",
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    correlation_id = getattr(request.state, "correlation_id", None)

    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        correlation_id=correlation_id,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred",
            code="INTERNAL_ERROR",
        ).model_dump(),
    )


# Health check endpoints
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Health check",
    description="Check if the service is healthy",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Used by:
    - Load balancers
    - Kubernetes readiness probes
    - Monitoring systems
    """
    return HealthResponse(
        status="healthy",
        version=app.version,
        timestamp=datetime.now(),
        checks={
            "api": "ok",
            # TODO: Check database connection
            # TODO: Check Redis connection
            # TODO: Check ML model availability
        },
    )


@app.get(
    "/ready",
    tags=["health"],
    summary="Readiness check",
    description="Check if the service is ready to accept traffic",
)
async def readiness_check() -> dict:
    """
    Readiness check endpoint.

    Returns 200 if service is ready to handle requests,
    503 if still initializing or degraded.
    """
    # TODO: Check if ML models are loaded
    # TODO: Check if database is accessible
    # TODO: Check if required services are available

    return {"status": "ready"}


# Include routers
app.include_router(audio.router, prefix=settings.api_v1_prefix)


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": "Eloquent Transformers API",
        "version": app.version,
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics" if settings.enable_metrics else None,
    }
