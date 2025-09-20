from rest_framework import serializers
from .models import CustomUser, Conversation, Message


# ------------------------
# USER SERIALIZER
# ------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "user_id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "created_at",
        ]


# ------------------------
# MESSAGE SERIALIZER
# ------------------------
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(source="sender_id", read_only=True)     # nested sender
    recipient = UserSerializer(read_only=True)                      # nested recipient

    class Meta:
        model = Message
        fields = [
            "message_id",
            "sender",
            "recipient",
            "message_body",
            "sent_at",
        ]


# ------------------------
# CONVERSATION SERIALIZER
# ------------------------
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(source="participants_id", many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True, source="message_set")

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "messages",
            "created_at",
        ]