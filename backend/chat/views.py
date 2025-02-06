from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from asgiref.sync import sync_to_async, async_to_sync
from orders.models import Order
from customers.models import Customer

from .models import ChatMessage, ChatSession
from .serializers import ChatMessageSerializer, ChatSessionSerializer

from .openai_utils import process_conversation
from .db_lookup import perform_db_lookup 

class ChatMessageView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        session_id = self.request.query_params.get('session_id', None)
        if not session_id:
            return None
        return ChatMessage.objects.filter(session__session_id= session_id).order_by("-created_at")

class ChatSessionListView(generics.ListCreateAPIView):
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        return ChatSession.objects.all().order_by("-id")


class LLMChatView(APIView):
    """
    A minimal API view that receives a user's query,
    delegates processing to the OpenAI utilities,
    and returns the final response.
    To use this remove session validation in utils
    """
    def post(self, request, *args, **kwargs):
        user_query = request.data.get("query", "").strip()
        if not user_query:
            return Response({"error": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delegate the conversation processing to the utility function.
        result = async_to_sync(process_conversation)(user_query, None, user=request.user)
        
        return Response(result, status=status.HTTP_200_OK)

