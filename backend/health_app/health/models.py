from django.db import models
from user.models import User,Base
from django.utils.timezone import datetime
# Create your models here.
class UserHealthProfile(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(default=datetime(2001, 1, 1, 0, 0, 0))
    weight_choices = (('kg','kg'),('lb','lb'))
    waist_choices = (('cm','cm'),('in','in'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="health_profile")
    height=models.FloatField()
    weight=models.FloatField()
    weight_type=models.CharField(max_length=2,choices=weight_choices)
    waist=models.FloatField()
    waist_choices=models.CharField(max_length=2,choices=waist_choices)
    smoking_status=models.BooleanField(default=False)
    vaping_status=models.BooleanField(default=False)
    blood_pressure=models.CharField(max_length=7,default='129/80')
    a1c_level=models.FloatField()
    blood_sugar_level=models.FloatField()
    pregnant=models.BooleanField(default=False)
    malaria=models.BooleanField(default=False)
    covid=models.BooleanField(default=False)
    is_height_selling=models.BooleanField(default=False)
    is_weight_selling=models.BooleanField(default=False)
    is_waist_selling=models.BooleanField(default=False)
    is_smoking_status_selling=models.BooleanField(default=False)
    is_vaping_status_selling=models.BooleanField(default=False)
    is_blood_pressure_selling=models.BooleanField(default=False)
    is_a1c_level_selling=models.BooleanField(default=False)
    is_blood_sugar_level_selling=models.BooleanField(default=False)
    is_pregnant_selling=models.BooleanField(default=False)
    is_malaria_selling=models.BooleanField(default=False)
    is_covid_selling=models.BooleanField(default=False)
    last_updated_time=models.DateTimeField(default=datetime(2001, 1, 1, 0, 0, 0))
    fhir_id=models.CharField(max_length=128,null=True,blank=True)

    def get_selling_fields(self):
        field_mapping = {
            'height': self.is_height_selling,
            'weight': self.is_weight_selling,
            'waist': self.is_waist_selling,
            'smoking_status': self.is_smoking_status_selling,
            'vaping_status': self.is_vaping_status_selling,
            'blood_pressure': self.is_blood_pressure_selling,
            'a1c_level': self.is_a1c_level_selling,
            'blood_sugar_level': self.is_blood_sugar_level_selling,
            'pregnant': self.is_pregnant_selling,
            'malaria': self.is_malaria_selling,
            'covid': self.is_covid_selling,
        }
        return [field for field, is_selling in field_mapping.items() if is_selling]

    def get_selling_data(self):
        """Return a dictionary of key-value pairs for fields available for selling."""
        selling_fields = self.get_selling_fields()
        selling_data = {field: getattr(self, field) for field in selling_fields}
        if 'weight' in selling_data:
            selling_data['weight_type'] = self.weight_type
        if 'waist' in selling_data:
            selling_data['waist_choices'] = self.waist_choices
        return selling_data
    def __str__(self):
        return f"{self.user.user_name}'s Health Profile"
    


class Contract(models.Model):
    created_at=models.DateTimeField(auto_now_add=True)
    contract_id=models.AutoField(primary_key=True)
    # contract_secret=models.CharField(max_length=64)
    data_points=models.TextField(null=True,blank=True)
    # price=models.FloatField(default=0)
    seller=models.ForeignKey(User,null=True,blank=True,related_name="contract_user",on_delete=models.CASCADE)
    expiry_time=models.DateTimeField(null=True,blank=True)
    data_file=models.CharField(max_length=250,null=True,blank=True)
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
