from typing import Any


def makeResponseData(status: int, message: str = None, details: Any = None) -> dict:
    response_data = {
        'status': status,
        'message': message,
        'details': details
    }
    return response_data
