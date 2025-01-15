from rest_framework import serializers
from agriculture.models import AgricultureData

class AgricultureDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgricultureData
        fields = ('red_beans','maize','peas','coffee','milk','avocados','cassava','sweet_potatoes','irish_potatoes','pumpkins','rice','plantains','bananas','oranges')
        read_only_fields = ['id', 'user'] 
class ChangeAgricultureDataStatusSerializer(serializers.Serializer):
    is_red_beans_selling=serializers.BooleanField(required=True)
    is_maize_selling=serializers.BooleanField(required=True)
    is_peas_selling=serializers.BooleanField(required=True)
    is_coffee_selling=serializers.BooleanField(required=True)
    is_milk_selling=serializers.BooleanField(required=True)
    is_avocados_selling=serializers.BooleanField(required=True)
    is_cassava_selling=serializers.BooleanField(required=True)
    is_sweet_potatoes_selling=serializers.BooleanField(required=True)
    is_irish_potatoes_selling=serializers.BooleanField(required=True)
    is_pumpkins_selling=serializers.BooleanField(required=True)
    is_rice_selling=serializers.BooleanField(required=True)
    is_plantains_selling=serializers.BooleanField(required=True)
    is_bananas_selling=serializers.BooleanField(required=True)
    is_oranges_selling=serializers.BooleanField(required=True)


class ContractRetrieveSerializer(serializers.Serializer):
    contract_id=serializers.IntegerField(required=True)

class ContractGetPriceSerializer(serializers.Serializer):
    contract_id=serializers.IntegerField(required=True)
    secret_key=serializers.CharField(required=True,allow_blank=False,allow_null=False)
    data_points=serializers.ListField(required=True)

class DataPurchaseSerializer(serializers.Serializer):
    contract_id=serializers.IntegerField(required=True)
    secret_key=serializers.CharField(required=True,allow_blank=False,allow_null=False)
    data_points=serializers.ListField(required=True)
