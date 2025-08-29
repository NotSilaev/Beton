from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from django.http import Http404
from django.db import transaction

from utils import makeResponseData, makeModelFilterKwargs

from apps.auth.access import checkAuthToken
from apps.store.models import Category, Product, ProductVariant, ProductVariantImage, Order, OrderItem
from apps.store.serializers import (
    CategorySerializer, 
    ProductSerializer, 
    ProductVariantSerializer, 
    OrderSerializer
)
from apps.store.schemas import ProductListOffsetScheme

import json
import uuid
from pydantic import ValidationError


class CategoryList(APIView):
    def get(self, request: Request) -> Response:
        categories = Category.objects.all()
        serialized_categories = CategorySerializer(categories, many=True).data
        response_data = makeResponseData(
            status=200,
            message='OK',
            details={'categories': serialized_categories}
        )
        return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def post(self, request: Request) -> Response:
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = makeResponseData(
                status=201,
                message='Created',
                details={'category': serializer.data}
            )
            return Response(response_data, status=status.HTTP_201_CREATED)


class CategoryDetail(APIView):
    def getObject(self, category_slug: str) -> Category:
        try:
            return Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request: Request, category_slug: str) -> Response:
        category = self.getObject(category_slug)
        serialized_category = CategorySerializer(category).data
        response_data = makeResponseData(
            status=200,
            message='OK',
            details={'category': serialized_category}
        )
        return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def patch(self, request: Request, category_slug: str) -> Response:
        category = self.getObject(category_slug)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = makeResponseData(
                status=200,
                message='OK',
                details={'category': serializer.data}
            )
            return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def delete(self, request: Request, category_slug: str) -> Response:
        category = self.getObject(category_slug)
        category.delete()
        response_data = makeResponseData(status=204, message='No Content')
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)\


class ProductList(APIView):
    def get(self, request: Request) -> Response:
        offset = request.GET.get('offset')
        if offset:
            try:
                offset = json.loads(offset)
                offset = ProductListOffsetScheme(**offset)
            except (TypeError, json.decoder.JSONDecodeError):
                response_data = {
                    'errors': [makeResponseData(status=400, message='Offset must be a valid JSON string')]
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            except ValidationError as e:
                response_data = {
                    'errors': [makeResponseData(status=400, message='Offset validation error', details=e.errors())]
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            offset = ProductListOffsetScheme(start=0, end=5)
        
        filters = ['category__slug']
        query_params = request.query_params
        filter_kwargs = makeModelFilterKwargs(filters, query_params)
        if filter_kwargs:
            products_count = Product.objects.filter(**filter_kwargs).count()
            products = Product.objects.filter(**filter_kwargs)[offset.start:offset.end]
        else:
            products_count = Product.objects.all().count()
            products = Product.objects.all()[offset.start:offset.end]

        serialized_products = ProductSerializer(products, many=True).data

        response_data = makeResponseData(
            status=200,
            message='OK',
            details={
                'products_count': products_count,
                'products': serialized_products
            }
        )
        return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def post(self, request: Request) -> Response:
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            product = serializer.save()

        response_data = makeResponseData(
            status=201,
            message='Created',
            details={'product': serializer.data}
        )
        return Response(response_data, status=status.HTTP_201_CREATED)


class ProductDetail(APIView):
    def getObject(self, product_slug: str) -> Product:
        try:
            return Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request: Request, product_slug: str) -> Response:
        product = self.getObject(product_slug)
        serialized_product = ProductSerializer(product).data
        response_data = makeResponseData(
            status=200,
            message='OK',
            details={'product': serialized_product}
        )
        return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def patch(self, request: Request, product_slug: str) -> Response:
        product = self.getObject(product_slug)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = makeResponseData(
                status=200,
                message='OK',
                details={'product': serializer.data}
            )
            return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def delete(self, request: Request, product_slug: str) -> Response:
        product = self.getObject(product_slug)
        product.delete()
        response_data = makeResponseData(status=204, message='No Content')
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)



