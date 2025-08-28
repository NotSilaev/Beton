from django.conf import settings
from django.http import JsonResponse

import logs
from utils import makeResponseData, getClientIP, getCurrentDateTime
from cache import Cache

import json
import traceback
from datetime import datetime


class ExceptionMiddleware:
    """Intercepts all project exceptions and logs them in the log file."""

    def __init__(self, next):
        self.next = next

    def __call__(self, request):
        response = self.next(request)
        return response

    def process_exception(self, request, exception) -> JsonResponse:
        logs.addLog(
            level='error', 
            message=traceback.format_exc(),
            send_telegram_message=True
        )

        if settings.DEBUG:
            error_details = str(exception)
        else:
            error_details = None

        response_data = makeResponseData(status=500, message='Unexpected error', details=error_details)
        response = {'errors': [response_data]}
        return JsonResponse(response, status=500)


class RateLimitMiddleware:
    """Limits the number of requests per minute from one ip address."""

    def __init__(self, next):
        self.next = next

    def __call__(self, request):
        response = self.process_request(request)
        if not response:
            response = self.next(request)
        return response

    def process_request(self, request) -> None | JsonResponse:
        now = getCurrentDateTime(exclude_timezone=True)
        client_ip: str = getClientIP(request)
        reject_request = False

        cache = Cache()
        client_cache_key = f'requests:{client_ip}'
        client_requests = cache.getValue(client_cache_key)
        client_cache_key_ttl = cache.getKeyTTL(client_cache_key)

        if client_requests:
            client_requests = json.loads(client_requests)
            client_requests_count = client_requests['count']
            client_last_request = datetime.strptime(
                client_requests['last_request'],
                '%Y-%m-%d %H:%M:%S.%f'
            )

            # Selecting the delay time depending on the number of requests
            delay_levels = {
                1: {'range': range(0, 50), 'delay': 0},
                2: {'range': range(50, 100), 'delay': 0.25},
                3: {'range': range(100, 200), 'delay': 0.5},
            }
            for level in delay_levels.values():
                if client_requests_count in level['range']:
                    request_delay = (now - client_last_request).seconds
                    if request_delay < level['delay']:
                        reject_request = True
                    break
            else:
                reject_request = True

            client_requests_count += 1
        else:
            client_requests_count = 1
            client_cache_key_ttl = 60

        # Set actual client requests state
        client_requests = json.dumps({
            'count': client_requests_count, 
            'last_request': now
        }, default=str)

        cache.setValue(
            key=client_cache_key, 
            value=client_requests, 
            expire=client_cache_key_ttl
        )

        if reject_request:
            response_data = makeResponseData(status=429, message='Too Many Requests')
            return JsonResponse(response_data, status=429)
