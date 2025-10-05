# views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib import messages
from .models import Message
from django.shortcuts import render


""" View to delete a user and cascade delete related messages and notifications."""
@login_required
def delete_user(request):
    user = request.user
    username = user.username
    user.delete()
    messages.success(request, f"Account '{username}' and all related data deleted successfully.")
    return redirect("home")


""" View to display a conversation between two users with message threading."""
def conversation_view(request, user_id):
    # Get top-level messages (not replies) for a conversation
    messages = (
        Message.objects
        .filter(receiver_id=user_id, parent_message__isnull=True)
        .select_related("sender", "receiver")   # avoid extra queries
        .prefetch_related("replies__sender")    # prefetch replies + their senders
    )

    return render(request, "messaging/conversation.html", {"messages": messages})