"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views.
More info: https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # =============================
    # Admin
    # =============================
    path("admin/", admin.site.urls),

    # =============================
    # API Documentation
    # =============================
    path(
        "api/schema/",
        SpectacularAPIView.as_view(
            authentication_classes=[],
            permission_classes=[],
        ),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
            authentication_classes=[],
            permission_classes=[],
        ),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema",
            authentication_classes=[],
            permission_classes=[],
        ),
        name="redoc",
    ),

    # =============================
    # API Routes
    # =============================
    path(
        "api/auth/",
        include(("apps.accounts.api.urls", "accounts"), namespace="accounts"),
    ),
    path(
        "api/chat/",
        include(("apps.chat.api.urls", "chats"), namespace="chats"),
    ),
    path(
        "api/products/",
        include(("apps.products.api.urls", "products"), namespace="products"),
    ),
    path(
        "api/wishlist/",
        include(("apps.wishlist.api.urls", "wishlist"), namespace="wishlist"),
    ),
    path(
        "api/cart/",
        include(("apps.cart.api.urls", "cart"), namespace="cart"),
    ),
    path(
        "api/orders/",
        include(("apps.orders.api.urls", "orders"), namespace="orders"),
    ),
    path(
        "api/reports/",
        include(("apps.reports.api.urls", "reports"), namespace="reports"),
    ),
    path(
        "api/notifications/",
        include(("apps.notifications.api.urls", "notifications"), namespace="notifications"),
    ),
]