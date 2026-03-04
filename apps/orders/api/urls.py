from django.urls import path
from .views.public.public_views import (
    CheckoutView,
    OrderListView,
    OrderDetailView,
    CancelOrderView,
    AccountOverviewView
    # PaymentConfirmView,
)
from .views.admin.admin_views_update import AdminOrderStatusUpdateView
from .views.admin.admin_order_detail_view import AdminOrderDetailView
from .views.admin.admin_order_list_view import AdminOrderListView
from .views.admin.admin_order_search_view import AdminOrderSearchView
from .views.admin.admin_order_stats_view import AdminOrderStatsView
from .views.public.payment_views import CreatePaymentIntentView
from .views.public.webhooks import stripe_webhook




urlpatterns = [

# PUBLIC ROUTES


    path("checkout/", CheckoutView.as_view(), name="order-checkout"),
    path("", OrderListView.as_view(), name="order-list"),
    path("<uuid:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("<uuid:pk>/cancel/", CancelOrderView.as_view(), name="order-cancel"),
    path("account-overview/", AccountOverviewView.as_view(), name="account-overview"),


    # =========================
    # PAYMENT
    # =========================


    path("<uuid:pk>/create-payment-intent/", CreatePaymentIntentView.as_view(), name="create-payment-intent"),
    path("payments/webhook/", stripe_webhook, name="stripe-webhook"),



# ADMIN ROUTES


    path("admin/<uuid:pk>/update-status/",AdminOrderStatusUpdateView.as_view(),name="admin-order-update-status"),
    path("admin/search/", AdminOrderSearchView.as_view(), name="admin-order-search"),
    path("admin/", AdminOrderListView.as_view(), name="admin-order-list"),
    path("adimn/stats/", AdminOrderStatsView.as_view(), name="admin-order-stats"),
    path("admin/<uuid:pk>/", AdminOrderDetailView.as_view(), name="admin-order-detail"),
]