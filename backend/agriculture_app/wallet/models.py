from django.db import models


class Wallet(models.Model):
    transaction_id = models.CharField(max_length=255, unique=True, blank=False,null=False,primary_key=True)
    from_account = models.CharField(max_length=255, blank=False, null=False)
    to_account = models.CharField(max_length=255, blank=False, null=False)
    amount=models.FloatField()
    fee=models.FloatField()
    created_at = models.DateTimeField()
    type = models.CharField(max_length=64, blank=True, null=True)
    memo= models.CharField(max_length=255, blank=True, null=True)