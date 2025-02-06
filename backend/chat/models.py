from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
import uuid

class ChatSession(models.Model):
    """
    Represents a chat session, which can be linked to an authenticated user or an anonymous session ID.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255, default="New Session")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session {self.session_id} - {self.title}"


class ChatMessage(models.Model):
    '''
    Represents an individual message within a chat session.
    '''
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', null = True)
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('assistant', 'Assistant')])
    content = models.TextField(null = True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role.capitalize()} Message at {self.created_at}"

