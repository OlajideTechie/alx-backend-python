# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib import messages
from .models import Message
from django.shortcuts import render
from django.views.decorators.cache import cache_page


""" View to delete a user and cascade delete related messages and notifications."""
@login_required
def delete_user(request):
    user = request.user
    username = user.username
    user.delete()
    messages.success(request, f"Account '{username}' and all related data deleted successfully.")
    return redirect("home")


""" View to display a conversation between two users with message threading."""
@login_required
def conversation_view(request, user_id):
    """
    Retrieve conversation between logged-in user and another user.
    """
    other_user = get_object_or_404(User, id=user_id)

    # Filter messages between the two users
    messages = Message.objects.filter(
        (models.Q(sender=request.user, receiver=other_user) |
         models.Q(sender=other_user, receiver=request.user))
    ).select_related("sender", "receiver").order_by("timestamp")

    return render(request, "messaging/conversation.html", {
        "messages": messages,
        "other_user": other_user
    })
    
    
@login_required
def send_message(request, receiver_id):
    """
    Send a message from the logged-in user to another user.
    """
    if request.method == "POST":
        content = request.POST.get("content")
        receiver = get_object_or_404(User, id=receiver_id)

        # Create message with sender=request.user
        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content
        )
        return JsonResponse({"status": "success", "message": "Message sent!"})

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@login_required
def unread_messages_view(request):
    """
    Display unread messages for the logged-in user.
    """
    unread_messages = (
        Message.unread.unread_for_user(request.user)
        .only("id", "sender", "content", "timestamp")
    )

    return render(request, "messaging/unread_messages.html", {
        "unread_messages": unread_messages
    })
    
    
@login_required
@cache_page(60) # Cache for 60 seconds
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
