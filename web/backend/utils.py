from typing import Any
from datetime import datetime
from zoneinfo import ZoneInfo


def makeResponseData(status: int, message: str = None, details: Any = None) -> dict:
    response_data = {
        'status': status,
        'message': message,
        'details': details
    }
    return response_data


def getCurrentDateTime(timezone_code: str = 'UTC', exclude_timezone: bool = False) -> datetime:
    timezone = ZoneInfo(timezone_code)
    current_datetime = datetime.now(tz=timezone)
    if exclude_timezone:
        current_datetime = current_datetime.replace(tzinfo=None)
    return current_datetime
