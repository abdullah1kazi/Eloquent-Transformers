"""Structured logging middleware."""

import time
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    Structured logging middleware with correlation IDs.

    Logs all requests with:
    - Request method, path, query params
    - Response status code, time
    - Correlation ID for tracing
    - User ID if authenticated
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response with structured data."""
        start_time = time.time()

        # Get correlation ID
        correlation_id = getattr(request.state, "correlation_id", None)

        # Log request
        await logger.ainfo(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            correlation_id=correlation_id,
        )

        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            await logger.ainfo(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=f"{duration:.3f}s",
                correlation_id=correlation_id,
            )

            return response

        except Exception as e:
            duration = time.time() - start_time

            # Log error
            await logger.aerror(
                "request_failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration=f"{duration:.3f}s",
                correlation_id=correlation_id,
            )
            raise
