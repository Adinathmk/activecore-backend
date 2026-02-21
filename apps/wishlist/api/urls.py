from django.urls import path
from .views.views import (
    WishlistView,
    WishlistItemCreateView,
    WishlistItemDeleteView,
    WishlistCountView,
    MoveAllWishlistToCartView
)


app_name = "wishlist"

urlpatterns = [
    path("", WishlistView.as_view(), name="wishlist"),
    path("items/", WishlistItemCreateView.as_view(), name="wishlist-add"),
    path("items/<int:variant_id>/", WishlistItemDeleteView.as_view(), name="wishlist-remove"),
    path("count/", WishlistCountView.as_view(), name="wishlist-count"),
    path( "move-all-to-cart/",MoveAllWishlistToCartView.as_view(),name="wishlist-move-all-to-cart"),
]