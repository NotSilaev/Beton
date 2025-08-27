from django.db.models import Q
from django.http import JsonResponse

from utils import makeResponseData, getCurrentDateTime

from apps.auth.models import AuthToken
from apps.auth.utils import hashAuthToken

import secrets


def checkAuthToken(view_func):
    "Verifies the authenticity of the transmitted authorization token before executing the request."

    def wrapper(*args, **kwargs):
        request = args[1]
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            plain_token = auth_header.split()[1]

            potential_tokens = AuthToken.objects.filter(
                Q(expires_at__gt=getCurrentDateTime()) | Q(expires_at__isnull=True), revoked=False
            ).values('token_hash', 'salt_hex')

            for token_record in potential_tokens:
                salt = bytes.fromhex(token_record['salt_hex'])
                cadidate_token_hash, salt_hex = hashAuthToken(plain_token, salt)

                if secrets.compare_digest(cadidate_token_hash, token_record['token_hash']):
                    result = view_func(*args, **kwargs)
                    return result

        response_data = makeResponseData(status=403, message='Invalid auth token')
        return JsonResponse(response_data, status=403)

    return wrapper
