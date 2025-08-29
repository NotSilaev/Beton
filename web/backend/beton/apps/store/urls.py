from django.urls import path

from apps.store import views


urlpatterns = [
    path('categories/', views.CategoryList.as_view(), name='category_list'),
    path('categories/<str:category_slug>/', views.CategoryDetail.as_view(), name='category_detail'),
    path('products/', views.ProductList.as_view(), name='product_list'),
    path('products/<str:product_slug>/', views.ProductDetail.as_view(), name='product_detail'),
    path('products/<str:product_slug>/variants/', views.ProductVariantList.as_view(), name='product_variant_list'),
    path(
        'products/<str:product_slug>/<str:variant_slug>/', 
        views.ProductVariantDetail.as_view(), 
        name='product_variant_detail'
    ),
    path('orders/', views.OrderList.as_view(), name='order_list'),
    path('orders/<str:order_id>/', views.OrderDetail.as_view(), name='order_detail'),
]
