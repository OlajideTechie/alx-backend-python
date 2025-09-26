from rest_framework import viewsets, filters, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import CustomUser, Conversation, Message
from .serializers import UserSerializer, MessageSerializer, ConversationSerializer
from .permissions import IsOwner, IsParticipantOfConversation
from .pagination import MessagePagination


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    Allows unauthenticated creation of users.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["email", "username", "first_name", "last_name"]

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]


class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing conversations.
    Only authenticated users who are participants can access.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter]
    search_fields = ["participants_id__user_id"]

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        if user_id:
            return self.queryset.filter(participants_id__user_id=user_id).distinct()
        return self.queryset

    def perform_create(self, serializer):
        participants_ids = self.request.data.get("participants_ids", [])
        if not participants_ids or len(participants_ids) < 2:
            raise ValidationError("At least two participants are required.")

        participants_qs = CustomUser.objects.filter(user_id__in=participants_ids)
        if participants_qs.count() != len(participants_ids):
            raise ValidationError("One or more participant IDs are invalid.")

        conversation = serializer.save()
        conversation.participants_id.set(participants_qs)
        conversation.save()


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing messages in conversations.
    Only participants can view, create, update, or delete messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter]
    search_fields = ["conversation__conversation_id"]
    pagination_class = MessagePagination

    def get_queryset(self):
        conversation_id = self.request.query_params.get("conversation_id")
        if conversation_id:
            return Message.objects.filter(
                conversation__conversation_id=conversation_id
            ).order_by("sent_at")
        return Message.objects.all().order_by("sent_at")

    def perform_create(self, serializer):
        conversation_id = self.request.data.get("conversation_id")
        sender_id = self.request.data.get("sender_id")
        recipient_id = self.request.data.get("recipient_id")
        message_body = self.request.data.get("message_body")

        if not all([conversation_id, sender_id, recipient_id, message_body]):
            raise ValidationError("conversation_id, sender_id, recipient_id, and message_body are required.")

        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        sender = get_object_or_404(CustomUser, user_id=sender_id)
        recipient = get_object_or_404(CustomUser, user_id=recipient_id)

        if sender not in conversation.participants_id.all() or recipient not in conversation.participants_id.all():
            return Response(
                {"detail": "Both sender and recipient must be participants in the conversation."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer.save(
            conversation=conversation,
            sender_id=sender,
            recipient=recipient,
            message_body=message_body,
            sent_at=timezone.now(),
        )

    @swagger_auto_schema(
        operation_description="Retrieve messages for a specific conversation.",
        manual_parameters=[
            openapi.Parameter(
                "conversation_id",
                openapi.IN_QUERY,
                description="ID of the conversation",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={200: MessageSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)