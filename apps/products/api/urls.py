from django.urls import path
from apps.products.api.views.public.product_detail_view import ProductDetailAPIView
from apps.products.api.views.public.product_list_view import ProductListAPIView
app_name = "products"

urlpatterns = [
    path("", ProductListAPIView.as_view(), name="product-list"),
    path("<slug:slug>/", ProductDetailAPIView.as_view(), name="product-detail"),   
]
