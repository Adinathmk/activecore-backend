from django.urls import path

from .views.wishlist_views import WishlistView
from .views.wishlist_item_views import WishlistItemCreateView, WishlistItemDeleteView
from .views.wishlist_meta_views import WishlistCountView
from .views.wishlist_cart_views import MoveAllWishlistToCartView


urlpatterns = [
    path("", WishlistView.as_view(), name="wishlist"),
    path("items/", WishlistItemCreateView.as_view(), name="wishlist-add-item"),
    path("items/<int:variant_id>/", WishlistItemDeleteView.as_view(), name="wishlist-remove-item"),
    path("count/", WishlistCountView.as_view(), name="wishlist-count"),
    path("move-to-cart/", MoveAllWishlistToCartView.as_view(), name="wishlist-move-to-cart"),
]