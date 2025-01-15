from rest_framework import serializers
from health.models import UserHealthProfile
import re
class UserHealthProfileSerializer(serializers.ModelSerializer):
    smoking_status=serializers.BooleanField(required=True)
    vaping_status=serializers.BooleanField(required=True)
    pregnant=serializers.BooleanField(required=True)
    malaria=serializers.BooleanField(required=True)
    covid=serializers.BooleanField(required=True)


    
    class Meta:
        model = UserHealthProfile
        fields = [
            'height', 'weight', 'weight_type', 'waist', 'waist_choices',
            'smoking_status', 'vaping_status', 'blood_pressure', 'a1c_level',
            'blood_sugar_level', 'pregnant', 'malaria', 'covid'
        ]
        read_only_fields = ['id', 'user'] 

    def validate_blood_pressure(self, value):
        pattern =  r'^\d{1,3}/\d{1,3}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Blood pressure's format is not valid(e.g., 120/80)."
            )
        systolic, diastolic = map(int, value.split('/'))

        if systolic > 129 or diastolic > 80:
            raise serializers.ValidationError(
                "Please talk to your doctor about your blood pressure."
            )

        return value
    
    def validate_a1c_level(self, value):
        if not isinstance(value, float):
            raise serializers.ValidationError("A1c must be a floating-point number (e.g., 0.0).")
        if round(value, 1) != value:
            raise serializers.ValidationError("A1c must have only 1 decimal point (e.g., 7.5).")
        if value >= 5.7:
            raise serializers.ValidationError("Please tell your doctor the value of your A1c level.")
        return value
    
    def validate_blood_sugar_level(self, value):
        if not isinstance(value, float):
            raise serializers.ValidationError("Blood sugar level must be a floating-point number (e.g., 0.0).")
        if value>99:
            raise serializers.ValidationError("Please tell your doctor the value of your blood sugar level.")
        return value
class ChangeHealthDataStatusSerializer(serializers.Serializer):
    is_height_selling=serializers.BooleanField(required=True)
    is_weight_selling=serializers.BooleanField(required=True)
    is_waist_selling=serializers.BooleanField(required=True)
    is_smoking_status_selling=serializers.BooleanField(required=True)
    is_vaping_status_selling=serializers.BooleanField(required=True)
    is_blood_pressure_selling=serializers.BooleanField(required=True)
    is_a1c_level_selling=serializers.BooleanField(required=True)
    is_blood_sugar_level_selling=serializers.BooleanField(required=True)
    is_pregnant_selling=serializers.BooleanField(required=True)
    is_malaria_selling=serializers.BooleanField(required=True)
    is_covid_selling=serializers.BooleanField(required=True)
    # secret_key=serializers.CharField(required=True,allow_blank=False,allow_null=False)
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     request = self.context.get('request')
    #     if request and request.method == 'GET':
    #         self.fields['secret_key'].required = False

class ContractRetrieveSerializer(serializers.Serializer):
    contract_id=serializers.IntegerField(required=True)



class DataPurchaseSerializer(serializers.Serializer):
    contract_id=serializers.IntegerField(required=True)
    secret_key=serializers.CharField(required=True,allow_blank=False,allow_null=False)
    data_points=serializers.ListField(required=True)


class ContractGetPriceSerializer(serializers.Serializer):
    contract_id=serializers.IntegerField(required=True)
    secret_key=serializers.CharField(required=True,allow_blank=False,allow_null=False)
    data_points=serializers.ListField(required=True)
