from django.db import models

import typing
import uuid
from decimal import Decimal


Category = typing.NewType('Category', models.Model)
ProductVariantImage = typing.NewType('ProductVariantImage', models.Model)


def getCategoryImageLocation(instance: Category, filename: str) -> str:
    image_location = f'store/categories/{instance.slug}.webp'
    return image_location
    
def getProductVariantImageLocation(instance: ProductVariantImage, filename: str) -> str:
    image_id = uuid.uuid4()
    image_location = (
        'store/products/'
        f'{instance.product_variant.product.slug}/'
        f'{instance.product_variant.slug}/'
        f'{image_id}.webp'
    )
    return image_location

def formatPrice(price: Decimal) -> str:
    "Formats the price by adding spaces between thousands and the ruble symbol."
    
    integer_part = str(price).split('.')[0]
    formatted_integer = '{0:,}'.format(int(integer_part)).replace(',', ' ')
    return f"{formatted_integer} ₽"
