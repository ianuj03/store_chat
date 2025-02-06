import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from .models import ChatSession
        self.session_id = self.scope['url_route']['kwargs'].get('session_id')  # Check for session_id in the URL
        user = self.scope["user"] if self.scope["user"].is_authenticated else None

        if self.session_id:
            # Try to fetch the existing session
            session = await sync_to_async(ChatSession.objects.filter(session_id=self.session_id).first)()
            if session:
                await self.accept()
                await self.send(json.dumps({
                    "type": "session_connected",
                    "session_id": self.session_id,
                    "message": "Connected to the existing session."
                }))
            else:
                await self.close()  # Close connection if the session is invalid
        else:
            # Create a new session
            session = await sync_to_async(ChatSession.objects.create)(user=user, title="New Session")
            self.session_id = str(session.session_id)
            await self.accept()
            await self.send(json.dumps({
                "type": "session_created",
                "session_id": self.session_id,
                "message": "New session created successfully."
            }))

    async def disconnect(self, close_code):
        # Handle disconnection (optional)
        pass

    async def receive(self, text_data):
        from .models import ChatSession
        from .openai_utils import process_conversation
        data = json.loads(text_data)
        user = self.scope["user"] if self.scope["user"].is_authenticated else None

        user_query = data.get("query")
        session_id = data.get("session_id")

        if not session_id:
            await self.send(json.dumps({"error": "Session ID is required."}))
            return

        # Validate session before processing
        session_exists = await sync_to_async(ChatSession.objects.filter(session_id=session_id).exists)()
        if not session_exists:
            await self.send(json.dumps({"error": "Invalid session ID."}))
            return

        # Process the user query
        response = await process_conversation(user_query, session_id, user=user)

        # Send the AI's response
        await self.send(json.dumps({
            "type": "chat_response",
            "reply": response.get("reply")
        }))

