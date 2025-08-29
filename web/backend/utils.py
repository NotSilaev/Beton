from django.http.request import HttpRequest, QueryDict
from django.utils import timezone as django_timezone

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


def getClientIP(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def makeModelFilterKwargs(filters: list, query_params: QueryDict) -> dict:
    "Compiles a dictionary of kwargs for their application in the model filter."

    filter_kwargs = {}

    for field in filters:
        value = query_params.get(field)
        if value:
            if field.endswith('_at') and ':' in value:
                date_from_str, date_to_str = value.split(':')

                try:
                    date_from = django_timezone.make_aware(datetime.strptime(date_from_str, '%Y-%m-%d'))
                    date_to = django_timezone.make_aware(datetime.strptime(date_to_str, '%Y-%m-%d'))
                except ValueError:
                    continue

                date_from = date_from.replace(hour=0, minute=0, second=0)
                date_to = date_to.replace(hour=23, minute=59, second=59)

                filter_kwargs[f"{field}__range"] = [date_from, date_to]
            else:
                filter_kwargs[field] = value

    return filter_kwargs
