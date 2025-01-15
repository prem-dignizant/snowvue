from django.urls import path

from notification.views import (
    NotificationGetListView,
    NOtificationReadView

    
)
urlpatterns = [
    path('buyer_notification', NotificationGetListView.as_view(), name='all_buyer_notification'),
    path('read_notification',NOtificationReadView.as_view(),name="read_notification"),
]