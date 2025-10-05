# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
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
    Show unread messages for the logged-in user.
    """
    unread_messages = Message.unread.for_user(request.user)

    return render(request, "messaging/unread_messages.html", {
        "unread_messages": unread_messages
    })
    
    
