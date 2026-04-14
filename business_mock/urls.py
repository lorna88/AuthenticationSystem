from django.urls import path

from business_mock.views_orders import OrderMockView
from business_mock.views_products import ProductMockView
from business_mock.views_stores import StoreMockView

app_name = 'mock'

urlpatterns = [
    path('orders/', OrderMockView.as_view(), name='mock_orders'),
    path('orders/<int:pk>/', OrderMockView.as_view(), name='mock_order_detail'),
    path('products/', ProductMockView.as_view(), name='mock_products'),
    path('products/<int:pk>/', ProductMockView.as_view(), name='mock_product_detail'),
    path('stores/', StoreMockView.as_view(), name='mock_stores'),
    path('stores/<int:pk>/', StoreMockView.as_view(), name='mock_store_detail'),
]