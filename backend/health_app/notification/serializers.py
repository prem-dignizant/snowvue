from rest_framework import serializers


class NotificationReadSerializer(serializers.Serializer):
    notification_id = serializers.IntegerField(required=True)