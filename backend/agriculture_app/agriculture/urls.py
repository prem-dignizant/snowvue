from django.urls import path
from agriculture.views import (
    AgricultureDataViewSet,
    AgricultureDataStatusView,
    ContractRetrieveView,
    DataPurchaseView,
    ContractGetPriceView
)
urlpatterns=[
    path("data",AgricultureDataViewSet.as_view(),name="agriculture_data"),
    path('agriculture_data_status',AgricultureDataStatusView.as_view(),name="change_data_status"),
    path('contract',ContractRetrieveView.as_view(),name="contract"),
    path('purchase',DataPurchaseView.as_view(),name="data_purchase"),
    path('contract_price',ContractGetPriceView.as_view(),name="contract_price"),
]