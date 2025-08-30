from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify

from apps.auth.models import User, AuthToken
from apps.auth.utils import hashAuthToken
from apps.store.models import Category, Product, ProductVariant, Order
from apps.store.serializers import (
    CategorySerializer, 
    ProductSerializer, 
    ProductVariantSerializer, 
    OrderSerializer
)

import uuid
from io import BytesIO
from PIL import Image


def getTestImage():
    bts = BytesIO()
    img = Image.new("RGB", (100, 100))
    img.save(bts, 'jpeg')
    image_id = uuid.uuid4()
    return SimpleUploadedFile(f"test-{image_id}.jpg", bts.getvalue())


class CategoryTests(APITestCase):
    def testCategoryCreation(self):
        url = reverse('category_list')

        data = {
            'title': 'Home decorations',
            'description': 'Everything for home and yard',
            'image': getTestImage(),
        }

        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        response = self.client.post(url, data, format='multipart', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def testCategoryEditing(self):
        # Create category
        data = {'title': 'Garden accessories'}
        serializer = CategorySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        # Get created category
        category_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('category_detail', kwargs={'category_slug': category_slug})
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_200_OK)     
        
        # Change category data
        data = {
            'title': 'Accessories for garden', 
            'description': 'Everything for garden'
        }

        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        # Request with incorrect auth token
        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=auth_header + 'extra_chars') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)          
        
        # Request with correct auth token
        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get edited category
        category_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('category_detail', kwargs={'category_slug': category_slug})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def testCategoryDeletion(self):
        # Create category
        data = {'title': 'Bathroom decorations'}
        serializer = CategorySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        # Get category
        category_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('category_detail', kwargs={'category_slug': category_slug})
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete category
        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        # Request with incorrect auth token
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=auth_header + 'extra_chars') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)          
        
        # Request with correct auth token
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)   

        # Try to get deleted category
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
   
        

