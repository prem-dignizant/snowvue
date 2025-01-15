from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q,Exists, OuterRef
from health_backend_app.utils import wrap_response
from health.serializers import (
    UserHealthProfileSerializer,
    ChangeHealthDataStatusSerializer,
    ContractRetrieveSerializer,
    DataPurchaseSerializer,
    ContractGetPriceSerializer)
from health.models import UserHealthProfile,Contract,ContractRecipient
from rest_framework.permissions import IsAuthenticated
from health_backend_app.custom_permission import IsVerified,IsRegistered
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from django.conf import settings
from notification.models import Notification,NotificationRecipient
from user.models import User
from health_backend_app.service import (validate_secret_key,
                                        deploy_contract,
                                        invoke_initialize_health_data,
                                        get_wasm_bytes,
                                        get_price,
                                        transfer, store_s3,get_s3_data)
import json
from django.db import transaction
import os
from rest_framework.pagination import PageNumberPagination

class ContractPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size' 
    max_page_size = 20 
# Create your views here.
class UserHealthProfileViewSet(APIView):
    queryset = UserHealthProfile.objects.select_related('user')
    serializer_class = UserHealthProfileSerializer
    permission_classes = [IsAuthenticated,IsVerified,IsRegistered]
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if self.get_queryset().exists():
                return wrap_response(
                    success=False,
                    code="profile_exist",
                    errors=[{"field": "user", "message": "Profile already exists."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            profile = UserHealthProfile.objects.create(
                user=request.user,
                modified=timezone.now(),
                **serializer.validated_data
            )
            return wrap_response(
                success=True,
                code="profile_created",
                message="Profile created successfully.",
                data={"profile": serializer.data},
                status_code=status.HTTP_201_CREATED
            )
    def get(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            profile = self.get_queryset().first()
            last_profile_data_updated = profile.modified
            last_status_updated = profile.last_updated_time
            seven_days_ago = timezone.now() - timezone.timedelta(days=7)
            data_updated_in_last_seven_days = last_profile_data_updated > seven_days_ago
            status_updated_in_last_seven_days = last_status_updated > seven_days_ago
            
            serializer = self.serializer_class(profile)
            return wrap_response(
                success=True,
                code="profile_retrieved",
                data={
                    "profile": serializer.data,
                    "data_updated_in_last_seven_days": data_updated_in_last_seven_days,
                    "status_updated_in_last_seven_days": status_updated_in_last_seven_days},
                status_code=status.HTTP_200_OK
            )
        return wrap_response(
            success=False,
            code="profile_not_exist",
            errors=[{"field": "user", "message": "Profile does not exist."}],
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    def patch(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            profile = self.get_queryset().first()
            serializer = self.serializer_class(profile, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                profile.modified = timezone.now()
                serializer.save()
                return wrap_response(
                    success=True,
                    code="profile_updated",
                    message="Profile updated successfully.",
                    data=serializer.data,
                    status_code=status.HTTP_200_OK
                )
        return wrap_response(
            success=False,
            code="profile_not_exist",
            errors=[{"field": "user", "message": "Profile does not exist."}],
            status_code=status.HTTP_404_NOT_FOUND
        )
    

class HealthDataStatusView(APIView):
    serializer_class=ChangeHealthDataStatusSerializer
    permission_classes=[IsAuthenticated,IsVerified,IsRegistered]
    def get(self, request, *args, **kwargs):
        user=request.user
        health_profile=UserHealthProfile.objects.filter(user=user).first()
        if health_profile is None:
            return wrap_response(
                success=False,
                code='health_data_not_exist',
                message="Health profile data is not available for this user",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.serializer_class(data=health_profile.__dict__, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return wrap_response(
            success=True,
            code='health_data_status_retrieved',
            data=serializer.validated_data,
            status_code=status.HTTP_200_OK
        )
    def post(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user=request.user
        # is_secret_key_valid=validate_secret_key(serializer.validated_data['secret_key'],user.wallet_address)
        # if not is_secret_key_valid:
        #     return wrap_response(
        #         success=False,
        #         code='invalid_secret_key',
        #         message="Invalid secret key",
        #         errors=[{"field": "secret_key", "message": "Invalid secret key."}],
        #         status_code=status.HTTP_400_BAD_REQUEST
        #     )
        health_profile=UserHealthProfile.objects.filter(user=user).first()
        if health_profile is None:
            return wrap_response(
                success=False,
                code='health_data_not_exist',
                message="Health profile data is not available for this user",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        time_since_last_update = timezone.now() - health_profile.last_updated_time
        allowed_update_range = timezone.timedelta(hours=settings.HEALTH_DATA_UPDATE_HOURS_RANGE)
        if time_since_last_update < allowed_update_range:
            remaining_time = allowed_update_range - time_since_last_update
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes = remainder // 60
            hour_unit = "hour" if hours <= 1 else "hours"
            minute_unit = "minute" if minutes <= 1 else "minutes"
            formatted_time = f"{hours} {hour_unit} and {minutes} {minute_unit}"
            return wrap_response(
                success=False,
                code='seller_notification_update',
                errors=[{"field": "user", "message": f"Health data starus already updated. Please try again in {formatted_time} ."}],
                message=f"Health data status can only be updated once every {settings.HEALTH_DATA_UPDATE_HOURS_RANGE} hours. Please try again in {formatted_time} .",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            with transaction.atomic():
                update_fields = {field: serializer.validated_data[field] for field in serializer.validated_data}
                # update_fields['last_updated_time'] = timezone.now()
                for key, value in update_fields.items():
                    setattr(health_profile, key, value)
                # health_profile.save()

                # contract_path=os.path.join(settings.CONTRACT_PATH,'snowvue_asset.optimized.wasm')
                # with open(contract_path, "rb") as f:
                #         contract = f.read()
                # wasm_id="75375c0e4ca60ad5dc98c05b0f15ee4fb921762090f8654f479090720f97abab"
                # contract_id=deploy_contract(wasm_id=wasm_id,secret_key=serializer.validated_data['secret_key'])
                # if contract_id is None:
                #     raise ValueError("Contract deployment failed")
                # invoke_contract=invoke_initialize_health_data(contract_id=contract_id,health_data=health_profile.get_selling_data(),secret_key=serializer.validated_data['secret_key'])
                # if invoke_contract is None:
                #     raise ValueError("Contract invocation failed")
                # total_price=get_price(contract_id=contract_id)
                # if total_price is None:
                #     raise ValueError("Price generation failed")
        except Exception as e:
            return wrap_response(
                success=False,
                code='health_data_update_failed',
                errors=[{"field": "user", "message": str(e)}],
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        selling_data_points=health_profile.get_selling_fields()

        expiry_time=timezone.now()+timezone.timedelta(hours=settings.NOTIFICATION_EXPIRY_HOURS)

        new_contract=Contract(data_points=json.dumps(selling_data_points),
                            seller=user,
                            expiry_time=expiry_time)
        
        # Store data points in S3
        values = {field: getattr(new_contract.seller.health_profile, field, None) for field in selling_data_points}
        print(values)

        s3_url = store_s3(values)
        if s3_url is None:
            return wrap_response(success=False,code='transaction_failed',errors=[{"field":'contract_id',"message":'Transaction failed.'}],status_code=status.HTTP_400_BAD_REQUEST)
        new_contract.data_file = s3_url            
        new_contract.save()
        health_profile.last_updated_time=timezone.now()
        health_profile.save()
        new_notification = Notification.objects.create(to_buyer=True,
                                                       sender=user
                                                       ,content=f"{user.user_name}'s Health Data is available for buy",
                                                       contract=new_contract,
                                                       type='contract'
                                                       )
        all_user=User.objects.filter(is_registered=True,is_superuser=False).exclude(user_id=user.user_id)
        new_recipient=[]
        for recipient_user in all_user:
            new_recipient.append(NotificationRecipient(notification=new_notification,recipient=recipient_user))
        NotificationRecipient.objects.bulk_create(new_recipient)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'health_data_buyer_group',
            {
                'type': 'broadcast_message',
                'user_id':str(user.user_id),
                'data': {
                    'content':new_notification.content,
                    'notification_id':new_notification.notification_id,
                    'is_read':False,
                    'created_at':str(new_notification.created_at),
                    'type':new_notification.type,
                    'contract_id':new_contract.contract_id
                }
            }
        )
        return wrap_response(
            success=True,
            code='health_status_updated',
            message="Health data status updated successfully.",
            status_code=status.HTTP_200_OK,
        )
    

class ContractRetrieveView(APIView):
    serializer_class=ContractRetrieveSerializer
    permission_classes=[IsAuthenticated,IsVerified,IsRegistered]
    pagination_class=ContractPagination
    def get(self,request):
        excluded_contracts = ContractRecipient.objects.filter(
            buyer=request.user,
            is_purchased=True, 
            contract_id=OuterRef('pk')
        )
        all_contract=Contract.objects.filter(Q(expiry_time__isnull=True)|Q(expiry_time__gt=timezone.now())).exclude(seller=request.user).exclude(
            Exists(excluded_contracts)).order_by('expiry_time')
        paginator = self.pagination_class()
        paginated_contracts = paginator.paginate_queryset(all_contract, request)
        contract_list = []
        for contract in paginated_contracts:
            contract_dict={
                'contract_id':contract.contract_id,
                'user_name':contract.seller.user_name,
                'created_at':str(contract.created_at),
                'expiry_time':str(contract.expiry_time) if contract.expiry_time else None
            }
            contract_list.append(contract_dict)
        response_data = {
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'contracts': contract_list
        }
        return wrap_response(success=True,code='contract_retrieved',data=response_data,status_code=status.HTTP_200_OK)
    def post(self,request):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            contract_id=serializer.validated_data['contract_id']
            contract=Contract.objects.filter(contract_id=contract_id).exclude(seller=request.user).first()
            if contract is None:
                return wrap_response(success=False,code='contract_not_exist',errors=[{"field":'contract_id',"message":'contract_id does not exist.'}],status_code=status.HTTP_400_BAD_REQUEST)
            if contract.expiry_time and contract.expiry_time<=timezone.now():
                return wrap_response(success=False,code='contract_expired',errors=[{"field":'contract_id',"message":'contract expired.'}],status_code=status.HTTP_400_BAD_REQUEST)
            contract_recipient=ContractRecipient.objects.filter(contract=contract,buyer=request.user).first()
            if contract_recipient:
                if contract_recipient.is_purchased:
                    return wrap_response(success=False,code='contract_already_purchased',errors=[{"field":'contract_id',"message":'contract already purchased.'}],status_code=status.HTTP_400_BAD_REQUEST)
                
            response_data={
                "contract_id":contract.contract_id,
                "user_name":contract.seller.user_name,
                "created_at":str(contract.created_at),
                "expiry_time":str(contract.expiry_time) if contract.expiry_time else None,
                "data_points":json.loads(contract.data_points),
                "price":contract_recipient.price if contract_recipient else None,
                "selected_data_points":json.loads(contract_recipient.data_points) if contract_recipient else None
            }
            return wrap_response(success=True,code='contract_retrieved',data=response_data,status_code=status.HTTP_200_OK)

class ContractGetPriceView(APIView):
    serializer_class=ContractGetPriceSerializer
    permission_classes=[IsAuthenticated,IsVerified,IsRegistered]
    def post(self,request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=request.user
        contract_id=serializer.validated_data['contract_id']
        is_secret_key_valid=validate_secret_key(serializer.validated_data['secret_key'],user.wallet_address)
        if not is_secret_key_valid:
            return wrap_response(
                success=False,
                code='invalid_secret_key',
                message="Invalid secret key",
                errors=[{"field": "secret_key", "message": "Invalid secret key."}],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        contract=Contract.objects.filter(contract_id=contract_id).exclude(seller=request.user).first()  
        if contract is None or contract.expiry_time and contract.expiry_time<=timezone.now():
            return wrap_response(success=False,code='contract_not_exist',errors=[{"field":'contract_id',"message":'contract_id does not exist.'}],status_code=status.HTTP_400_BAD_REQUEST)
        data_points = serializer.validated_data['data_points']
        contract_data_points = json.loads(contract.data_points)
        if not all(point in contract_data_points for point in data_points):
            return wrap_response(
                success=False,
                code='invalid_data_points',
                errors=[{"field": 'data_points', "message": 'Invalid data points.'}],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        contract_recipient=ContractRecipient.objects.filter(contract=contract,buyer=request.user).first()
        if contract_recipient is  None:
            contract_recipient=ContractRecipient()
            contract_recipient.contract=contract
            contract_recipient.buyer=request.user
            contract_recipient.save()
        if contract_recipient.contract_secret is None:
            wasm_id='da28d7a18ec861b71502e521e6406d4ed0455b341e648b91225a3bfc5f049666'
            try:
                contract_id=deploy_contract(wasm_id=wasm_id,secret_key=serializer.validated_data['secret_key'])
                if contract_id is None:
                    raise ValueError("Contract deployment failed")
            except Exception as error:
                return wrap_response(success=False,code='contract_deploy_failed',errors=[{"field":'contract_id',"message":'contract deployment failed.'}],status_code=status.HTTP_400_BAD_REQUEST)
        if contract_recipient.is_purchased:
            return wrap_response(success=False,code='contract_already_purchased',errors=[{"field":'contract_id',"message":'contract already purchased.'}],status_code=status.HTTP_400_BAD_REQUEST)
            

        else:
            contract_id=contract_recipient.contract_secret
        total_price=get_price(contract_id=contract_id,data_points=serializer.validated_data['data_points'],user_id=request.user.user_id)
        if total_price is None:
            return wrap_response(success=False,code='contract_deploy_failed',errors=[{"field":'contract_id',"message":'contract deployment failed for getting price.'}],status_code=status.HTTP_400_BAD_REQUEST)
        contract_recipient.price=total_price
        contract_recipient.contract_secret=contract_id
        contract_recipient.data_points=json.dumps(serializer.validated_data['data_points'])
        contract_recipient.save()
        return wrap_response(success=True,code='contract_price_retrieved',data={"total_price":total_price},status_code=status.HTTP_200_OK)
    
 # Create a JSON file and upload to S3


class DataPurchaseView(APIView):
    serializer_class=DataPurchaseSerializer
    permission_classes=[IsAuthenticated,IsVerified,IsRegistered]


    def post(self,request):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            contract_id=serializer.validated_data['contract_id']
            contract=Contract.objects.select_related('seller').filter(contract_id=contract_id).exclude(seller=request.user).first()
            if contract is None:
                return wrap_response(success=False,code='contract_not_exist',errors=[{"field":'contract_id',"message":'contract_id does not exist.'}],status_code=status.HTTP_400_BAD_REQUEST)
            if contract.expiry_time and contract.expiry_time<=timezone.now():
                return wrap_response(success=False,code='contract_expired',errors=[{"field":'contract_id',"message":'contract expired.'}],status_code=status.HTTP_400_BAD_REQUEST)
            contract_recipient=ContractRecipient.objects.filter(contract=contract,buyer=request.user).first()
            if contract_recipient and contract_recipient.is_purchased:
                return wrap_response(success=False,code='contract_already_purchased',errors=[{"field":'contract_id',"message":'contract already purchased.'}],status_code=status.HTTP_400_BAD_REQUEST)
            if contract_recipient is None:
                contract_recipient=ContractRecipient()
                contract_recipient.contract=contract
                contract_recipient.buyer=request.user
                # contract_recipient.save()
                is_secret_key_valid=validate_secret_key(serializer.validated_data['secret_key'],request.user.wallet_address)
                if not is_secret_key_valid:
                    return wrap_response(success=False,code='secret_key_invalid',errors=[{"field":'secret_key',"message":'secret_key is invalid.'}],status_code=status.HTTP_400_BAD_REQUEST)
                # if contract_recipient.contract_secret is None:
                wasm_id='da28d7a18ec861b71502e521e6406d4ed0455b341e648b91225a3bfc5f049666'
                try:
                    contract_id=deploy_contract(wasm_id=wasm_id,secret_key=serializer.validated_data['secret_key'])
                    if contract_id is None:
                        raise ValueError("Contract deployment failed")
                    contract_recipient.contract_secret=contract_id
                except Exception as error:
                    return wrap_response(success=False,code='contract_deploy_failed',errors=[{"field":'contract_id',"message":'contract deployment failed.'}],status_code=status.HTTP_400_BAD_REQUEST)
            else:
                contract_id=contract_recipient.contract_secret
            data_points = serializer.validated_data['data_points']
            contract_data_points = json.loads(contract.data_points)
            if not all(point in contract_data_points for point in data_points):
                return wrap_response(
                    success=False,
                    code='invalid_data_points',
                    errors=[{"field": 'data_points', "message": 'Invalid data points.'}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            contract_recipient.price=get_price(contract_id=contract_id,data_points=serializer.validated_data['data_points'],user_id=request.user.user_id)
            contract_recipient.data_points=json.dumps(serializer.validated_data['data_points'])
            contract_recipient.save()
            is_transaction=transfer(contract_recipient.contract_secret,serializer.validated_data['secret_key'],data_points,request.user.user_id,contract.seller.wallet_address)
            if not is_transaction:
                return wrap_response(success=False,code='transaction_failed',errors=[{"field":'contract_id',"message":'Transaction failed.'}],status_code=status.HTTP_400_BAD_REQUEST)
            
            contract_recipient.is_purchased=True
            contract_recipient.save()
            return wrap_response(success=True,code='transaction_success',status_code=status.HTTP_200_OK)

    def get(self, request):
        pk = request.query_params.get('contract_recipient_id','')
        if not pk.isnumeric():
            return wrap_response(success=False,code='contract_recipient_id invalid',errors=[{"field":'contract_recipient_id',"message":'contract_recipient_id must be integer.'}],status_code=status.HTTP_400_BAD_REQUEST)
        try:
            contract_recipient = ContractRecipient.objects.get(contract_recipient_id=int(pk),buyer=request.user, is_purchased=True)
        except ContractRecipient.DoesNotExist:
            return wrap_response(success=False,code='contract_recipient_not_exist',errors=[{"field":'contract_recipient_id',"message":'contract_recipient_id does not exist.'}],status_code=status.HTTP_400_BAD_REQUEST)
        s3_url = contract_recipient.contract.data_file
        if s3_url is None:
            return wrap_response(success=False,errors=[{"field":'data_file',"message":'data_file not exists'}],status_code=status.HTTP_400_BAD_REQUEST) 
        data = get_s3_data(s3_url)
        data_keys = contract_recipient.data_points
        filter_data = {key:value for key,value in data.items() if key in data_keys}

        if not filter_data:
            return wrap_response(success=False,code='S3 service error',errors='Error Occur while downloading from S3',status_code=status.HTTP_400_BAD_REQUEST)
        return wrap_response(success=True,code='data retrieved',data=filter_data,status_code=status.HTTP_200_OK)         