class ProductVariantList(APIView):
    def get(self, request: Request, product_slug: str) -> Response:
        variants = (
            ProductVariant.objects
            .prefetch_related('images')
            .filter(product__slug=product_slug)
        )

        serialized_variants = ProductVariantSerializer(variants, many=True).data

        variant_images = {}
        for variant in variants:
            variant_images[variant.id] = set()
            for image in variant.images.all():
                variant_images[variant.id].add(str(image.image))

        for i, variant in enumerate(serialized_variants):
            variant_id = variant['id']
            serialized_variants[i]['images'] = variant_images[variant_id]

        response_data = makeResponseData(
            status=200,
            message='OK',
            details={'variants': serialized_variants}
        )
        return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def post(self, request: Request, product_slug: str) -> Response:
        try:
            product = Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            raise Http404

        data = request.data
        data['product'] = product.id

        with transaction.atomic():
            serializer = ProductVariantSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                variant = serializer.save()

            images = request.FILES.getlist('images')
            variant_images = []
            for image in images:
                variant_images.append(
                    ProductVariantImage(product_variant=variant, image=image)
                )
            ProductVariantImage.objects.bulk_create(variant_images)

            response_data = makeResponseData(
                status=201,
                message='Created',
                details={'product_variant': serializer.data}
            )
            return Response(response_data, status=status.HTTP_201_CREATED)


class ProductVariantDetail(APIView):
    def getObject(self, product_slug: str, variant_slug: str) -> Product:
        try:
            return ProductVariant.objects.get(product__slug=product_slug, slug=variant_slug)
        except ProductVariant.DoesNotExist:
            raise Http404

    def get(self, request: Request, product_slug: str, variant_slug: str) -> Response:
        variant = self.getObject(product_slug, variant_slug)
        serialized_variant = ProductVariantSerializer(variant).data
        response_data = makeResponseData(
            status=200,
            message='OK',
            details={'product_variant': serialized_variant}
        )
        return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def patch(self, request: Request, product_slug: str, variant_slug: str) -> Response:
        variant = self.getObject(product_slug, variant_slug)
        serializer = ProductVariantSerializer(variant, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = makeResponseData(
                status=200,
                message='OK',
                details={'product_variant': serializer.data}
            )
            return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def delete(self, request: Request, product_slug: str, variant_slug: str) -> Response:
        variant = self.getObject(product_slug, variant_slug)
        variant.delete()
        response_data = makeResponseData(status=204, message='No Content')
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)


class OrderList(APIView):
    def get(self, request: Request) -> Response:
        orders = Order.objects.all()

        filters = ['contact', 'contact_method']
        query_params = request.query_params
        filter_kwargs = makeModelFilterKwargs(filters, query_params)
        if filter_kwargs:
            orders = orders.filter(**filter_kwargs)

        serialized_orders = OrderSerializer(orders, many=True).data
        response_data = makeResponseData(
            status=200,
            message='OK',
            details={'orders': serialized_orders}
        )
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        data = request.data

        with transaction.atomic():
            serializer = OrderSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                order = serializer.save()

            order_items = []
            for product_data in data['products']:
                try:
                    product = ProductVariant.objects.get(id=product_data['id'])
                    order_items.append(
                        OrderItem(order=order, product=product, quantity=product_data['quantity'])
                    )
                except ProductVariant.DoesNotExist:
                    continue
            OrderItem.objects.bulk_create(order_items)

            response_data = makeResponseData(
                status=201,
                message='Created',
                details={'order': serializer.data}
            )
            return Response(response_data, status=status.HTTP_201_CREATED)


class OrderDetail(APIView):
    def getObject(self, order_id: str) -> Order:
        try:
            order_id = uuid.UUID(order_id).hex
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise Http404

    def get(self, request: Request, order_id: str) -> Response:
        order = self.getObject(order_id)
        serialized_order = OrderSerializer(order).data
        response_data = makeResponseData(
            status=200,
            message='OK',
            details={'order': serialized_order}
        )
        return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def patch(self, request: Request, order_id: str) -> Response:
        order = self.getObject(order_id)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = makeResponseData(
                status=200,
                message='OK',
                details={'order': serializer.data}
            )
            return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def delete(self, request: Request, order_id: str) -> Response:
        order = self.getObject(order_id)
        order.delete()
        response_data = makeResponseData(status=204, message='No Content')
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)
