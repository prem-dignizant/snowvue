from wallet.service import (
    check_balance,
    transfer,
    get_transactions)
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from agriculture_backend_app.custom_permission import IsVerified,IsRegistered,IsTncVerified
from rest_framework.views import APIView
from wallet.serializers import (
    FundTransferSerializer
)
from user.models import User
from rest_framework.response import Response
from agriculture_backend_app.utils import wrap_response
from wallet.models import Wallet
import stripe
from django.views.decorators.csrf import csrf_exempt
import pytz
from datetime import datetime
from rest_framework.renderers import JSONRenderer
from django.conf import settings
stripe.api_key = settings.STRIPE_API_KEY
class FundTransferView(APIView):
    permission_classes = [IsAuthenticated,IsVerified,IsRegistered,IsTncVerified]
    serializer_class = FundTransferSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        public_key=request.user.wallet_address
        transfer_status, trasnfer_response = transfer(serializer.validated_data["from_private_key"],serializer.validated_data["to_public_key"],serializer.validated_data["amount"],public_key=public_key)
        if transfer_status:
            Wallet.objects.create(transaction_id=trasnfer_response.get('transaction_id'), from_account=request.user.wallet_address, to_account=serializer.validated_data['to_public_key'], amount=serializer.validated_data['amount'], fee=float(trasnfer_response.get('fee_charged'))/10000000, created_at=trasnfer_response.get('created_at'), memo=trasnfer_response.get('memo') ,type=trasnfer_response.get('type'))
            return wrap_response(success=True,code="transfer_success",message="Transfer successful",status_code=status.HTTP_200_OK)
        return wrap_response(success=False, code=trasnfer_response.get('error_code'), errors=[{"field":"wallet","message": trasnfer_response.get('message')}], status_code=status.HTTP_400_BAD_REQUEST)
    
class BalanceView(APIView):
    permission_classes = [IsAuthenticated,IsVerified,IsRegistered,IsTncVerified]
    def get(self, request, *args, **kwargs):
        balance = check_balance(request.user.wallet_address)
        if balance is None:
            return wrap_response(success=False,code="balance_retrieval_failed",errors=[{"field":"wallet","message":"Failed to retrieve balance"}],status_code=status.HTTP_400_BAD_REQUEST)
        return wrap_response(success=True,code="balance_retrieved",data={'balance':balance},status_code=status.HTTP_200_OK)
    

class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated,IsVerified,IsRegistered,IsTncVerified]
    def get(self, request, *args, **kwargs):
        cursor=request.query_params.get('cursor',None)
        order=request.query_params.get('desc','true')
        if order=='true':
            desc=True
        elif order=='false':
            desc=False
        else:
            return wrap_response(success=False,code="invalid_order",errors=[{"field":"desc","message":"Invalid order"}],status_code=status.HTTP_400_BAD_REQUEST)
        transactions = get_transactions(public_key=request.user.wallet_address,cursor=cursor,desc=desc)
        if transactions is None:
            return wrap_response(success=False,code="transaction_history_retrieval_failed",errors=[{"field":"wallet","message":"Failed to retrieve transaction history"}],status_code=status.HTTP_400_BAD_REQUEST)
        return wrap_response(success=True,code="transaction_history_retrieved",data={'transactions':transactions},status_code=status.HTTP_200_OK)


class SuccessView(APIView):
    def get(self, request):
        return wrap_response(success=True,code="payment_success",message="Payment successful",status_code=status.HTTP_200_OK)
class CancelView(APIView):
    def get(self, request):
        return wrap_response(success=True,code="payment_cancelled",message="Payment cancelled",status_code=status.HTTP_200_OK)
