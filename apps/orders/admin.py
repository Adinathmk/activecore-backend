from django.contrib import admin
from .models import Order,OrderItem,OrderStatusHistory

admin.site.register(OrderStatusHistory)
admin.site.register(Order)
admin.site.register(OrderItem)