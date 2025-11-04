"""Correlation ID middleware for request tracing."""

import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Add correlation ID to requests for distributed tracing.

    This enables tracking requests across multiple services and log aggregation.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add correlation ID to request and response."""
        # Check if correlation ID exists in headers
        correlation_id = request.headers.get("X-Correlation-ID")

        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Store in request state for access in routes
        request.state.correlation_id = correlation_id

        # Call next middleware/route
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response
