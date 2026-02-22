from django.urls import path
from .views.public.public_views import (
    CheckoutView,
    OrderListView,
    OrderDetailView,
    CancelOrderView,
    # PaymentConfirmView,
)
from .views.admin.admin_views import AdminOrderStatusUpdateView

urlpatterns = [

    # =========================
    # USER ROUTES
    # =========================

    # Create Order (Reserve Stock)
    path("checkout/", CheckoutView.as_view(), name="order-checkout"),

    # List User Orders
    path("", OrderListView.as_view(), name="order-list"),

    # Order Detail
    path("<uuid:pk>/", OrderDetailView.as_view(), name="order-detail"),

    # Cancel Order
    path("<uuid:pk>/cancel/", CancelOrderView.as_view(), name="order-cancel"),


    # =========================
    # PAYMENT
    # =========================

#     # Payment confirmation (Webhook or manual verify)
#     path("<uuid:pk>/confirm-payment/", PaymentConfirmView.as_view(), name="order-confirm-payment"),


#     # =========================
#     # ADMIN ROUTES
#     # =========================

    path("admin/<uuid:pk>/update-status/",AdminOrderStatusUpdateView.as_view(),name="admin-order-update-status"),
]