from rest_framework import serializers
from .models import CustomUser, Conversation, Message
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that explicitly uses 'email' as the login field.
    """
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['username'] = user.username
        return token
        

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT view that uses the CustomTokenObtainPairSerializer.
    """
    serializer_class = CustomTokenObtainPairSerializer
    


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
        """Ensure the email is valid and unique, ignoring current user on update."""
        value = value.strip().lower()
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        user_id = self.instance.user_id if self.instance else None
        if CustomUser.objects.exclude(user_id=user_id).filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# ------------------------
# MESSAGE SERIALIZER
# ------------------------
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(source="sender_id", read_only=True)
    recipient = UserSerializer(read_only=True)
    message_body = serializers.CharField(max_length=1000)  # now writeable

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
    participants_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    messages = MessageSerializer(many=True, read_only=True, source="message_set")

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "participants_ids",
            "messages",
            "created_at",
        ]

    def create(self, validated_data):
        participants_ids = validated_data.pop("participants_ids", [])
        conversation = Conversation.objects.create(**validated_data)
        if participants_ids:
            participants = CustomUser.objects.filter(user_id__in=participants_ids)
            conversation.participants_id.set(participants)
        return conversation