from rest_framework import serializers

from apps.store.models import Category, Product, ProductVariant, Order, OrderItem


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
    base_product = ProductSerializer(read_only=True)
    base_product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='base_product'
    )

    class Meta:
        model = ProductVariant
        fields = ['id', 'slug', 'base_product', 'base_product_id', 'title', 'configuration', 'price', 'stock']
        read_only_fields = ['id', 'slug']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductVariantSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        source='orderitem_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'items', 'fullname', 
            'contact', 'contact_method', 'status', 
            'deadline', 'updated_at', 'created_at'
        ]
        read_only_fields = ['id']


