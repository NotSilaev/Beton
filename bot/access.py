from config import settings

import functools


def hasAccess(user_id: int) -> bool:
    if user_id in settings.TELEGRAM_BOT_WHITE_LIST:
        return True
    return False


def access_checker(): 
    "Сhecks whether the user has access rights to the handler"

    def container(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                user_id = args[0].from_user.id
            except (IndexError, AttributeError):
                user_id = None

            if hasAccess(user_id):
                result = await func(*args, **kwargs)

        return wrapper
    return container
