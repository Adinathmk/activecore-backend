from django.urls import path
from .views.public.public_views import (
    CheckoutView,
    OrderListView,
    OrderDetailView,
    CancelOrderView,
    # PaymentConfirmView,
)
from .views.admin.admin_views_update import AdminOrderStatusUpdateView
from .views.admin.admin_order_detail_view import AdminOrderDetailView
from .views.admin.admin_order_list_view import AdminOrderListView
from .views.admin.admin_order_stats_view import AdminOrderStatsView




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
    path("admin/", AdminOrderListView.as_view(), name="admin-order-list"),
    path("adimn/stats/", AdminOrderStatsView.as_view(), name="admin-order-stats"),
    path("admin/<uuid:pk>/", AdminOrderDetailView.as_view(), name="admin-order-detail"),
]