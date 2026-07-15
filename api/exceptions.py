# Custom API exception handler for consistent JSON error responses.

from rest_framework.views import exception_handler  # DRF's default exception handler.
from rest_framework.response import Response  # Used to return API responses.
from rest_framework import status as drf_status  # HTTP status code constants.


# Custom exception handler.
def standard_exception_handler(exc, context):
    # Pass the exception to DRF's default handler.
    response = exception_handler(exc, context)

    # Check if DRF handled the exception.
    if response is not None:

        # Get the error details from the response.
        detail = response.data

        # Process dictionary-based validation errors.
        if isinstance(detail, dict):

            # Store error messages in a list.
            messages = []

            # Loop through each field and its error message.
            for key, value in detail.items():

                # If the error is a list or tuple, use the first message.
                if isinstance(value, (list, tuple)):
                    messages.append(f'{key}: {value[0]}')

                # Otherwise, use the value directly.
                else:
                    messages.append(f'{key}: {value}')

            # Join all error messages into one string.
            detail = '; '.join(messages)

        # Return a consistent JSON error format.
        response.data = {
            'error': True,
            'status_code': response.status_code,
            'detail': detail,
        }

        return response

    # Handle unexpected exceptions with a generic 500 error.
    return Response(
        {
            'error': True,
            'status_code': drf_status.HTTP_500_INTERNAL_SERVER_ERROR,
            'detail': 'An unexpected error occurred.',
        },

        # Set the HTTP response status code.
        status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
