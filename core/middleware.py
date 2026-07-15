"""Custom middleware. Adds request metadata used across the site."""

import logging
import time

from django.utils.deprecation import MiddlewareMixin


# Create a logger for this module.
logger = logging.getLogger(__name__)


class RequestMetaMiddleware(MiddlewareMixin):
    """Attach timing and a request id to each incoming request."""

    def process_request(self, request):
        # Store the request start time.
        request.start_time = time.time()

        # Continue request processing.
        return None

    def process_response(self, request, response):
        # Calculate request processing time.
        duration = time.time() - getattr(
            request, 'start_time', time.time()
        )

        # Add request duration to the response header.
        response['X-Request-Duration-Ms'] = str(round(duration * 1000, 2))

        # Return the modified response.
        return response
