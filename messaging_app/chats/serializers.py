from rest_framework import serializers
from .models import CustomUser, Conversation, Message
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError


# ------------------------
# USER SERIALIZER
# ------------------------
class UserSerializer(serializers.ModelSerializer):
    
    full_name = serializers.SerializerMethodField() # Read-only field to get full name
    class Meta:
        model = CustomUser
        fields = [
            "user_id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "full_name",
            "role",
            "created_at",
        ]
        extra_kwargs = {
            'password': {'required': True, 'write_only': True, 'min_length': 8},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
            "username": {"required": True},
            "phone_number": {"required": False},
        }
        
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
        
    def validate_email(self, value):
        """Ensure the email is valid and unique."""
        value = value.strip().lower()
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Enter a valid email address.")

        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


# ------------------------
# MESSAGE SERIALIZER
# ------------------------
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(source="sender_id", read_only=True)
    recipient = UserSerializer(read_only=True)    
    message_body = serializers.CharField(max_length=1000, read_only=True)                  

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