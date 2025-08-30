from rest_framework import serializers

from apps.store.models import Category, Product, ProductVariant, Order


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title', 'description', 'image']
        read_only_fields = ['id', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'slug', 'title', 'description', 'category']
        read_only_fields = ['id', 'slug']
        
        
class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'slug', 'title', 'configuration', 'price', 'stock']
        read_only_fields = ['id', 'slug']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'products', 'fullname', 'contact', 'contact_method', 'status', 'deadline', 'updated_at', 'created_at'
        ]
        read_only_fields = ['id']
