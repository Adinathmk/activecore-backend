from django.urls import path
from .views import AddToCartView,CartDetailView,UpdateCartItemView,RemoveCartItemView,ClearCartView,ValidateCartView,CartCountView

app_name = "cart"

urlpatterns = [
    path("", CartDetailView.as_view(), name="cart-detail"),
    path("add/", AddToCartView.as_view(), name="cart-add"),
    path("item/<int:item_id>/", UpdateCartItemView.as_view(),name="cart-item-update",),
    path("remove/<int:item_id>/", RemoveCartItemView.as_view(), name="cart-remove-item"),
    path("clear/", ClearCartView.as_view(), name="cart-clear"),
    path("validate/", ValidateCartView.as_view(), name="cart-validate"),
    path("count/", CartCountView.as_view(), name="cart-count"),
]