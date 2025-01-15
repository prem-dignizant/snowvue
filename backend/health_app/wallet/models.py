from django.db import models
from user.models import User

# class Wallet(models.Model):
#     transaction_id = models.CharField(max_length=255, unique=True, blank=False,null=False,primary_key=True)
#     from_account = models.CharField(max_length=255, blank=False, null=False)
#     to_account = models.CharField(max_length=255, blank=False, null=False)
#     amount=models.FloatField()
#     fee=models.FloatField()
#     created_at = models.DateTimeField()
#     type = models.CharField(max_length=64, blank=True, null=True)
#     memo= models.CharField(max_length=255, blank=True, null=True)



class Subscription(models.Model):
    subscription_id = models.AutoField(blank=False,null=False,primary_key=True)
    user=models.ForeignKey(User,related_name="stripe_subscription",null=True,blank=True,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    first_name=models.CharField(max_length=128,null=False,blank=False)
    last_name=models.CharField(max_length=128,null=False,blank=False)
    organization_name=models.CharField(max_length=128,null=False,blank=False)
    position=models.CharField(max_length=128,null=False,blank=False)
    address=models.TextField(null=False,blank=False)
    organization_type=models.CharField(max_length=128,null=False,blank=False)
    stripe_subscription_id=models.CharField(max_length=128,null=False,blank=False)


