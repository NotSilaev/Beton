import sys
sys.path.append('../') # src/

from exceptions import exceptions_catcher
from utils import respondEvent, datetimeToString, formatPrice
from api.beton import BetonAPI
from pagination import Paginator

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import dateutil
from decimal import Decimal


router = Router(name=__name__)


@router.callback_query(F.data.startswith('orders'))
@exceptions_catcher()
async def orders(event: CallbackQuery) -> None:
    orders_status = None
    if '-' in event.data:
        event_data_elements = event.data.split('-')
        orders_status = event_data_elements[1]

    if not orders_status:
        message_text = (
            '*🛒 Список заказов*\n\n'
            '🗂 Выберите статус заказов для отображения'
        )

        keyboard = InlineKeyboardBuilder()
        keyboard.button(text='⏳ Активные', callback_data='orders-active')
        keyboard.button(text='✅ Заверёшнные', callback_data='orders-completed')
        keyboard.button(text='🚫 Отклонённые', callback_data='orders-rejected')
        keyboard.button(text='⬅️ Назад', callback_data='start')
        keyboard.adjust(1, 2, 1)

    else:
        status_titles = {
            'active': '⏳ активные',
            'completed': '✅ завершённые',
            'rejected': '🚫 отклонённые',
        }
        status_title = status_titles[orders_status]

        beton_api = BetonAPI()
        orders = beton_api.getOrdersList(status=orders_status)
        orders_count = len(orders)

        if not orders:
            keyboard = InlineKeyboardBuilder()
            keyboard.button(text='⬅️ Назад', callback_data='orders')
            return await respondEvent(
                event, 
                text='📂 Нет ни одного заказа с выбранным статусом',
                reply_markup=keyboard.as_markup()
            )

        orders_cards = []
        for order in orders:
            order_id = order['id']
            fullname = order['fullname']
            created_at = datetimeToString(
                dateutil.parser.parse(order['created_at'])
            )
            orders_cards.append(
                {'text': f'{fullname} | {created_at}', 'callback_data': f'order_card-{order_id}'}
            )

        try:
            page = int(event_data_elements[2])
        except IndexError:
            page = 1
        paginator = Paginator(
            array=orders_cards, 
            offset=5, 
            page_callback=f'orders-{orders_status}', 
            back_callback='orders'
        )
        keyboard = paginator.getPageKeyboard(page)

        message_text = (
            '*🛒 Список заказов*\n\n'
            f'🗃️ Количество заказов: *{orders_count}* (статус: {status_title})'
        )

    await respondEvent(
        event,
        text=message_text, 
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(F.data.startswith('order_card'))
@exceptions_catcher()
async def order_card(event: CallbackQuery) -> None:
    order_id = '-'.join(event.data.split('-')[1:])

    beton_api = BetonAPI()
    order = beton_api.getOrder(order_id)

    fullname = order['fullname']
    contact = order['contact']
    contact_method = order['contact_method']

    items = order['items']
    order_cart_products = []
    cart_total_price = 0
    for i, item in enumerate(items):
        product = item['product'] 
        quantity = Decimal(item['quantity'])
        price = Decimal(product['price'])
        total_price = price * quantity
        cart_total_price += total_price
        configuration = ', '.join(f"{k}: {v}" for k, v in product['configuration'].items())
        order_cart_products.append(
            f'*{i+1}.* '
            f'{product["title"]} ({configuration}) [{quantity} шт.] — '
            f'*{formatPrice(total_price)}* ({formatPrice(price)} / шт.)'
        )
    order_cart = '\n\n'.join(order_cart_products)

    updated_at = datetimeToString(
        dateutil.parser.parse(order['updated_at'])
    )
    created_at = datetimeToString(
        dateutil.parser.parse(order['created_at'])
    )

    status = order['status']
    status_emojis = {
        'active': '⏳',
        'completed': '✅',
        'rejected': '🚫',
    }
    status_emoji = status_emojis[status]

    message_text = (
        f'*🛒 Карточка заказа ({status_emoji})*\n\n'

        f'*🆔 Номер заказа:* `{order_id}`\n\n'

        f'🤵🏼 Заказчик: *{fullname}*\n'
        f'📞 Номер телефона: `{contact}`\n'
        f'📲 Способ связи: *{contact_method}*\n\n'

        '*🛒 Состав заказа:*\n'
        f'{order_cart}\n\n'

        f'💰 Сумма заказа: *{formatPrice(cart_total_price)}*\n\n'

        f'Обновлён: *{updated_at}*\n'
        f'Сформирован: *{created_at}*'
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='⬅️ Назад', callback_data='orders')

    await respondEvent(
        event,
        text=message_text, 
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup(),
    )
