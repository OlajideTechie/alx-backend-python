from rest_framework.permissions import BasePermission
from rest_framework import permissions
from .models import Conversation

""" Custom permissions for chat application.
    - IsOwner: Allows only owners of an object to edit or delete it.
    - IsParticipantOfConversation: Allows only participants of a conversation
        to send, view, update, or delete messages.
    """

class IsParticipantOfConversation(BasePermission):
    """
    Custom permission to allow only participants of a conversation
    to send, view, update, or delete messages.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission:
        - obj could be a Message or a Conversation
        - Only participants in the conversation are allowed for any method
        """
        if hasattr(obj, "conversation"):  # obj is a Message
            conversation = obj.conversation
        elif isinstance(obj, Conversation):  # obj is a Conversation
            conversation = obj
        else:
            return False

        if request.method in ["GET", "HEAD", "OPTIONS", "PUT", "PATCH", "DELETE"]:
            return request.user in conversation.participants.all()

        return False
class IsOwner(BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.
    Assumes the object has an `user` attribute.
    """
    def has_object_permission(self, request, view, obj):
        return hasattr(obj, "user") and obj.user == request.user
    
