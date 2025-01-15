from rest_framework import serializers


class FundTransferSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True)
    to_public_key= serializers.CharField(required=True,allow_blank=False,allow_null=False)
    from_private_key= serializers.CharField(required=True,allow_blank=False,allow_null=False)