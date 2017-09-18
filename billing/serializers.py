from rest_framework import serializers
from . import models

class BillingInfo(serializers.ModelSerializer):
    class Meta:
        model = models.BillingInfo
        fields = '__all__'
class CPMPrice(serializers.ModelSerializer):
    class Meta:
        model = models.CPMPrice
        fields = '__all__'
class Bill(serializers.ModelSerializer):
    class Meta:
        model = models.Bill
        fields = '__all__'
class Payment(serializers.ModelSerializer):
    class Meta:
        model = models.Payment
        fields = '__all__'
