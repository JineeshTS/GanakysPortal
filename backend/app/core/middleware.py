"""
Request ID middleware for request tracing.
WBS Reference: FIX-WBS Task 1.3.1.2
"""
import uuid
from contextvars import ContextVar
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable to store request ID across async calls
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    """
    Get the current request ID.

    Can be used in any async context to get the request ID
    for logging or other tracking purposes.
    """
    return request_id_var.get()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that assigns a unique ID to each request.

    The request ID is:
    - Generated if not provided in X-Request-ID header
    - Stored in context variable for access anywhere in request lifecycle
    - Added to response headers for client correlation
    """

    REQUEST_ID_HEADER = "X-Request-ID"

    async def dispatch(self, request: Request, call_next) -> Response:
        # Get request ID from header or generate new one
        request_id = request.headers.get(self.REQUEST_ID_HEADER)
        if not request_id:
            request_id = str(uuid.uuid4())

        # Store in context variable for access in handlers/services
        token = request_id_var.set(request_id)

        try:
            # Process request
            response = await call_next(request)

            # Add request ID to response headers
            response.headers[self.REQUEST_ID_HEADER] = request_id

            return response
        finally:
            # Reset context variable
            request_id_var.reset(token)
