from rest_framework import serializers
from . import models

class BillboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Billboard
        fields = '__all__'
class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Photo
        fields = '__all__'
class BillboardMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BillboardMedia
        fields = '__all__'
