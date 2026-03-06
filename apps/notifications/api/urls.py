from django.urls import path
from .views import NotificationListView, SendGlobalNotificationView, SendUserNotificationView

urlpatterns = [
    path("", NotificationListView.as_view()),
    path("send/", SendGlobalNotificationView.as_view()),
    path("send-user/", SendUserNotificationView.as_view()),
]