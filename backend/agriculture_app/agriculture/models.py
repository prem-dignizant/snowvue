from django.db import models
from user.models import Base,User
from django.utils.timezone import datetime

class AgricultureData(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(default=datetime(2001, 1, 1, 0, 0, 0))
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name="agriculture")
    red_beans=models.FloatField()
    maize=models.FloatField()
    peas=models.FloatField()
    coffee=models.FloatField()
    milk=models.FloatField()
    avocados=models.FloatField()
    cassava=models.FloatField()
    sweet_potatoes=models.FloatField()
    irish_potatoes=models.FloatField()
    pumpkins=models.FloatField()
    rice=models.FloatField()
    plantains=models.FloatField()
    bananas=models.FloatField()
    oranges=models.FloatField()
    is_red_beans_selling=models.BooleanField(default=False)
    is_maize_selling=models.BooleanField(default=False)
    is_peas_selling=models.BooleanField(default=False)
    is_coffee_selling=models.BooleanField(default=False)
    is_milk_selling=models.BooleanField(default=False)
    is_avocados_selling=models.BooleanField(default=False)
    is_cassava_selling=models.BooleanField(default=False)
    is_sweet_potatoes_selling=models.BooleanField(default=False)
    is_irish_potatoes_selling=models.BooleanField(default=False)
    is_pumpkins_selling=models.BooleanField(default=False)
    is_rice_selling=models.BooleanField(default=False)
    is_plantains_selling=models.BooleanField(default=False)
    is_bananas_selling=models.BooleanField(default=False)
    is_oranges_selling=models.BooleanField(default=False)
    last_updated_time=models.DateTimeField(default=datetime(2001, 1, 1, 0, 0, 0))
    def get_selling_fields(self):
        field_mapping = {
            'red_beans': self.is_red_beans_selling,
            'maize': self.is_maize_selling,
            'peas': self.is_peas_selling,
            'coffee': self.is_coffee_selling,
            'milk': self.is_milk_selling,
            'avocados': self.is_avocados_selling,
            'cassava': self.is_cassava_selling,
            'sweet_potatoes': self.is_sweet_potatoes_selling,
            'irish_potatoes': self.is_irish_potatoes_selling,
            'pumpkins': self.is_pumpkins_selling,
            'rice': self.is_rice_selling,
            'plantains': self.is_plantains_selling,
            'bananas': self.is_bananas_selling,
            'oranges': self.is_oranges_selling,
        }
        return [field for field, is_selling in field_mapping.items() if is_selling]
    def get_selling_data(self):
        """Return a dictionary of key-value pairs for fields available for selling."""
        selling_fields = self.get_selling_fields()    
        selling_data = {field: getattr(self, field) for field in selling_fields}
        return selling_data
    def __str__(self):
        return f"{self.user.user_name}'s data"

class Contract(models.Model):
    created_at=models.DateTimeField(auto_now_add=True)
    contract_id=models.AutoField(primary_key=True)
    # contract_secret=models.CharField(max_length=64)
    data_points=models.TextField(null=True,blank=True)
    # price=models.FloatField(default=0)
    seller=models.ForeignKey(User,null=True,blank=True,related_name="contract_user",on_delete=models.CASCADE)
    expiry_time=models.DateTimeField(null=True,blank=True)
    def __str__(self):
        return str(self.contract_id)
    

class ContractRecipient(models.Model):
    contract_recipient_id=models.AutoField(primary_key=True)
    created_at=models.DateTimeField(auto_now_add=True)
    contract=models.ForeignKey(Contract,null=True,blank=True,related_name="contract_recipient",on_delete=models.CASCADE)
    contract_secret=models.CharField(max_length=64,null=True,blank=True)
    data_points=models.TextField(null=True,blank=True)
    price=models.FloatField(default=0)
    buyer=models.ForeignKey(User,null=True,blank=True,related_name="contract_recipient_user",on_delete=models.CASCADE)
    is_purchased=models.BooleanField(default=False)
    def __str__(self):
        return str(self.contract_recipient_id)