class ProductTests(APITestCase):
    def testProductCreation(self):
        category = Category.objects.create(title='Living room decorations')

        url = reverse('product_list')
        data = {
            'title': 'Ornamental flowerpot',
            'description': 'Decorative floor tub made of real concrete',
            'category': category.pk,
        }

        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        response = self.client.post(url, data, format='multipart', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def testProductEditing(self):
        category = Category.objects.create(title='Kitchen decorations') 

        # Create product
        data = {
            'title': 'Napkin holder',
            'description': 'Concrete napkin holder',
            'category': category.pk,
        }
        serializer = ProductSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        # Get created product
        product_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('product_detail', kwargs={'product_slug': product_slug})
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_200_OK)     
        
        # Change product data
        data = {
            'title': 'Oval concrete napkin holder', 
            'description': 'Oval shaped concrete napkin holder',
        }

        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        # Request with incorrect auth token
        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=auth_header + 'extra_chars') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)          
        
        # Request with correct auth token
        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)  

        # Get edited product
        product_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('product_detail', kwargs={'product_slug': product_slug})
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def testProductDeletion(self):
        category = Category.objects.create(title='Porch decorations')

        # Create product
        data = {
            'title': 'Concrete vase',
            'description': 'Handmade flower vase made of concrete',
            'category': category.pk,
        }
        serializer = ProductSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        # Get product
        product_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('product_detail', kwargs={'product_slug': product_slug})
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete product
        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        # Request with incorrect auth token
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=auth_header + 'extra_chars') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)          
        
        # Request with correct auth token
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)     

        # Try to get deleted product
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class ProductVariantTests(APITestCase):
    def testProductVariantCreation(self):
        category = Category.objects.create(title='Living room decorations')
        product = Product.objects.create(
            slug=f'Ornamental flowerpot', 
            title=f'Planters for flowers at home', 
            category=category
        )

        url = reverse('product_variant_list', kwargs={'product_slug': product.slug})
        data = {
            'base_product_id': product.pk,
            'title': 'Green flowerpot XXL',
            'price': 15_000,
            'stock': 10,
            'images': (getTestImage() for i in range(0, 3))
        }

        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        response = self.client.post(url, data, format='multipart', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def testProductVariantEditing(self):
        category = Category.objects.create(title='Living room decorations')
        product = Product.objects.create(
            slug=f'Ornamental flowerpot', 
            title=f'Planters for flowers at home', 
            category=category
        )

        # Create product variant
        data = {
            'base_product_id': product.pk,
            'title': 'Green flowerpot',
            'price': 15_000,
            'stock': 10,
        }
        serializer = ProductVariantSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        # Get created product variant
        variant_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('product_variant_detail', kwargs={'product_slug': product.slug, 'variant_slug': variant_slug})
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_200_OK)     
        
        # Change product variant data
        data = {
            'base_product_id': product.pk,
            'title': 'Green flowerpot XXL',
            'price': 25_000,
            'stock': 5,
        }

        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        # Request with incorrect auth token
        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=auth_header + 'extra_chars') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)          
        
        # Request with correct auth token
        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)  

        # Get edited product variant
        variant_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('product_variant_detail', kwargs={'product_slug': product.slug, 'variant_slug': variant_slug})
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def testProductVariantDeletion(self):
        category = Category.objects.create(title='Living room decorations')
        product = Product.objects.create(
            slug=f'Ornamental flowerpot', 
            title=f'Planters for flowers at home', 
            category=category
        )

        # Create product variant
        data = {
            'base_product_id': product.pk,
            'title': 'Green flowerpot XXL',
            'price': 15_000,
            'stock': 10,
        }
        serializer = ProductVariantSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        # Get product variant
        variant_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('product_variant_detail', kwargs={'product_slug': product.slug, 'variant_slug': variant_slug})
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete product variant
        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        # Request with incorrect auth token
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=auth_header + 'extra_chars') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)          
        
        # Request with correct auth token
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)     

        # Try to get deleted product variant
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class OrderTests(APITestCase):
    def testOrderCreation(self):
        category = Category.objects.create(title='Home')

        products_to_create = []
        variants_to_create = []
        for product_index in range(5):
            product_id = str(uuid.uuid4()).split('-')[0]
            product = Product(
                slug=f'product-{product_id}', 
                title=f'Test product {product_id}', 
                category=category
            )
            products_to_create.append(product)
            for variant_index in range(3):
                variant_id = str(uuid.uuid4()).split('-')[0]
                variants_to_create.append(ProductVariant(
                    base_product=product, 
                    slug=f'variant-{variant_id}', 
                    title=f'Test variant {variant_id}',
                    configuration={'size': 10, 'color': 'white'},
                    price=(1000 * variant_index),
                    stock=(5 * variant_index)
                ))
        products = Product.objects.bulk_create(products_to_create)
        variants = ProductVariant.objects.bulk_create(variants_to_create)

        url = reverse('order_list')

        data = {
            'items': [{'id': variant.id, 'quantity': 5} for variant in variants],
            'fullname': 'Nikita Silaev',
            'contact': '+7 999 888 77 66',
            'contact_method': 'phone'
        }
        response = self.client.post(url, data, format='json') 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def testOrderEditing(self):
        category = Category.objects.create(title='Home')

        products_to_create = []
        variants_to_create = []
        for product_index in range(5):
            product_id = str(uuid.uuid4()).split('-')[0]
            product = Product(
                slug=f'product-{product_id}', 
                title=f'Test product {product_id}', 
                category=category
            )
            products_to_create.append(product)
            for variant_index in range(3):
                variant_id = str(uuid.uuid4()).split('-')[0]
                variants_to_create.append(ProductVariant(
                    base_product=product, 
                    slug=f'variant-{variant_id}', 
                    title=f'Test variant {variant_id}',
                    configuration={'size': 10, 'color': 'white'},
                    price=(1000 * variant_index),
                    stock=(5 * variant_index)
                ))
        products = Product.objects.bulk_create(products_to_create)
        variants = ProductVariant.objects.bulk_create(variants_to_create)

        data = {
            'items': [{'id': variant.id, 'quantity': 5} for variant in variants],
            'fullname': 'Nikita Silaev',
            'contact': '+7 999 888 77 66',
            'contact_method': 'phone'
        }
        serializer = OrderSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        url = reverse('order_detail', kwargs={'order_id': serializer.data['id']})

        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        data = {
            'items': [{'id': variant.id, 'quantity': 5} for variant in variants[:2]],
            'contact': '+7 999 888 77 66',
            'contact_method': 'telegram'
        }

        # Request with incorrect auth token
        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=auth_header + 'extra_chars') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)          
        
        # Request with correct auth token
        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def testOrderDeletion(self):
        category = Category.objects.create(title='Home')

        products_to_create = []
        variants_to_create = []
        for product_index in range(5):
            product_id = str(uuid.uuid4()).split('-')[0]
            product = Product(
                slug=f'product-{product_id}', 
                title=f'Test product {product_id}', 
                category=category
            )
            products_to_create.append(product)
            for variant_index in range(3):
                variant_id = str(uuid.uuid4()).split('-')[0]
                variants_to_create.append(ProductVariant(
                    base_product=product, 
                    slug=f'variant-{variant_id}', 
                    title=f'Test variant {variant_id}',
                    configuration={'size': 10, 'color': 'white'},
                    price=(1000 * variant_index),
                    stock=(5 * variant_index)
                ))
        products = Product.objects.bulk_create(products_to_create)
        variants = ProductVariant.objects.bulk_create(variants_to_create)

        data = {
            'items': [{'id': variant.id, 'quantity': 5} for variant in variants],
            'fullname': 'Nikita Silaev',
            'contact': '+7 999 888 77 66',
            'contact_method': 'telegram'
        }
        serializer = OrderSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        url = reverse('order_detail', kwargs={'order_id': serializer.data['id']})

        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        # Request with incorrect auth token
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=auth_header + 'extra_chars') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)          
        
        # Request with correct auth token
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)     

        # Try to get deleted product
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
