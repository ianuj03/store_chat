from django.contrib import admin
from .models import ChatMessage, ChatSession

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user', 'content', 'created_at') 

    def get_user(self, obj):
        return obj.session.user if obj.session and obj.session.user else "Anonymous"
    get_user.short_description = 'User'


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'title', 'created_at')

