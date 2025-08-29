from django.db import models
from django.utils.text import slugify
from django_resized import ResizedImageField

from apps.store import utils

import uuid


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    image = ResizedImageField(
        upload_to=utils.getCategoryImageLocation,
        force_format='WEBP',
        quality=90,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'categories'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    slug = models.SlugField(max_length=150, unique=True)
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='products'
    )

    class Meta:
        db_table = 'products'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductVariant(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    slug = models.SlugField(max_length=150, unique=True)
    title = models.CharField(max_length=100, unique=True)
    configuration = models.JSONField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField(default=0)

    class Meta:
        db_table = 'product_variants'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductVariantImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    image = ResizedImageField(
        upload_to=utils.getProductVariantImageLocation,
        force_format='WEBP',
        quality=90,
        blank=True
    )

    class Meta:
        db_table = 'product_variant_images'


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    products = models.ManyToManyField(ProductVariant, through='OrderItem')
    fullname = models.CharField(max_length=50)
    contact = models.CharField(max_length=100)
    contact_method = models.CharField(max_length=30)
    deadline = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'order_items'
        unique_together = ['order', 'product']
