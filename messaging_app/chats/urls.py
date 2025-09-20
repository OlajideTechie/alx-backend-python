
from django.urls import path, include
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet, CustomUserViewSet



router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet, basename='conversation')

messages_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
messages_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
	path('', include(router.urls)),
	path('', include(messages_router.urls)),

]
