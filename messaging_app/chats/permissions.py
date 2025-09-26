from rest_framework.permissions import BasePermission

"""Custom permission to only allow owners of an object to edit it."""
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user