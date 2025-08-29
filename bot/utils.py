from aiogram.types import Message, CallbackQuery
from aiogram.types.user import User

from datetime import datetime
from zoneinfo import ZoneInfo


async def respondEvent(event: Message | CallbackQuery, **kwargs) -> int:
    "Responds to various types of events: messages and callback queries."

    if isinstance(event, Message):
        bot_message = await event.answer(**kwargs)
    elif isinstance(event, CallbackQuery):
        bot_message = await event.message.edit_text(**kwargs)
        await event.answer()

    return bot_message.message_id


def getCurrentDateTime(timezone_code: str = 'UTC') -> datetime:
    timezone = ZoneInfo(timezone_code)
    current_datetime = datetime.now(tz=timezone)
    return current_datetime


def datetimeToString(dt: datetime, readable: bool = True) -> str:
    dt_string = datetime.strftime(dt, '%Y-%m-%d %H:%M:%S.%fT%z')

    if readable:
        dt_string = ''.join(dt_string.split('T')[:-1])
        dt = datetime.fromisoformat(dt_string)
        cleaned_dt = dt.replace(microsecond=0, second=0, tzinfo=None)
        dt_string = cleaned_dt.strftime("%Y-%m-%d %H:%M")

    return dt_string


def makeGreetingMessage(timezone_code: str = 'UTC') -> str:
    "Generates a welcome message based on the current time of day."

    hour = getCurrentDateTime(timezone_code).hour

    if hour in range(0, 3+1) or hour in range(22, 23+1): # 22:00 - 3:00 is night
        greeting = '🌙 Доброй ночи'
    elif hour in range(4, 11+1): # 4:00 - 11:00 is morning
        greeting = '☕️ Доброе утро'
    elif hour in range(12, 17+1): # 12:00 - 17:00 is afternoon
        greeting = '☀️ Добрый день'
    elif hour in range(18, 21+1): # 18:00 - 21:00 is evening
        greeting = '🌆 Добрый вечер'
    else:
        greeting = '👋 Здравствуйте'
    
    return greeting


def getUserName(user: User) -> str:
    "Generates a string to address the user."

    user_id: int = user.id
    username: str = user.username
    first_name: str = user.first_name
    last_name: str = user.last_name
    
    if first_name:
        if last_name:
            user_name = f'{first_name} {last_name}'
        else:
            user_name = first_name
    elif username:
        user_name = f'@{username}'
    else:
        user_name = f'User №{user_id}'

    return user_name
