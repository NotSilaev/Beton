from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from config import project_settings
from api.telegram import TelegramAPI

from apps.store.models import Order
from apps.store.utils import formatPrice


@receiver(post_save, sender=Order)
def OrderPostSaveHandler(sender, instance, created, **kwargs):
    "Sends a notification to the telegram bot about the order creation."

    if not created:
        return

    def processAfterTransactionCommit():
        order_cart_products = []
        cart_total_price = 0
        for i, order_item in enumerate(instance.orderitem_set.all()):
            product = order_item.product
            quantity = order_item.quantity
            total_price = product.price * quantity
            cart_total_price += total_price
            configuration = ', '.join(f"{k}: {v}" for k, v in product.configuration.items())
            order_cart_products.append(
                f'*{i+1}.* '
                f'{product.title} ({configuration}) [{quantity} шт.] — '
                f'*{formatPrice(total_price)}* ({formatPrice(product.price)} / шт.)'
            )
        order_cart = '\n\n'.join(order_cart_products)

        message_text = (
            '*🔔 Получен новый заказ*\n\n'

            f'🤵🏼 Заказчик: *{instance.fullname}*\n'
            f'📞 Номер телефона: `{instance.contact}`\n'
            f'📲 Способ связи: *{instance.contact_method}*\n\n'

            '*🛒 Состав заказа:*\n'
            f'{order_cart}\n\n'
            
            f'💰 Сумма заказа: *{formatPrice(cart_total_price)}*'
        )

        telegram_api = TelegramAPI(bot_token=project_settings.TELEGRAM_ORDERS_BOT_TOKEN)
        for user_id in project_settings.TELEGRAM_ORDERS_BOT_USERS:
            telegram_api.sendRequest(
                request_method='POST',
                api_method='sendMessage',
                parameters={
                    'chat_id': user_id,
                    'text': message_text,
                    'parse_mode': 'Markdown'
                }
            )

    transaction.on_commit(processAfterTransactionCommit)


