# views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib import messages


""" View to delete a user and cascade delete related messages and notifications."""
@login_required
def delete_user(request):
    user = request.user
    username = user.username
    user.delete()
    messages.success(request, f"Account '{username}' and all related data deleted successfully.")
    return redirect("home")