from django.conf import settings
from django.http import JsonResponse

import logs
from utils import makeResponseData

import traceback


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
