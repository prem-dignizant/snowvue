import qrcode
import base64 
from qrcode.image.styledpil import StyledPilImage
from urllib.parse import urlparse, parse_qs
from io import BytesIO
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from agriculture_backend_app.custom_permission import IsVerified,IsRegistered,IsTncVerified,IsSubscribed
from .models import (
    User,
    EmailVerificationToken,
    UserProfile,
    MobileVerificationToken
)
from rest_framework.views import APIView
from rest_framework.generics import (
    CreateAPIView,
    UpdateAPIView,
    )
from .serializers import (
    UserSerializer,
    UserMobileSerializer,
    EmailVerificationSerializer,
    UserProfileSerializer,
    ResendEmailVerificationSerializer,
    TOTPVerifySerializer,
    EmailObtainViewSerializer,
    UserLogoutSerializer,
    UserLoginSerializer,
    UserRefreshSerializer,
    UserNameObtainViewSerializer,
    TOTPCreateSerializer,
    TOTPRecoverySerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    MobileObtainViewSerializer,
    MobileVerificationSerializer,
    ResendMobileVerificationSerializer,
    UserLoginMobileSerializer,
    ForgotPasswordMobileSerializer
)
from .service import (
    send_verification_email,
    get_user_totp_device,
    generate_token,
    unzip_token,
    create_wallet,
    fund_wallet,
    send_forgot_password_email,
    validate_and_format_number,
    send_verification_sms,
    send_forgot_password_sms
    )
import random
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from agriculture_backend_app.utils  import wrap_response

class EmailObtainView(APIView):
    permission_classes = [AllowAny]
    authentication_classes=[]
    def post(self, request):
        serializer = EmailObtainViewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user = User.objects.get(email=serializer.validated_data["email"])
                return wrap_response(success=True, code="email_exist",data={'email':serializer.validated_data["email"]}, status_code=status.HTTP_200_OK)
            except User.DoesNotExist:
                return wrap_response(success=False, code="email_not_exist",errors=[{"field":'email',"message":'Email address not exist.'}] ,status_code=status.HTTP_404_NOT_FOUND)

class MobileObtainView(APIView):
    permission_classes = [AllowAny]
    authentication_classes=[]
    def post(self, request):
        serializer = MobileObtainViewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user = User.objects.get(mobile_number=serializer.validated_data["mobile_number"])
                return wrap_response(success=True, code="number_exist",data={'mobile_number':serializer.validated_data["mobile_number"]}, status_code=status.HTTP_200_OK)
            except User.DoesNotExist:
                return wrap_response(success=False, code="mobile_not_exist",errors=[{"field":'mobile_number',"message":'Mobile number not exist.'}] ,status_code=status.HTTP_404_NOT_FOUND)


class UserNameObtainView(APIView):
    permission_classes = [AllowAny]
    authentication_classes=[]
    def post(self, request):
        serializer = UserNameObtainViewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if User.objects.filter(user_name=serializer.validated_data["user_name"]).exists():
                return wrap_response(success=False, code="user_exist",errors=[{"field":'user_name',"message":'user_name already exist.'}], status_code=status.HTTP_400_BAD_REQUEST)
            return wrap_response(success=True, code="user_not_exist", status_code=status.HTTP_200_OK)
