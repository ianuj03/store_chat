from django.urls import path
from .views import (
    LLMChatView,
    ChatMessageView,
    ChatSessionListView
)

urlpatterns = [
    # Participant endpoints
    path('llm-chat/', LLMChatView.as_view(), name='llm-chat-view'),
    path('chat/', ChatMessageView.as_view(), name='chat-view'),
    path('session/', ChatSessionListView.as_view(), name='chat-session-view'),
]
