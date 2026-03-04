from django.urls import path
from apps.products.api.views.public.product_detail_view import ProductDetailAPIView
from apps.products.api.views.public.product_list_view import ProductListAPIView
from .views.admin.admin_category_create_view import AdminCategoryCreateAPIView
from .views.admin.admin_product_type_create_view import AdminProductTypeCreateAPIView
from .views.admin.admin_product_list_create_view import AdminProductListCreateAPIView
from .views.admin.admin_product_retrieve_update_delete_view import AdminProductRetrieveUpdateDeleteAPIView
from .views.admin.admin_product_search_view import AdminProductSearchAPIView
from apps.products.api.views.admin.admin_variant_list_create_view import AdminVariantListCreateAPIView
from apps.products.api.views.admin.admin_variant_retrieve_update_delete_view import AdminVariantRetrieveUpdateDeleteAPIView
from .views.public.product_rating_view import ProductRatingAPIView
from .views.public.featured_product_list_view import FeaturedProductListView
from .views.public.product_search_view import ProductSearchAPIView

app_name = "products"

urlpatterns = [
    # Admin Routes
    path("admin/categories/", AdminCategoryCreateAPIView.as_view(), name="admin-category-create"),
    path("admin/product-types/", AdminProductTypeCreateAPIView.as_view(), name="admin-product-type-create"),
    path("admin/search/", AdminProductSearchAPIView.as_view(), name="admin-product-search"),
    path("admin/variants/", AdminVariantListCreateAPIView.as_view(), name="admin-variant-list-create"),
    path("admin/variants/<int:id>/", AdminVariantRetrieveUpdateDeleteAPIView.as_view(), name="admin-variant-detail"),
    path("admin/", AdminProductListCreateAPIView.as_view(), name="admin-product-list-create"),
    path("admin/<int:pk>/", AdminProductRetrieveUpdateDeleteAPIView.as_view(), name="admin-product-detail"),
    
    path("", ProductListAPIView.as_view(), name="product-list"),
    path("search/", ProductSearchAPIView.as_view(), name="product-search"),
    path("<slug:slug>/", ProductDetailAPIView.as_view(), name="product-detail"),
    path("<slug:slug>/rate/",ProductRatingAPIView.as_view(),name="product-rate",),
    path("home/featured/",FeaturedProductListView.as_view(),name="home-featured-products",),

]
