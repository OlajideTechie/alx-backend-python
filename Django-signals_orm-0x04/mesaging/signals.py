# signals.py
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
from .models import Message, MessageHistory, Notification
from django.contrib.auth.models import User


"""Signal to log message edits and maintain history."""
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                
                # Save old content into history
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content
                )
                
                # Mark the message as edited
                instance.edited = True
        except Message.DoesNotExist:
            pass

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            content=f"New message from {instance.sender.username}"
        )
        
@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    
    Message.objects.filter(user=instance).delete()
    Notification.objects.filter(user=instance).delete()
  
    print(f"Cleanup done for user {instance.username}")