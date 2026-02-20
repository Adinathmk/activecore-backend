from django.urls import path
from .views import (
    WishlistView,
    WishlistItemCreateView,
    WishlistItemDeleteView,
)

app_name = "wishlist"

urlpatterns = [
    path("", WishlistView.as_view(), name="wishlist"),
    path("items/", WishlistItemCreateView.as_view(), name="wishlist-add"),
    path("items/<int:variant_id>/", WishlistItemDeleteView.as_view(), name="wishlist-remove"),
]