class StripePaymentView(APIView):
    permission_classes = [IsAuthenticated,IsVerified,IsRegistered,IsTncVerified]
    def post(self, request, *args, **kwargs):
        request_data=request.data.get('values',{})
        if not request.user.stripe_id:
            try:
                if request.user.email is not None:
                    customer = stripe.Customer.create(
                        name=request.user.user_name,
                        email=request.user.email,
                        metadata={"user_id":request.user.user_id}
                    )
                elif request.user.mobile_number is not None:
                    customer = stripe.Customer.create(
                        name=request.user.user_name,
                        phone=request.user.mobile_number,
                        metadata={"user_id":request.user.user_id}
                    )
                else:
                    raise Exception("Email or mobile number is required")
                customer_data=customer.to_dict()
                request.user.stripe_id = customer_data['id']
                request.user.save()
            except Exception as e:
                return wrap_response(
                success=False,
                code='customer_creation_failed',
                errors=[{"field":"user","message":str(e)}],
                status_code=status.HTTP_400_BAD_REQUEST
                )
        try:
            price = "price_1QZS1GHPEt7mTfhhsKJkhJhw"
            subscription = 'simple_sub'
            checkout_session = stripe.checkout.Session.create(
                customer=request.user.stripe_id,
                line_items=[
                    {
                        'price': price,
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                billing_address_collection='required',
                success_url=request.META.get('HTTP_ORIGIN','http://localhost:3000') + '/subscriptions/success',
                cancel_url=request.META.get('HTTP_ORIGIN','http://localhost:3000') + '/subscriptions/failure',
                metadata={
                    'plan_id': subscription,
                    "valid" : "Monthly",
                    "first_name":request_data.get('first_name',''),
                    "last_name":request_data.get('last_name',''),
                    "organization_name":request_data.get('organization_name',''),
                    "position":request_data.get('position',''),
                    "address":request_data.get('address',''),
                    "organization_type":request_data.get('organization_type',''),
                    "consent":request_data.get('consent',False),
                }
            )
        except:
            return wrap_response(
            success=False,
            code='payment_failed',
            errors=[{"field":"user","message":"Payment failed"}],
            status_code=status.HTTP_400_BAD_REQUEST
            )
        return wrap_response(success=True,code="payment_success",data={'url':checkout_session.url},status_code=status.HTTP_200_OK)
    


#secrer=whsec_e5e583723cbb68db09d8341f98e210ee0021b9f90a3aad2cb7cda8560af213a1
@csrf_exempt 
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    response=None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        response = Response({"message": "Failed"},status=status.HTTP_400_BAD_REQUEST)
        # return wrap_response(success=False,code="invalid_payload",errors=[{"field":"payload","message":"Invalid payload"}],status_code=status.HTTP_400_BAD_REQUEST)
    
    except stripe.error.SignatureVerificationError :
        response = Response({"message": "Failed"},status=status.HTTP_400_BAD_REQUEST)
        # return wrap_response(success=False,code="invalid_signature",errors=[{"field":"signature","message":"Invalid signature"}],status_code=status.HTTP_400_BAD_REQUEST)

    if event['type'] == 'checkout.session.completed' and response is None:
        print('Payment was successful.')
        user=User.objects.filter(stripe_id=event['data']['object']['customer']).first() 
        if user is None:
            response = Response({"message": "Failed"},status=status.HTTP_400_BAD_REQUEST)
            # return wrap_response(success=False,code="user_not_found",errors=[{"field":"user","message":"User not found"}],status_code=status.HTTP_400_BAD_REQUEST)
        session = event['data']['object']  
        subscription_id = session.get('subscription')
        if subscription_id:
            subscription = stripe.Subscription.retrieve(subscription_id)
            current_period_end = subscription['current_period_end']
            expiry_date = datetime.fromtimestamp(current_period_end, tz=pytz.utc)
            user.subscription_expiry_date = expiry_date
            user.is_buyer = True
            user.save(update_fields=['subscription_expiry_date', 'is_buyer'])
            print(f"User subscription updated to: {expiry_date}")
        else:
            response = Response({"message": "Failed"},status=status.HTTP_400_BAD_REQUEST)
            # return wrap_response(success=False, code="subscription_not_found", errors=[{"field": "subscription", "message": "No subscription found"}], status_code=status.HTTP_400_BAD_REQUEST)
    if response is None:
        response = Response({"message": "Success"},status=status.HTTP_200_OK)
    # return wrap_response(success=True,code="payment_success",message="Payment successful",status_code=status.HTTP_200_OK) 
    response.accepted_renderer = JSONRenderer()
    response.accepted_media_type = 'application/json'
    response.renderer_context = {'request': request}
    return response