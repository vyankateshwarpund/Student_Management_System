"""Custom exception handler for consistent error responses."""
from rest_framework.views import exception_handler
from rest_framework import status


def custom_exception_handler(exc, context):
    """Wrap all DRF exceptions in the standard response format."""
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {
            'success': False,
            'message': _get_error_message(response),
        }

        # If the response data contains field-level errors, include them
        if isinstance(response.data, dict):
            # Check if it's a simple {'detail': '...'} error
            if 'detail' in response.data:
                custom_response['message'] = str(response.data['detail'])
            else:
                # Field-level validation errors
                custom_response['errors'] = response.data
                custom_response['message'] = 'Validation error'
        elif isinstance(response.data, list):
            custom_response['errors'] = {'non_field_errors': response.data}
            custom_response['message'] = 'Validation error'

        response.data = custom_response

    return response


def _get_error_message(response):
    """Generate a human-readable error message based on status code."""
    status_messages = {
        status.HTTP_400_BAD_REQUEST: 'Bad request',
        status.HTTP_401_UNAUTHORIZED: 'Authentication required',
        status.HTTP_403_FORBIDDEN: 'Permission denied',
        status.HTTP_404_NOT_FOUND: 'Resource not found',
        status.HTTP_405_METHOD_NOT_ALLOWED: 'Method not allowed',
        status.HTTP_409_CONFLICT: 'Conflict',
        status.HTTP_429_TOO_MANY_REQUESTS: 'Too many requests',
        status.HTTP_500_INTERNAL_SERVER_ERROR: 'Internal server error',
    }
    return status_messages.get(response.status_code, 'An error occurred')
