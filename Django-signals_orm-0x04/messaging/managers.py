from django.db import models

class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        """
        Returns unread messages for the given user.
        Uses .only() to fetch only needed fields.
        """
        return (
            self.filter(receiver=user, read=False)
            .only("id", "sender", "content", "timestamp")
        )