class UserRegistrationView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    authentication_classes=[]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data.pop('confirm_password', None)
            try:
                User.objects.get(email=serializer.validated_data["email"])
                return wrap_response(
                    success=False,
                    code="user_exist",
                    errors=[{"field":"email","message": "User with this email already exists."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            except :
                pass
            try:
                User.objects.get(user_name=serializer.validated_data["user_name"])
                return wrap_response(
                    success=False,
                    code="user_exist",
                    errors=[{"field":"user_name","message": "User with this user name already exists."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            except :
                pass
            user = User.objects.create_user(**serializer.validated_data)
            key = "".join(["{}".format(random.randint(0, 9)) for _ in range(0, 6)])
            token = EmailVerificationToken.objects.create(
                user=user,
                token=key,
                expiry_date=timezone.now() + timezone.timedelta(minutes=5),
            )

            res = send_verification_email(
                serializer.validated_data["email"], token.token
            )
            if not res:
                User.objects.filter(user_id=user.user_id).delete()
                return wrap_response(
                    success=False,
                    code="failed_to_send_verification_email",
                    errors=[{"field":"email","message": "Failed to send verification email."}],
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return wrap_response(
                success=True,
                code="user_created",
                message="User created successfully.",
                status_code=status.HTTP_201_CREATED
            )   
        
class UserRegistrationMobileView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserMobileSerializer
    permission_classes = [AllowAny]
    authentication_classes=[]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data.pop('confirm_password', None)
            mobile_status,mobilenumber,country_code=validate_and_format_number(serializer.validated_data["mobile_number"])
            if not mobile_status:
                return wrap_response(
                    success=False,
                    code="validation_error",
                    errors=[{"field":"mobile_number","message": "Invalid mobile number.Please enter a valid mobile number."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            serializer.validated_data["country_code"] = country_code
            try:
                User.objects.get(mobile_number=serializer.validated_data["mobile_number"])
                return wrap_response(
                    success=False,
                    code="user_exist",
                    errors=[{"field":"mobile_number","message": "User with this mobile number already exists."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            except :
                pass
            try:
                User.objects.get(user_name=serializer.validated_data["user_name"])
                return wrap_response(
                    success=False,
                    code="user_exist",
                    errors=[{"field":"user_name","message": "User with this user name already exists."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            except :
                pass
            serializer.validated_data["is_registered_with_email"] = False
            user = User.objects.create_user(**serializer.validated_data)
            key = "".join(["{}".format(random.randint(0, 9)) for _ in range(0, 6)])
            token = MobileVerificationToken.objects.create(
                user=user,
                token=key,
                expiry_date=timezone.now() + timezone.timedelta(minutes=5),
            )
            res=send_verification_sms(user.mobile_number,token.token)
            if not res:
                User.objects.filter(user_id=user.user_id).delete()
                return wrap_response(
                    success=False,
                    code="failed_to_send_verification_sms",
                    errors=[{"field":"mobile_number","message": "Failed to send verification sms."}],
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return wrap_response(
                success=True,
                code="user_created",
                message="User created successfully.",
                status_code=status.HTTP_201_CREATED
            )   
class ResendEmailVerificationView(CreateAPIView):
    permission_classes = [AllowAny]
    authentication_classes=[]
    serializer_class = ResendEmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user=User.objects.get(email=serializer.validated_data["email"])
            except User.DoesNotExist:
                return wrap_response(
                    success=False,
                    code="user_not_exist",
                    errors=[{"field":"email","message": "User with this email does not exist."}],
                    status_code=status.HTTP_404_NOT_FOUND
                )
            if user.is_email_verified:
                return wrap_response(
                    success=False,
                    code="email_already_verified",
                    errors=[{"field":"email","message": "Email already verified."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            try:
                EmailVerificationToken.objects.get(user=user).delete()
            except EmailVerificationToken.DoesNotExist:
                pass
            key = "".join(["{}".format(random.randint(0, 9)) for _ in range(0, 6)])
            token = EmailVerificationToken.objects.create(
                user=user,
                token=key,
                expiry_date=timezone.now() + timezone.timedelta(minutes=5),
            )
            res = send_verification_email(
                serializer.validated_data["email"], key
            )
            if not res:
                token.delete()
                return wrap_response(
                    success=False,
                    code="failed_to_send_verification_email",
                    errors=[{"field":"email","message": "Failed to send verification email."}],
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return wrap_response(
                success=True,
                code="email_sent",
                message="Verification email sent successfully.",
                status_code=status.HTTP_201_CREATED
            )
        
class ResendMobileVerificationView(CreateAPIView):
    permission_classes = [AllowAny]
    authentication_classes=[]
    serializer_class = ResendMobileVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user=User.objects.get(mobile_number=serializer.validated_data["mobile_number"])
            except User.DoesNotExist:
                return wrap_response(
                    success=False,
                    code="user_not_exist",
                    errors=[{"field":"mobile_number","message": "User with this mobile number does not exist."}],
                    status_code=status.HTTP_404_NOT_FOUND
                )
            if user.is_mobile_verified:
                return wrap_response(
                    success=False,
                    code="mobile_number_already_verified",
                    errors=[{"field":"mobile_number","message": "Mobile number already verified."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            try:
                MobileVerificationToken.objects.get(user=user).delete()
            except MobileVerificationToken.DoesNotExist:
                pass
            key = "".join(["{}".format(random.randint(0, 9)) for _ in range(0, 6)])
            token = MobileVerificationToken.objects.create(
                user=user,
                token=key,
                expiry_date=timezone.now() + timezone.timedelta(minutes=5),
            )
            res=send_verification_sms(user.mobile_number,token.token)
            if not res:
                token.delete()
                return wrap_response(
                    success=False,
                    code="failed_to_send_verification_sms",
                    errors=[{"field":"mobile_number","message": "Failed to send verification sms."}],
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return wrap_response(
                success=True,
                code="sms_sent",
                message="Verification sms sent successfully.",
                status_code=status.HTTP_201_CREATED
            )
    
class EmailVerificationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes=[]
    serializer_class = EmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            try:
                instance=User.objects.get(email=serializer.validated_data["email"])
            except User.DoesNotExist:
                return wrap_response(
                    success=False,
                    code="user_not_exist",
                    errors=[{"field":"email","message": "User with this email does not exist."}],
                    status_code=status.HTTP_404_NOT_FOUND
                )
            if instance.is_email_verified:
                return wrap_response(
                    success=False,
                    code="email_already_verified",
                    errors=[{"field":"email","message": "Email already verified."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            try:
                email_verification_token=EmailVerificationToken.objects.get(user=instance)
            except EmailVerificationToken.DoesNotExist:
                return wrap_response(
                    success=False,
                    code="token_not_exist",
                    errors=[{"field":"email","message": "Verification token does not exist for the provided email."}],
                    status_code=status.HTTP_404_NOT_FOUND
            )
            if email_verification_token.token != serializer.validated_data["token"]:
                return wrap_response(
                    success=False,
                    code="invalid_token",
                    errors=[{"field":"token","message": "Invalid verification code."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            if email_verification_token.expiry_date < timezone.now():
                email_verification_token.delete()
                return wrap_response(
                    success=False,
                    code="token_expired",
                    errors=[{"field":"email","message": "The verification code has expired and should be verified within 5 minutes of sending."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            instance.is_active = True
            instance.is_email_verified = True
            instance.save()
            email_verification_token.delete()
            token=generate_token(instance.user_id)
            return wrap_response(
                success=True,
                code="email_verified",
                message="Email verified successfully.",
                status_code=status.HTTP_200_OK,
                data={'auth_token':token,'is_registered':instance.is_registered,'is_mfa_setup':instance.mfa_enabled,'is_confirm_tnc':instance.is_confirm_tnc}
            )
        

class MobileVerificationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes=[]
    serializer_class = MobileVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            try:
                instance=User.objects.get(mobile_number=serializer.validated_data["mobile_number"])
            except User.DoesNotExist:
                return wrap_response(
                    success=False,
                    code="user_not_exist",
                    errors=[{"field":"mobile_number","message": "User with this mobile number does not exist."}],
                    status_code=status.HTTP_404_NOT_FOUND
                )
            if instance.is_mobile_verified:
                return wrap_response(
                    success=False,
                    code="mobile_number_already_verified",
                    errors=[{"field":"mobile_number","message": "Mobile number already verified."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            try:
                mobile_verification_token=MobileVerificationToken.objects.get(user=instance)
            except MobileVerificationToken.DoesNotExist:
                return wrap_response(
                    success=False,
                    code="token_not_exist",
                    errors=[{"field":"mobile_number","message": "Verification token does not exist for the provided mobile number."}],
                    status_code=status.HTTP_404_NOT_FOUND
            )
            if mobile_verification_token.token != serializer.validated_data["token"]:
                return wrap_response(
                    success=False,
                    code="invalid_token",
                    errors=[{"field":"token","message": "Invalid verification code."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            if mobile_verification_token.expiry_date < timezone.now():
                mobile_verification_token.delete()
                return wrap_response(
                    success=False,
                    code="token_expired",
                    errors=[{"field":"mobile_number","message": "The verification code has expired and should be verified within 5 minutes of sending."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            instance.is_active = True
            instance.is_mobile_verified = True
            instance.save()
            mobile_verification_token.delete()
            token=generate_token(instance.user_id)
            return wrap_response(
                success=True,
                code="mobile_number_verified",
                message="Mobile number verified successfully.",
                status_code=status.HTTP_200_OK,
                data={'auth_token':token,'is_registered':instance.is_registered,'is_mfa_setup':instance.mfa_enabled,'is_confirm_tnc':instance.is_confirm_tnc}
            )
        
class UserLoginView(CreateAPIView):
    permission_classes = [AllowAny]
    authentication_classes=[]
    serializer_class = UserLoginSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
        except User.DoesNotExist:
            return wrap_response(
                success=False,
                code="user_not_exist",
                errors=[{"field":"email","message": "User with this email does not exist."}],
                status_code=status.HTTP_404_NOT_FOUND
            )
        verified_password=user.check_password(serializer.validated_data['password'])   
        if not verified_password:
            return wrap_response(
                success=False,
                code="invalid_credentials",
                errors=[{"field":"password","message": "Invalid credentials."}],
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        if not user.is_active or not user.is_email_verified:
            try:
                EmailVerificationToken.objects.get(user=user).delete()
            except EmailVerificationToken.DoesNotExist:
                pass
            key = "".join(["{}".format(random.randint(0, 9)) for _ in range(0, 6)])
            res = send_verification_email(
                serializer.validated_data["email"], key
            )
            token = EmailVerificationToken.objects.create(
                user=user,
                token=key,
                expiry_date=timezone.now() + timezone.timedelta(minutes=5),
            )
            if not res:
                token.delete()
                return wrap_response(
                    success=False,
                    code="failed_to_send_verification_email",
                    errors=[{"field":"email","message": "Failed to send verification email."}],
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return wrap_response(
                success=False,
                code="user_not_active",
                errors=[{"field":"email","message": "User is not active. Please verify your email."}],
                status_code=status.HTTP_403_FORBIDDEN
            )
        token=generate_token(user.user_id)
        return wrap_response(
        success=True,
        code="login_successful",
        message="Login successful",
        data={'is_mfa_setup': user.mfa_enabled, 'is_registered': user.is_registered, 'auth_token': token,'is_confirm_tnc':user.is_confirm_tnc},
        status_code=status.HTTP_200_OK
        )

class UserLoginMobileView(CreateAPIView):
    permission_classes = [AllowAny]
    authentication_classes=[]
    serializer_class = UserLoginMobileSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(mobile_number=serializer.validated_data['mobile_number'])
        except User.DoesNotExist:
            return wrap_response(
                success=False,
                code="user_not_exist",
                errors=[{"field":"mobile_number","message": "User with this mobile number does not exist."}],
                status_code=status.HTTP_404_NOT_FOUND
            )
        verified_password=user.check_password(serializer.validated_data['password'])   
        if not verified_password:
            return wrap_response(
                success=False,
                code="invalid_credentials",
                errors=[{"field":"password","message": "Invalid credentials."}],
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        if not user.is_active or not user.is_mobile_verified:
            try:
                MobileVerificationToken.objects.get(user=user).delete()
            except MobileVerificationToken.DoesNotExist:
                pass
            key = "".join(["{}".format(random.randint(0, 9)) for _ in range(0, 6)])
            res = True
            token = MobileVerificationToken.objects.create(
                user=user,
                token=key,
                expiry_date=timezone.now() + timezone.timedelta(minutes=5),
            )
            if not res:
                token.delete()
                return wrap_response(
                    success=False,
                    code="failed_to_send_verification_sms",
                    errors=[{"field":"mobile_number","message": "Failed to send verification sms."}],
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return wrap_response(
                success=False,
                code="user_not_active",
                errors=[{"field":"mobile_number","message": "User is not active. Please verify your mobile number."}],
                status_code=status.HTTP_403_FORBIDDEN
            )
        token=generate_token(user.user_id)
        return  wrap_response(
        success=True,
        code="login_successful",
        message="Login successful",
        data={'is_mfa_setup': user.mfa_enabled, 'is_registered': user.is_registered, 'auth_token': token,'is_confirm_tnc':user.is_confirm_tnc},
        status_code=status.HTTP_200_OK
        )
        

class UserTokenRefreshView( CreateAPIView):
    permission_classes = [AllowAny]
    authentication_classes=[]
    serializer_class = UserRefreshSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh = RefreshToken(serializer.validated_data["refresh"])
        except Exception as e:
            return wrap_response(
                success=False,
                code="invalid_refresh_token",
                errors=[{"field":"refresh","message": str(e)}],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        access_token = refresh.access_token
        user=User.objects.get(user_id=refresh["user_id"])
        return wrap_response(
            success=True,
            code="token_refreshed",
            data={'access':str(access_token)},
            status_code=status.HTTP_200_OK
        )
    
class PolicyView(APIView):
    permission_classes = []
    authentication_classes=[]
    serializer_class=TOTPCreateSerializer
    def post(self, request, format=None): 
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth_token = serializer.validated_data['auth_token']
        user_id, error =unzip_token(auth_token)
        if user_id is None:
            if error=="invalid_token":
                message="Invalid token"
            else:
                message="Expired token"
            return wrap_response(
                success=False,
                code=error,
                errors=[{"field":"auth_token","message":message}],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(user_id=user_id)
            user.is_confirm_tnc=True
            user.save()
            return wrap_response(
                success=True,
                code="tnc_confirmed",
                message="TnC confirmed",
                data={'is_registered':user.is_registered,'is_mfa_setup':user.mfa_enabled},
                status_code=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return wrap_response(
                success=False,
                code="user_not_found",
                errors=[{"field":"auth_token","message": "User not found."}],
                status_code=status.HTTP_404_NOT_FOUND
            )
class TOTPCreateView(APIView):
    permission_classes = []
    authentication_classes=[]
    serializer_class = TOTPCreateSerializer
    def post(self, request, format=None):  
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth_token = serializer.validated_data['auth_token']
        user_id, error =unzip_token(auth_token)
        if user_id is None:
            if error=="invalid_token":
                message="Invalid token"
            else:
                message="Expired token"
            return wrap_response(
                success=False,
                code=error,
                errors=[{"field":"auth_token","message":message}],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(user_id=user_id)
            if not user.is_confirm_tnc:
                return wrap_response(
                    success=False,
                    code="tnc_not_confirmed",
                    errors=[{"field":"auth_token","message": "Please confirm T&C."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return wrap_response(
                success=False,
                code="user_not_found",
                errors=[{"field":"auth_token","message": "User not found."}],
                status_code=status.HTTP_404_NOT_FOUND
            )
        if not user.mfa_enabled:
            device = get_user_totp_device(self, user)
            if not device:
                if user.is_registered_with_email:
                    device_name=f"Snowvue: {user.email}"
                else:
                    device_name=f"Snowvue: {user.mobile_number}"
                device = user.totpdevice_set.create(confirmed=False,name=device_name)
            url = device.config_url
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            secret_code = query_params.get('secret', [None])[0]
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            img= qr.make_image(image_factory=StyledPilImage, embeded_image_path="media/LOGO.png")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            img_base64 = "data:image/png;base64," + img_base64
            return wrap_response(
                success=True,
                code="qr_generated",
                data={"secret_code": secret_code, "qr_code": img_base64},
                status_code=status.HTTP_200_OK
            )
        return wrap_response(
            success=False,
            code="mfa_already_enabled",
            errors=[{"field":"mfa","message": "MFA is already enabled for this user."}],
            status_code=status.HTTP_403_FORBIDDEN
        )
class TOTPVerifyView(APIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = TOTPVerifySerializer
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        auth_token = serializer.validated_data['auth_token']
        user_id, error =unzip_token(auth_token)
        if user_id is None:
            if error=="invalid_token":
                message="Invalid token"
            else:
                message="Expired token"
            return wrap_response(
                success=False,
                code=error,
                errors=[{"field":"auth_token","message":message}],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(user_id=user_id)
            if not user.is_confirm_tnc:
                return wrap_response(
                    success=False,
                    code="tnc_not_confirmed",
                    errors=[{"field":"auth_token","message": "Please confirm T&C."}],
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return wrap_response(
                success=False,
                code="user_not_found",
                errors=[{"field":"auth_token","message": "User not found."}],
                status_code=status.HTTP_404_NOT_FOUND
            )
        device = get_user_totp_device(self,user)
        if device is None:
            return wrap_response(
                success=False,
                code="mfa_not_enabled",
                errors=[{"field":"auth_token","message": "Please setup mfa authentication."}],
                status_code=status.HTTP_404_NOT_FOUND
            )
        if  device.verify_token(token):
            recovery_flag=device.confirmed
            if not device.confirmed:
                device.confirmed = True
                device.save()
            user.mfa_enabled = True
            user.save()
            data={}
            data["is_registered"]=user.is_registered
            if not recovery_flag:
                data['recovery_code']=user.recovery_code
                data["is_mfa_setup"]=False
            else:
                data["is_mfa_setup"]=True
            if user.is_registered:
                refresh_token=RefreshToken.for_user(user)
                access_token=refresh_token.access_token
                access_token = str(access_token)
                refresh_token= str(refresh_token)
                data['access'] = access_token
                data['refresh'] = refresh_token
                
            else:
                token=generate_token(user.user_id)
                data["auth_token"]=token
            return wrap_response(
                success=True,
                code="login_successful",
                message="Login successful",
                status_code=status.HTTP_200_OK,
                data=data
            )
        return wrap_response(
            success=False,
            code="invalid_code",
            errors=[{"field":"token","message": "2FA Authentication code is invalid or expired."}],
            status_code=status.HTTP_400_BAD_REQUEST
        )

class TOTPRecoveryView(UpdateAPIView):
    permission_classes=[]
    authentication_classes=[]
    serializer_class=TOTPRecoverySerializer
    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recovery_code = serializer.validated_data['recovery_code']
        auth_token = serializer.validated_data['auth_token']
        user_id, error =unzip_token(auth_token)
        if user_id is None:
            if error=="invalid_token":
                message="Invalid token"
            else:
                message="Expired token"
            return wrap_response(
                success=False,
                code=error,
                errors=[{"field":"auth_token","message":message}],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return wrap_response(
                success=False,
                code="user_not_found",
                errors=[{"field":"auth_token","message": "User not found."}],
                status_code=status.HTTP_404_NOT_FOUND
            )
        device = get_user_totp_device(self,user)
        if device is None:
            return wrap_response(
                success=False,
                code="mfa_not_setup",
                errors=[{"field":"auth_token","message": "2FA is not setup for this user."}],
                status_code=status.HTTP_403_FORBIDDEN
            )
        if recovery_code != user.recovery_code:
            return wrap_response(
                success=False,
                code="invalid_recovery_code",
                errors=[{"field":"recovery_code","message": "Invalid recovery code."}],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        device.delete()
        user.mfa_enabled = False
        user.recovery_code=None
        user.save()
        return wrap_response(
            success=True,
            code="recovery_successful",
            message="Recovery successful",
            status_code=status.HTTP_200_OK
        )
class UserLogoutView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLogoutSerializer
    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            if token['user_id']==request.auth['user_id']:
                token.blacklist()
                return wrap_response(
                    success=True,
                    code="logged_out",
                    message="User logged out successfully.",
                    status_code=status.HTTP_200_OK
                )
        except Exception as e:
            return wrap_response(
                success=False,
                code="invalid_refresh_token",
                errors=[{"field":"refresh","message": str(e)}],
                status_code=status.HTTP_400_BAD_REQUEST
            )

class ProfileView(APIView):
    permission_classes = [IsAuthenticated,IsVerified,IsRegistered,IsTncVerified]   
    def get_permissions(self):
        if self.request.method == 'POST':
            return []  
        return super().get_permissions()
    def get_authenticators(self):
        if self.request.method == 'POST':
            return []
        return super().get_authenticators()
    def post(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth_token = request.data.get("auth_token",None)
        if auth_token is None or not isinstance(auth_token, str):
            return wrap_response(
                success=False,
                code="validation_error",
                errors=[{"field":"auth_token","message": "Authentication token is required."}],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        user_id, error =unzip_token(auth_token)
        if user_id is None:
            if error=="invalid_token":
                message="Invalid token"
            else:
                message="Expired token"
            return wrap_response(
                success=False,
                code=error,
                errors=[{"field":"auth_token","message":message}],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return wrap_response(
                success=False,
                code="user_not_found",
                errors=[{"field":"auth_token","message": "User not found."}],
                status_code=status.HTTP_404_NOT_FOUND
            )
        if UserProfile.objects.filter(user=user).exists():
            return wrap_response(
                success=False,
                code="profile_exist",
                errors=[{"field": "user", "message": "Profile already exists."}],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        profile = UserProfile.objects.create(
            user=user,
            **serializer.validated_data
        )
        user.is_registered = True
        user.save()
        response_serializer = UserProfileSerializer(profile)
        refresh_token = RefreshToken.for_user(user)
        access_token = str(refresh_token.access_token)
        return wrap_response(
            success=True,
            code="profile_created",
            message="Profile created successfully.",
            data={"profile": response_serializer.data,"access":access_token,"refresh":str(refresh_token)},
            status_code=status.HTTP_201_CREATED
        )

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            return wrap_response(
                success=False,
                code="profile_not_exist",
                errors=[{"field": "user", "message": "Profile does not exist."}],
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UserProfileSerializer(profile)
        return wrap_response(
            success=True,
            code="profile_retrieved",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def patch(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            return wrap_response(
                success=False,
                code="profile_not_exist",
                errors=[{"field": "user", "message": "Profile does not exist."}],
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return wrap_response(
                success=True,
                code="profile_updated",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )


class UserWalletViewSet(APIView):
    permission_classes = [IsAuthenticated,IsVerified,IsRegistered]
    def post(self, request, *args, **kwargs):
        if request.user.wallet_address is None:
            wallet_address_list=create_wallet()
            if wallet_address_list is None:
                return wrap_response(
                    success=False,
                    code="wallet_creation_failed",
                    errors=[{"field": "wallet_address", "message": "Failed to create wallet address."}],
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            wallet_fund=fund_wallet(wallet_address_list[0])
            if wallet_fund is None:
                return wrap_response(
                    success=False,
                    code="wallet_funding_failed",
                    errors=[{"field": "wallet_address", "message": "Failed to fund wallet address."}],
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            request.user.wallet_address = wallet_address_list[0]
            request.user.save()
            return wrap_response(
                success=True,
                code="wallet_created",
                message="Wallet created successfully.",
                data={"public_key": wallet_address_list[0],'secret_key': wallet_address_list[1]},
                status_code=status.HTTP_201_CREATED
            )
        return wrap_response(
            success=False,
            code="wallet_address_already_exists",
            errors=[{"field": "wallet_address", "message": "Wallet address already exists."}],
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def get(self, request, *args, **kwargs):
        if request.user.wallet_address is not None:
            return wrap_response(
                success=True,
                code="wallet_address_retrieved",
                data={"public_key": request.user.wallet_address},
                status_code=status.HTTP_200_OK
            )
        return wrap_response(
            success=False,
            code="wallet_address_not_found",
            errors=[{"field": "wallet_address", "message": "Wallet address does not exist."}],
            status_code=status.HTTP_404_NOT_FOUND
        )
    

class ForgotPasswordView(CreateAPIView):
    serializer_class=ForgotPasswordSerializer
    permission_classes=[AllowAny]
    authentication_classes=[]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
        except User.DoesNotExist:
            return wrap_response(
                success=False,
                code="user_not_found",
                errors=[{"field": "email", "message": "User with this email does not exist."}],
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        reset_token = generate_token(user.user_id,True)
        res = send_forgot_password_email(
            user.email, reset_token
        )
        if not res:
            return wrap_response(
                success=False,
                code="failed_to_send_verification_email",
                errors=[{"field":"email","message": "Failed to send verification email."}],
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        user.reset_password_token= reset_token
        user.save()
        return wrap_response(
            success=True,
            code="reset_password_mail_sent",
            message="Reset password mail sent successfully.",
            status_code=status.HTTP_200_OK
        )
    
class ForgotPasswordMobileView(CreateAPIView):
    serializer_class=ForgotPasswordMobileSerializer
    permission_classes=[AllowAny]
    authentication_classes=[]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(mobile_number=serializer.validated_data['mobile_number'])
        except User.DoesNotExist:
            return wrap_response(
                success=False,
                code="user_not_found",
                errors=[{"field": "mobile_number", "message": "User with this mobile number does not exist."}],
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        reset_token = generate_token(user.user_id,True)
        res = send_forgot_password_sms(
            user.mobile_number, reset_token
        )
        if not res:
            return wrap_response(
                success=False,
                code="failed_to_send_verification_sms",
                errors=[{"field":"mobile_number","message": "Failed to send verification sms."}],
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        user.reset_password_token= reset_token
        user.save()
        return wrap_response(
            success=True,
            code="reset_password_sms_sent",
            message="Reset password sms sent successfully.",
            status_code=status.HTTP_200_OK
        )

class PasswordResetView(CreateAPIView):
    serializer_class=ResetPasswordSerializer
    permission_classes=[AllowAny]
    authentication_classes=[]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth_token = serializer.validated_data['token']
        user_id, error =unzip_token(auth_token,True)
        if user_id is None:
            if error=="invalid_token":
                message="Invalid token"
            else:
                message="Expired token. Please generate new reset password url."
            return wrap_response(
                success=False,
                code=error,
                errors=[{"field":"auth_token","message":message}],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return wrap_response(
                success=False,
                code="user_not_found",
                errors=[{"field":"auth_token","message": "User not found."}],
                status_code=status.HTTP_404_NOT_FOUND
            )
        if user.reset_password_token!=auth_token:
            return wrap_response(
                success=False,
                code="token_already_used",
                errors=[{"field":"auth_token","message": "This URl already used for resetting password."}],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(serializer.validated_data['password'])
        user.reset_password_token=None
        user.save()
        return wrap_response(
            success=True,
            code="password_reset_successful",
            message="Password reset successful.",
            status_code=status.HTTP_200_OK
        ) 

class UserModeView(APIView):
    permission_classes=[IsAuthenticated,IsVerified,IsRegistered,IsSubscribed]
    def get(self, request, *args, **kwargs):
        return wrap_response(
            success=True,
            code='user_mode_retrieved',
            data={"is_buyer":request.user.is_buyer},
            status_code=status.HTTP_200_OK
        )
    

class ChangeUserModeView(APIView):
    permission_classes=[IsAuthenticated,IsVerified,IsRegistered]
    def get(self, request, *args, **kwargs):
        if not request.user.is_buyer:
            if request.user.subscription_expiry_date is None or request.user.subscription_expiry_date < timezone.now():
                return wrap_response(
                    success=True,
                    code='permission_denied',
                    data={
                        "is_subscribed": False
                    },
                    status_code=status.HTTP_200_OK
                )
        request.user.is_buyer = not request.user.is_buyer
        request.user.save()
        return wrap_response(
            success=True,
            code='user_mode_changed',
            message="Successfully changed user mode.",
            data={"is_buyer":request.user.is_buyer},
            status_code=status.HTTP_200_OK
        )