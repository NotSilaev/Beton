from config import project_settings
from api.telegram import TelegramAPI

import os
import datetime
import logging


# Create a custom formatter
time_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(fmt='%(asctime)s [%(levelname)s] - %(message)s', datefmt=time_format)

# Create a logger and set the custom formatter
logger = logging.getLogger('custom_logger')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def addLog(level: str, message: str, details: str = None, send_telegram_message: bool = False) -> None:
    """
    Adds new log to file, console and telegram chat.

    :param level: log level (`info`, 'debug', 'warning', 'error', 'critical').
    :param message: log message.
    :param send_telegram_message: determines whether a log will be sent to telegram chat.
    """
    
    # Write the log into the log file
    now = datetime.datetime.now()
    path = f"logs/{now.year}/{now.month}/{now.day}/"
    filename = path + f"log-{now.hour}.log"

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(filename, 'a') as file:
        separator_string = f"\n\n{'='*50}\n\n"
        log = (
            "{0} [{1}]\n\n"
            "Exception message:\n{2}\n"
            "Exception details:\n{3}" 
            + separator_string
        )
        try:
            file.write(log.format(now, level, message, details))
        except:
            message = message.encode('utf-8')
            details = details.encode('utf-8')
            file.write(log.format(now, level, message, details))

    # Send the log message to Telegram Bot users
    if send_telegram_message:
        bot_token: str = project_settings.TELEGRAM_LOGS_BOT_TOKEN
        recepients: list = project_settings.TELEGRAM_LOGS_BOT_USERS

        telegram_api = TelegramAPI(bot_token)

        disable_notification = True
        if level.lower() in ['error', 'critical']:
            disable_notification = False

        for user_id in recepients:
            response = telegram_api.sendRequest(
                request_method='POST',
                api_method='sendMessage',
                parameters={
                    'chat_id': user_id,
                    'message': (
                        f"*[{level.upper()}]* _({now})_\n\n"
                        f"*Expection message:*\n`{message}`\n"
                        f"*Exceptions details:*\n`{details}`"
                    ),
                    'parse_mode': 'Markdown',
                    'disable_notification': disable_notification,
                }
            )
            
            if response['code'] == 400:
                addLog(
                    level='error', 
                    message=(
                        "Telegram message with last error log didn't send.\n",
                        f"API response: {response['text']}"
                    )
                )
