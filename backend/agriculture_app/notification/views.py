from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from notification.models import NotificationRecipient
from django.utils.timezone import now
from agriculture_backend_app.utils import wrap_response
from rest_framework import status
from agriculture_backend_app.custom_permission import IsRegistered
from notification.serializers import NotificationReadSerializer
from rest_framework.pagination import PageNumberPagination
class NotificationPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size' 
    max_page_size = 20  
# Create your views here.
class NotificationGetListView(APIView):
    permission_classes = [IsAuthenticated,IsRegistered]
    pagination_class = NotificationPagination
    serializer_class = NotificationReadSerializer

    def get(self, request):
        notifications = NotificationRecipient.objects.select_related('notification__contract').filter(
            recipient=request.user,
        ).filter(
            Q(notification__contract__isnull=True) | Q(notification__contract__expiry_time__isnull=True) |Q(notification__contract__expiry_time__gt=now())
        ).filter(
            Q(notification__is_all=True) | Q(notification__to_buyer=request.user.is_buyer)
        ).order_by('-notification__created_at')
        paginator = self.pagination_class()
        paginated_notifications = paginator.paginate_queryset(notifications, request)
        all_notifications = []
        for notification in paginated_notifications:
            notification_dict = {
                'notification_id': notification.notification.notification_id,
                'created_at': str(notification.notification.created_at),
                'content': notification.notification.content,
                'is_read': notification.is_read,
                'type':notification.notification.type,
                'contract_id':notification.notification.contract.contract_id if notification.notification.contract else None
            }
            all_notifications.append(notification_dict)
        unread_count = notifications.filter(is_read=False).count()
        response_data = {
            'unread_count': unread_count,
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'notifications': all_notifications
        }
        return wrap_response(success=True, code='notification_retrieved',data=response_data,status_code=status.HTTP_200_OK)
        # return paginator.get_paginated_response({'notifications': all_notifications})
    # def post(self, request):
    #     serializer=self.serializer_class(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     notification_id=serializer.validated_data['notification_id']
    #     notification=NotificationRecipient.objects.select_related('notification').filter(notification_id=notification_id,recipient=request.user,notification__to_buyer=request.user.is_buyer).first()
    #     if notification is None:
    #         return wrap_response(success=False, code='notification_not_exist',message="Notification not exist",status_code=status.HTTP_404_NOT_FOUND)
    #     response_data = {
    #         'notification_id': notification.notification.notification_id,
    #         'created_at': str(notification.notification.created_at),
    #         'content': notification.notification.content,
    #         'data_points': json.loads(notification.notification.data_points)
    #     }
    #     return wrap_response(success=True, code='notification_retrieved',data=response_data,status_code=status.HTTP_200_OK)

class NOtificationReadView(APIView):
    permission_classes = [IsAuthenticated,IsRegistered]
    serializer_class = NotificationReadSerializer

    def get(self, request):
        all_notification=NotificationRecipient.objects.filter(Q(recipient=request.user) & Q(is_read=False))
        if len(all_notification)==0:
            return wrap_response(success=False, code='notification_not_exist',message="Notification not exist",errors=[{"field": "user", "message": "Notification not exist."}],status_code=status.HTTP_404_NOT_FOUND)
        all_notification.update(is_read=True)
        return wrap_response(success=True, code='read_success',message="All notifications marked as read",status_code=status.HTTP_200_OK)

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification_id=serializer.validated_data['notification_id']
        notification=NotificationRecipient.objects.filter(Q(notification_id=notification_id) & Q(recipient=request.user)).first()
        if notification is None:
            return wrap_response(success=False, code='notification_not_exist',message="Notification not exist",errors=[{"field": "notification_id", "message": "Notification not exist."}],status_code=status.HTTP_404_NOT_FOUND)
        notification.is_read=True
        notification.save()
        return wrap_response(success=True, code='read_success',message="Notification marked as read",status_code=status.HTTP_200_OK)