
from rest_framework import serializers

class CookieRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
