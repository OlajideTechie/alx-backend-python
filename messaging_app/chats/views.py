from rest_framework import generics, status, viewsets, filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import  (
    CustomUser, 
    Property, 
    Payment, 
    Booking, 
    Conversation, 
    Message,
    Review,
)
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import datetime
from .serializers import (
    UserSerializer,
    MessageSerializer,
    ConversationSerializer,
)


# Create your viewsets here.


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['participants_id__user_id']

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return self.queryset.filter(participants_id__user_id=user_id).distinct()
        return self.queryset

    def perform_create(self, serializer):
        participants = self.request.data.get('participants', [])
        if not participants or len(participants) < 2:
            raise ValidationError("At least two participants are required to create a conversation.")
        users = CustomUser.objects.filter(user_id__in=participants)
        if users.count() != len(participants):
            raise ValidationError("One or more participant IDs are invalid.")
        conversation = serializer.save()
        conversation.participants_id.set(users)
        conversation.save()
        return conversation

    @swagger_auto_schema(
        operation_description="Retrieve conversations for a specific user.",
        manual_parameters=[
            openapi.Parameter(
                'user_id', openapi.IN_QUERY, description="ID of the user", type=openapi.TYPE_STRING, required=False
            ),
        ],
        responses={200: ConversationSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new conversation with participants.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'participants': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="List of user IDs to include in the conversation",
                ),
            },
            required=['participants'],
        ),
        responses={201: ConversationSerializer()},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['conversation__conversation_id']

    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            return self.queryset.filter(conversation__conversation_id=conversation_id).order_by('sent_at')
        return self.queryset.order_by('sent_at')

    def perform_create(self, serializer):
        conversation_id = self.request.data.get('conversation_id')
        sender_id = self.request.data.get('sender_id')
        recipient_id = self.request.data.get('recipient_id')
        message_body = self.request.data.get('message_body')

        if not all([conversation_id, sender_id, recipient_id, message_body]):
            raise ValidationError("conversation_id, sender_id, recipient_id, and message_body are required.")

        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        sender = get_object_or_404(CustomUser, user_id=sender_id)
        recipient = get_object_or_404(CustomUser, user_id=recipient_id)

        if sender not in conversation.participants_id.all() or recipient not in conversation.participants_id.all():
            raise ValidationError("Both sender and recipient must be participants in the conversation.")

        message = serializer.save(
            conversation=conversation,
            sender_id=sender,
            recipient=recipient,
            message_body=message_body,
            sent_at=timezone.now()
        )
        return message

    @swagger_auto_schema(
        operation_description="Retrieve messages for a specific conversation.",
        manual_parameters=[
            openapi.Parameter(
                'conversation_id', openapi.IN_QUERY, description="ID of the conversation", type=openapi.TYPE_STRING, required=False
            ),
        ],
        responses={200: MessageSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new message in a conversation.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'conversation_id': openapi.Schema(type=openapi.TYPE_STRING, description="ID of the conversation"),
                'sender_id': openapi.Schema(type=openapi.TYPE_STRING, description="ID of the sender"),
                'recipient_id': openapi.Schema(type=openapi.TYPE_STRING, description="ID of the recipient"),
                'message_body': openapi.Schema(type=openapi.TYPE_STRING, description="Content of the message"),
            },
            required=['conversation_id', 'sender_id', 'recipient_id', 'message_body'],  
        ),
        responses={201: MessageSerializer()},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


