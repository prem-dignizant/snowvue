from django.db import models
from user.models import User
from agriculture.models import Contract
# Create your models here.
class Notification(models.Model):
    type_choise=(('contract','contract'),)
    notification_id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=255,null=True, blank=True)
    is_all = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    contract = models.ForeignKey(Contract,on_delete=models.CASCADE,null=True, blank=True,related_name="contract_notification")
    to_buyer = models.BooleanField(default=False)
    type=models.CharField(max_length=10,null=True,blank=True,choices=type_choise)
    def __str__(self):
        return str(self.notification_id)


class NotificationRecipient(models.Model):
    notification_recipient_id = models.AutoField(primary_key=True)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='recipients', null=True, blank=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together = ('notification', 'recipient')
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification', 'recipient']),
        ]

    def __str__(self):
        return str(self.notification_recipient_id)