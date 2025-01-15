from django.urls import path

from health.views import (
    UserHealthProfileViewSet,
    HealthDataStatusView,
    ContractRetrieveView,
    DataPurchaseView,
    ContractGetPriceView
)
urlpatterns = [
    path('health_profile', UserHealthProfileViewSet.as_view(), name='health_profile'),
    path('health_data_status',HealthDataStatusView.as_view(),name="change_data_status"),
    path('contract',ContractRetrieveView.as_view(),name="contract"),
    path('purchase',DataPurchaseView.as_view(),name="data_purchase"),
    path('contract_price',ContractGetPriceView.as_view(),name="contract_price"),

]