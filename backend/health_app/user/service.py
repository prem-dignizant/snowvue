from django.core.mail import EmailMessage
from django.conf import settings
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.conf import settings
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
import uuid, jwt,httpx,random,os
from django.core.cache import cache
from user.models import UserProfile
from stellar_sdk import Keypair, Server
key=b'njVD0FDf5dqAJ7YREQRNVXRUQ39XmK29uIqz357Jj0s='
fernet=Fernet(key)
from django.utils import timezone as django_timezone
from datetime import datetime
import requests,phonenumbers
from vonage import Auth, Vonage
from vonage_sms import SmsMessage, SmsResponse
def generate_token(user_id,forgot=False):
    if forgot:
        token =  str(random.randint(10000,99999)) + '--' +  str(django_timezone.now()+django_timezone.timedelta(minutes=5))  + '--' + str(user_id)+ '--' + "forgot"
    else:
        token =  str(random.randint(10000,99999)) + '--' +  str(django_timezone.now()+django_timezone.timedelta(minutes=5))  + '--' + str(user_id)    
    encrypted_token = fernet.encrypt(token.encode()).decode()
    return encrypted_token
def unzip_token(token,forgot=False):
    try:
        decrypted_token = fernet.decrypt(token.encode()).decode()
        parts = decrypted_token.split("--")
        expiry_time_str = parts[1]
        expiry_time = datetime.fromisoformat(expiry_time_str)

        if django_timezone.now() > expiry_time:
            return None, "expired_token"
        if forgot:
            if parts[-1]!= "forgot":
                return None, "invalid_token"
            user_id=parts[-2]
        else:
            user_id = parts[-1]
        return user_id, None
    except Exception as e:
        return None, "invalid_token"
def delete_exist_token(token,user):
    try:
        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for token in outstanding_tokens:
            if not BlacklistedToken.objects.filter(token=token).exists():
                BlacklistedToken.objects.create(token=token)
    except Exception as e:
        pass



def send_verification_email(email, token):
    try:
        subject = 'Please Verify Your Email Address'
        html_content=f"<strong>Verification Code: {token}</strong>"
        email = EmailMessage(subject, html_content, settings.DEFAULT_FROM_EMAIL, [email])
        email.content_subtype = 'html'

        res=email.send()
        return res
    except:
        return None
    

def send_verification_sms(mobile_number, token):
    try:
        parsed_number=phonenumbers.parse(mobile_number)
        mobile_num=str(parsed_number.country_code)+str(parsed_number.national_number)
        client = Vonage(Auth(api_key='f50e8d46', api_secret='M5qiV5OH91V0SMVF'))
        message = SmsMessage(
            to=mobile_num,
            from_='Snowvue',
            text=f"Verification Code: {token}.",
        )
        response: SmsResponse = client.sms.send(message)
        if response.messages[0].status=='0':
            return True
        return False
    except:
        return False

def send_forgot_password_email(email, token):
    try:
        subject = 'Reset Your Password'
        html_content = f"""
        <p>You're receiving this email because you requested a password reset for your user account at Snowvue.</p>
        <p>Please go to the following page and choose a new password: <a href="{settings.FRONTEND_HEALTH_URL}/auth?token={token}&type=reset-password&value={email}&via=email">Click_me</a></p>
        <p>Your username, in case you’ve forgotten: {email}</p>
        <p>Thanks for using our site!</p>
        <p>The Snowvue team</p>
        """
        email = EmailMessage(subject, html_content, settings.DEFAULT_FROM_EMAIL, [email])
        email.content_subtype = 'html'
        res=email.send()
        return res
    except:
        return None

def send_forgot_password_sms(mobile_number, token):
    try:
        parsed_number=phonenumbers.parse(mobile_number)
        mobile_num=str(parsed_number.country_code)+str(parsed_number.national_number)
        client = Vonage(Auth(api_key='f50e8d46', api_secret='M5qiV5OH91V0SMVF'))
        message = SmsMessage(
            to=mobile_num,
            from_='Snowvue',
            text=f"forget password url : {settings.FRONTEND_HEALTH_URL}/auth?token={token}&type=reset-password&value=+{mobile_num}&via=mobile",
        )
        response: SmsResponse = client.sms.send(message)
        if response.messages[0].status=='0':
            return True
        return False
    except:
        return False

def get_user_totp_device(self, user, confirmed=None):
    devices = devices_for_user(user, confirmed=confirmed)
    for device in devices:
        if isinstance(device, TOTPDevice):
            return device
        
def fhir_authorization():
    print('acces token coming from api call')
    url = f"{settings.FHIR_URL}connect/token"
    payload = {
        'client_id': settings.FHIR_CLIENT_ID,
        'client_secret': settings.FHIR_CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'scope': 'meldrx-api patient/*.* cds'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response=httpx.post(url, data=payload,headers=headers)
    if response.status_code == 200:
        response=response.json()
        if 'access_token' in response:
            cache.set('ACCESS_TOKEN',response['access_token'],60*5)
            return response['access_token']
    return None


def register_with_fhir(user:UserProfile):
    access_token=cache.get('ACCESS_TOKEN')
    if access_token is None:
        access_token=fhir_authorization()
    if access_token is not None:
        data={}
        data["resourceType"]= "Patient"
        if user.middle_name is not None:
            data["name"]=[
                            {
                            "use": "official",
                            "family": user.last_name,
                            "given": [user.first_name,user.middle_name]
                            }
                        ]
        else:
            data["name"]=[
                            {
                            "use": "official",
                            "family": user.last_name,
                            "given": [user.first_name]
                            }
                        ]
        if user.sex=="M":
            data["gender"]='male'
        elif user.sex=="F":
            data["gender"]='female'
        else:
            data["gender"]='unknown'
        data["birthDate"]=str(user.dob)
        data["address"]=[
                            {
                            "use": "home",
                            "text": user.address
                            }
                        ]
        data["identifier"]=[
            {
            "use": "usual",
            "system": "http://localhost:8000",
            "value": str(user.user.user_id)
            }]
        print(data)
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        res=httpx.post(f'{settings.FHIR_URL}api/fhir/{settings.FHIR_WORKSPACE_ID}/Patient',json=data,headers=headers)
        print(res)
    return None

# user=UserProfile.objects.select_related('user').get(user__email='harmil.tl@yopmail.com')
# register_with_fhir(user)

server = Server("https://horizon-testnet.stellar.org")
def create_wallet():
    try:
        keypair = Keypair.random()
        public_key = keypair.public_key
        secret_key = keypair.secret

        return [public_key,secret_key]
    except Exception as error:
        return None
    

def fund_wallet(public_key:str):

    if  public_key is None:
        return None
    try:
        friendbot_url = f"https://friendbot.stellar.org?addr={public_key}"
        response = requests.get(friendbot_url)

        if response.ok:
            return True
        else:
            return None
    except Exception as error:
        return None
    

def validate_and_format_number(raw_number:str):
    try:
        parsed = phonenumbers.parse(raw_number, None)
        if phonenumbers.is_valid_number(parsed):
            return True, phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),'+'+str(parsed.country_code)
        else:
            return False, "invalid_phone_number","Pleese enter a valid phone number."
    except Exception as e:
        return False, "invalid_phone_number","Pleese enter a valid phone number."