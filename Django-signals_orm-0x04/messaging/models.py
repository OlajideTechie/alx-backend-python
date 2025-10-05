from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # Threaded replies
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    # Edit tracking
    edited_at = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="edited_messages"
    )

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20]}"

    @property
    def is_reply(self):
        return self.parent_message is not None

    def get_thread(self):
        """
        Recursively fetch all replies to this message in a threaded structure.
        """
        replies = []
        for reply in self.replies.all().select_related("sender").prefetch_related("replies__sender"):
            replies.append({
                "id": reply.id,
                "content": reply.content,
                "sender": reply.sender.username,
                "timestamp": reply.timestamp,
                "replies": reply.get_thread()  # recursion
            })
        return replies


class MessageHistory(models.Model):
    """
    Keeps old versions of messages when they are edited.
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="history")
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"History of message {self.message.id} at {self.edited_at}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="notifications")
    content = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.content}"