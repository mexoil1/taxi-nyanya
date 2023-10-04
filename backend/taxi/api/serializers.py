from rest_framework import serializers

class CostSerializer(serializers.Serializer):
    time = serializers.FloatField()
    distance = serializers.FloatField()
    city = serializers.CharField(max_length=200)