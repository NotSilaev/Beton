import sys
sys.path.append('../') # src/

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from exceptions import exceptions_catcher
from utils import respondEvent, makeGreetingMessage, getUserName


router = Router(name=__name__)


@router.message(CommandStart())
@router.callback_query(F.data == 'start')
@router.message(F.text & (~F.text.startswith("/")))
@exceptions_catcher()
async def start(event: Message | CallbackQuery) -> None:
    user_id = event.from_user.id
    user_name: str = getUserName(user=event.from_user)

    greeting: str = makeGreetingMessage()

    message_text = (
        f'*{greeting}*, {user_name}'
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Hello, world!', callback_data='#')

    await respondEvent(
        event,
        text=message_text, 
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup(),
    )
