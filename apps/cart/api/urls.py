from django.urls import path
from .views.cart_read_views import CartDetailView
from .views.cart_meta_views import CartCountView
from .views.cart_write_views import (
    AddToCartView,
    UpdateCartItemView,
    RemoveCartItemView,
    ClearCartView,
)
from .views.cart_validation_views import ValidateCartView

urlpatterns = [
    # Read
    path("", CartDetailView.as_view(), name="cart-detail"),
    path("count/", CartCountView.as_view(), name="cart-count"),

    # Write
    path("add/", AddToCartView.as_view(), name="cart-add"),
    path("items/<int:item_id>/", UpdateCartItemView.as_view(), name="cart-update"),
    path("items/<int:item_id>/remove/", RemoveCartItemView.as_view(), name="cart-remove"),
    path("clear/", ClearCartView.as_view(), name="cart-clear"),

    # Validation
    path("validate/", ValidateCartView.as_view(), name="cart-validate"),
]