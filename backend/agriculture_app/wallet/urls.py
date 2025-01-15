from django.urls import path
from wallet.views import  (
    FundTransferView,
    BalanceView,
    TransactionHistoryView,
    StripePaymentView,
    SuccessView,
    CancelView,
    stripe_webhook
)
urlpatterns=[
    path('transfer', FundTransferView.as_view(), name='fund_transfer_view'),
    path('balance', BalanceView.as_view(), name='balance_view'),
    path('transaction', TransactionHistoryView.as_view(), name='transaction_history_view'),
    path('payment/subscribe', StripePaymentView.as_view(), name='stripe_payment_view'),
    path('payment/success', SuccessView.as_view(), name='success_view'),
    path('payment/cancel', CancelView.as_view(), name='cancel_view'),
    path('webhook', stripe_webhook, name='webhook_view'),
]