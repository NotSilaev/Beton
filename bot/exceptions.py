from config import settings
from logs import addLog
from api.telegram import TelegramAPI

import traceback
import functools


def exceptions_catcher(): 
    """
    Catches all the exceptions in functions.
    If exception is noticed, it adds a new note to a logfile 
    and sends a telegram message for user about unsuccessful request.
    """

    def container(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                event = args[0]
                user_id = event.from_user.id
            except (IndexError, AttributeError):
                user_id = None

            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                log_text = f'{e}\n\n{traceback.format_exc()}'
                addLog(level='error', text=log_text)

                if user_id:                 
                    message_text = (
                        "*❌ Произошла неизвестная ошибка.*\n\n"
                        "Попробуйте повторить Ваш запрос, если ничего не изменится — немного подождите.\n\n"
                        "*🙏 Приносим извинения за предоставленные неудобства.*"
                    )

                    telegram_api = TelegramAPI(settings.TELEGRAM_BOT_TOKEN)
                    telegram_api.sendRequest(
                        request_method='POST',
                        api_method='sendMessage',
                        parameters={
                            'chat_id': user_id,
                            'text': message_text,
                            'parse_mode': 'Markdown',
                        },
                    )
        return wrapper
    return container
