from django.urls import path
from apps.products.api.views.product_detail_APiView import ProductDetailAPIView
app_name = "products"

urlpatterns = [
    path("products/<slug:slug>/", ProductDetailAPIView.as_view(), name="product-detail"),   
]
