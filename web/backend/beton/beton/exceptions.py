from rest_framework.views import exception_handler
from rest_framework.exceptions import ErrorDetail

from utils import makeResponseData


def getDetails(value: ErrorDetail | list | tuple | dict) -> str:
    """Recursively extract human-readable message from error value."""

    if isinstance(value, ErrorDetail):
        return str(value)
    elif isinstance(value, (list, tuple)):
        return [getDetails(item) for item in value]
    elif isinstance(value, dict):
        return {k: getDetails(v) for k, v in value.items()}
    return str(value)


def validationExceptionsHandler(exception, context):
    response = exception_handler(exception, context)

    if response is not None:
        # Build standardized error format
        errors = []

        if isinstance(response.data, list):
            for item in response.data:
                response_data = makeResponseData(
                    response.status_code, 
                    message='Validation error', 
                    details=getDetails(item)
                )
                errors.append(response_data)

        elif isinstance(response.data, dict):
            for key, value in response.data.items():
                if key in ('non_field_errors', 'detail'):
                    message = 'Validation error'
                else:
                    message = f"{key.replace('_', ' ').title()} error"

                response_data = makeResponseData(response.status_code, message, details=getDetails(value))
                errors.append(response_data)

        else:
            response_data = makeResponseData(
                response.status_code, 
                message='Unexpected error',
                details=str(response.data)
            )
            errors.append(response_data)

        response.data = {'errors': errors}

    return response
