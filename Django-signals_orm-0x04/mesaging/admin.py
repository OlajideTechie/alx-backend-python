# messaging/admin.py
from django.contrib import admin
from .models import Message, Notification

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "content", "timestamp")
    search_fields = ("sender__username", "receiver__username", "content")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "message", "content", "is_read", "created_at")
    search_fields = ("user__username", "content")
    list_filter = ("is_read", "created_at")