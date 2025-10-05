# messaging/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

class MessagingSignalTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username="alice", password="pass123")
        self.receiver = User.objects.create_user(username="bob", password="pass123")

    def test_notification_created_on_new_message(self):
        # Create a message
        msg = Message.objects.create(sender=self.sender, receiver=self.receiver, content="Hello Bob!")

        # Check notification
        notif = Notification.objects.filter(user=self.receiver, message=msg).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.content, f"New message from {self.sender.username}")
        self.assertFalse(notif.is_read)