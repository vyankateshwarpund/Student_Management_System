"""Custom API response utilities for consistent response format."""
from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """Return a standardized success response."""
    response_data = {
        'success': True,
        'message': message,
    }
    if data is not None:
        response_data['data'] = data
    return Response(response_data, status=status_code)


def created_response(data=None, message="Created successfully"):
    """Return a standardized 201 response."""
    return success_response(data=data, message=message, status_code=status.HTTP_201_CREATED)


def error_response(message="An error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """Return a standardized error response."""
    response_data = {
        'success': False,
        'message': message,
    }
    if errors is not None:
        response_data['errors'] = errors
    return Response(response_data, status=status_code)


def not_found_response(message="Resource not found"):
    """Return a standardized 404 response."""
    return error_response(message=message, status_code=status.HTTP_404_NOT_FOUND)


def unauthorized_response(message="Authentication required"):
    """Return a standardized 401 response."""
    return error_response(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


def forbidden_response(message="You do not have permission to perform this action"):
    """Return a standardized 403 response."""
    return error_response(message=message, status_code=status.HTTP_403_FORBIDDEN)
