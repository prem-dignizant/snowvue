from uuid import uuid4

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
import random, string
from .manager import UserManager


class Base(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class User(AbstractBaseUser, PermissionsMixin, Base):
    user_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False, unique=True
    )
    email = models.EmailField(db_index=True, max_length=100, unique=True,null=True,blank=True)
    mobile_number=models.CharField(max_length=24,null=True,blank=True,unique=True)
    country_code=models.CharField(max_length=8,null=True,blank=True)
    user_name=models.CharField(max_length=128,unique=True,null=False,blank=False)
    recovery_code=models.CharField(max_length=25, unique=True,null=False,blank=False)
    mfa_enabled = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_mobile_verified = models.BooleanField(default=False)
    is_registered_with_email=models.BooleanField(default=True)
    is_confirm_tnc=models.BooleanField(default=False)
    wallet_address=models.CharField(max_length=64,null=True,blank=True)
    reset_password_token = models.CharField(max_length=255, null=True, blank=True)
    is_buyer=models.BooleanField(default=False)
    stripe_id=models.CharField(max_length=32,null=True,blank=True)
    subscription_expiry_date=models.DateTimeField(null=True,blank=True)
    USERNAME_FIELD = "user_name"
    REQUIRED_FIELDS = []
    objects = UserManager()
    def save(self, *args, **kwargs):
        if not self.recovery_code:
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=25))
                if not User.objects.filter(recovery_code=code).exists():
                    self.recovery_code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user_name or ""


class EmailVerificationToken(Base):
    email_verification_token_id = models.AutoField(primary_key=True)
    token = models.CharField(max_length=16)
    expiry_date = models.DateTimeField()
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="email_verification_token"
    )

    def __str__(self):
        return str(self.user.email)
    
class MobileVerificationToken(Base):
    mobile_verification_token_id = models.AutoField(primary_key=True)
    token = models.CharField(max_length=16)
    expiry_date = models.DateTimeField()
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="mobile_verification_token"
    )

    def __str__(self):
        return str(self.user.mobile_number)


class UserProfile(Base):
    first_name = models.CharField(null=True, blank=True, max_length=128)
    middle_name=models.CharField(null=True,blank=True,max_length=128)
    last_name = models.CharField(null=True, blank=True, max_length=128)
    address=models.TextField(null=True,blank=True)
    dob=models.DateField(null=True,blank=True)
    race=models.CharField(null=True,blank=True,max_length=128)
    sex=models.CharField(null=True,blank=True,max_length=16)
    what3words=models.CharField(null=True,blank=True,max_length=128)
    zipcode=models.IntegerField(null=True,blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    national_id=models.CharField(max_length=16,null=True,blank=True)
    tribe=models.CharField(null=True,blank=True,max_length=128)
    ssn = models.CharField(max_length=16,null=True,blank=True)
    def __str__(self):
        return f"{self.user.user_name}'s Profile"
    

