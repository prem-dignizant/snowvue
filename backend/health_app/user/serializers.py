from rest_framework import serializers
from user.models import (
    User
)
from user.service import validate_and_format_number
import re
from django.core.validators import RegexValidator
from datetime import date
class UserSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    user_name = serializers.CharField(required=True,allow_null=False ,allow_blank=False)
    class Meta:
        model = User
        fields = ("user_id", "email", "password", "confirm_password", "user_name")
        extra_kwargs = {
            'confirm_password': {'write_only': True}
        }
    def validate_email(self, value):
        value = value.strip().lower()
        return value
    def validate_password(self, value):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{16,}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Password must contain at least 16 characters, including at least one uppercase letter, one lowercase letter, one number, and one special character (@, $, !, %, *, ?, &)."
            )
        return value
    def validate_confirm_password(self, value):
        
        password = self.initial_data.get("password")
        if password != value:
            raise serializers.ValidationError("password and confirm_password fields didn't match.")
        return value

class UserMobileSerializer(serializers.ModelSerializer):
    mobile_number=serializers.CharField(required=True,allow_null=False ,allow_blank=False)
    password = serializers.CharField(write_only=True, required=True,allow_null=False ,allow_blank=False)
    confirm_password = serializers.CharField(write_only=True, required=True)
    user_name = serializers.CharField(required=True,allow_null=False ,allow_blank=False)
    class Meta:
        model = User
        fields = ("user_id", "mobile_number", "password", "confirm_password", "user_name","country_code")
        extra_kwargs = {
            'confirm_password': {'write_only': True}
        }
    def validate_mobile_number(self, value):
        value = value.strip()
        return value
    def validate_password(self, value):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{16,}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Password must contain at least 16 characters, including at least one uppercase letter, one lowercase letter, one number, and one special character (@, $, !, %, *, ?, &)."
            )
        return value
    def validate_confirm_password(self, value):
        password = self.initial_data.get("password")
        if password != value:
            raise serializers.ValidationError("password and confirm_password fields didn't match.")
        return value
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    def validate_email(self, value):
        value = value.strip().lower()
        return value
    
class UserLoginMobileSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(required=True,allow_null=False ,allow_blank=False)
    password = serializers.CharField(required=True)
    def validate_mobile_number(self, value):
        value = value.strip()
        return value
class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    token = serializers.CharField(write_only=True, max_length=16)
    def validate_email(self, value):
        value = value.strip().lower()
        return value
    
class MobileVerificationSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(required=True,allow_null=False ,allow_blank=False)
    token = serializers.CharField(write_only=True, max_length=16)
    def validate_mobile_number(self, value):
        value = value.strip()
        return value


class ResendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        value = value.strip().lower()
        return value
    
class ResendMobileVerificationSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(required=True,allow_null=False ,allow_blank=False)

    def validate_mobile_number(self, value):
        value = value.strip()
        return value

class UserProfileSerializer(serializers.Serializer):
    dob = serializers.DateField(format='%Y-%m-%d', required=True, allow_null=True)
    middle_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    zipcode = serializers.IntegerField(required=False, allow_null=True)
    tribe = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    race = serializers.CharField(required=True)
    sex = serializers.CharField(required=True)
    what3words = serializers.CharField(required=True,
        validators=[
            RegexValidator(
                regex=r'^[a-z]+\.[a-z]+\.[a-z]+$',
                message="what3words must be in the format 'word.word.word' using only lowercase alphabetic characters."
            )
        ])
    national_id = serializers.CharField(required=True)
    ssn = serializers.CharField(required=False)
    def validate_ssn(self,value):
        if value and not re.match(r'^[0-9]{3}-[0-9]{2}-[0-9]{4}$', value):
            raise serializers.ValidationError('SSN must be in the format "XXX-XX-XXXX"')
        return value
    def validate_sex(self, value):
        value_set=('M','F','NA')
        if value not in value_set:
            raise serializers.ValidationError("sex must be one of 'M', 'F', 'NA'.")
        return value
    
    def validate_dob(self, value):
        if value is None:
            raise serializers.ValidationError("Date of birth cannot be null.")
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError("User must be at least 18 years old.")
        
        return value

    def validate_race(self, value):
        value_set=('Black','White','Asian','Mixed','Unknown')
        if value not in value_set:
            raise serializers.ValidationError("race must be one of 'Black', 'White', 'Asian', 'Mixed', 'Unknown'.")
        return value
    email = serializers.EmailField(source='user.email', read_only=True)
    def validate_national_id(self, value):
        sex = self.initial_data.get("sex", "").upper() 
        if sex == "F":
            pattern = r"^CF[A-Z0-9]{12}$"  
        elif sex == "M":
            pattern = r"^CM[A-Z0-9]{12}$" 
        elif sex == "NA":
            pattern = r"^[A-Z0-9]{14}$"
        else:
            raise serializers.ValidationError("sex must be specified as 'M' , 'F' or 'NA' for valid national_id validation.")
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "national_id must be 14 characters, start with 'CF' for females or 'CM' for males, "
                "contain only uppercase letters and numbers, and include both letters and numbers."
            )
        if not (re.search(r'[A-Z]', value) and re.search(r'[0-9]', value)):
            raise serializers.ValidationError("national_id must contain at least one letter and one number.")

        return value
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    

class TOTPVerifySerializer(serializers.Serializer):
    token = serializers.IntegerField(required=True)
    auth_token = serializers.CharField(required=True)
    def validate(self, data):
        token = data["token"]
        auth_token = data["auth_token"]
        return data
    
class TOTPRecoverySerializer(serializers.Serializer):
    recovery_code = serializers.CharField(required=True,allow_blank=False ,allow_null=False)
    auth_token = serializers.CharField(required=True,allow_blank=False ,allow_null=False)
    def validate(self, data):
        recovery_code = data["recovery_code"]
        auth_token = data["auth_token"]
        return data
class TOTPCreateSerializer(serializers.Serializer):
    auth_token = serializers.CharField(required=True)
    def validate(self, data):
        auth_token = data["auth_token"]
        return data

class EmailObtainViewSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    def validate_email(self, value):
        value = value.strip().lower()
        return value
    
class MobileObtainViewSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(required=True,allow_null=False ,allow_blank=False)
    def validate_mobile_number(self, value):
        value = value.strip()
        mobile_status,mobilenumber,country_code=validate_and_format_number(value)
        if not mobile_status:
            raise serializers.ValidationError("Invalid mobile number. Please enter correct mobile number")
        return value

class UserNameObtainViewSerializer(serializers.Serializer):
    user_name = serializers.CharField(required=True)
class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class UserRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)




class ForgotPasswordSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True)

class ForgotPasswordMobileSerializer(serializers.Serializer):
    mobile_number=serializers.CharField(required=True,allow_null=False ,allow_blank=False)

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True,allow_null=False,allow_blank=False)
    confirm_password = serializers.CharField(required=True,allow_null=False,allow_blank=False)
    token = serializers.CharField(required=True,allow_null=False,allow_blank=False)
    def validate_password(self, value):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{16,}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Password must contain at least 16 characters, including at least one uppercase letter, one lowercase letter, one number, and one special character (@, $, !, %, *, ?, &)."
            )
        return value
    def validate_confirm_password(self, value):
        
        password = self.initial_data.get("password")
        if password != value:
            raise serializers.ValidationError("password and confirm_password fields didn't match.")
        return value



