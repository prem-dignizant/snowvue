from django.contrib import admin
from notification.models import Notification, NotificationRecipient

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'is_all', 'to_buyer','created_at')
    search_fields = ('content', 'is_all')
    list_filter = ('is_all', 'created_at')
    def id(self, obj):
        return obj.notification_id
@admin.register(NotificationRecipient)
class NotificationRecipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'notification', 'is_read')
    search_fields = ('recipient__username', 'notification__content')
    def id(self, obj):
        return obj.notification_recipient_id