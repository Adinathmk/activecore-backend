from django.urls import path
from apps.products.api.views.public.product_detail_view import ProductDetailAPIView
from apps.products.api.views.public.product_list_view import ProductListAPIView
from .views.admin.admin_category_create_view import AdminCategoryCreateAPIView
from .views.admin.admin_product_type_create_view import AdminProductTypeCreateAPIView
from .views.admin.admin_product_list_create_view import AdminProductListCreateAPIView
from .views.admin.admin_product_retrieve_update_delete_view import AdminProductRetrieveUpdateDeleteAPIView
from .views.public.product_rating_view import ProductRatingAPIView
app_name = "products"

urlpatterns = [
    path("", ProductListAPIView.as_view(), name="product-list"),
    path("<slug:slug>/", ProductDetailAPIView.as_view(), name="product-detail"),
    path("<slug:slug>/rate/",ProductRatingAPIView.as_view(),name="product-rate",),

    path("admin/categories/", AdminCategoryCreateAPIView.as_view(), name="admin-category-create"),
    path("admin/product-types/", AdminProductTypeCreateAPIView.as_view(), name="admin-product-type-create"),

    path("admin/", AdminProductListCreateAPIView.as_view(), name="admin-product-create"),   
    path("admin/<int:pk>/",AdminProductRetrieveUpdateDeleteAPIView.as_view(),name="admin-product-detail"),
]
