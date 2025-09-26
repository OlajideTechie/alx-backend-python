from rest_framework.permissions import BasePermission
from rest_framework import permissions

"""Custom permission to only allow owners of an object to edit it."""
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user