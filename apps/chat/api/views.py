# apps/chat/api/views.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import ChatMessage


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        messages = ChatMessage.objects.filter(
            user=request.user
        ).order_by("created_at")[:50]

        data = [
            {
                "role": m.role,
                "text": m.message
            }
            for m in messages
        ]

        return Response(data)