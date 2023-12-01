from rest_framework import serializers

from .models import City


class CostSerializer(serializers.Serializer):
    time = serializers.FloatField()
    distance = serializers.FloatField()
    city = serializers.CharField(max_length=200)
    address_to = serializers.CharField(max_length=1000)
    address_by = serializers.CharField(max_length=1000)
    children_count = serializers.IntegerField()
    with_friend = serializers.BooleanField(default=False)
    is_planned = serializers.BooleanField(default=False)
    time_of_plan = serializers.CharField(max_length=20)
    day_of_plan = serializers.CharField(max_length=100)
    time_of_planned = serializers.CharField(max_length=1000)
    day_of_planned = serializers.CharField(max_length=1000)


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ('id', 'title', 'latitude', 'longitude')


class TgMessageSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    phone_number = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=200)
    address_by = serializers.CharField(max_length=1000)
    address_to = serializers.CharField(max_length=1000)
    rate = serializers.CharField(max_length=100)
    price = serializers.IntegerField()


class GetDataOfTripSerializer(serializers.Serializer):
    address_by = serializers.CharField(max_length=1000)
    address_to = serializers.CharField(max_length=1000)
    with_friend = serializers.BooleanField(default=False)
    address_by_friend = serializers.CharField(max_length=1000)
    address_to_friend = serializers.CharField(max_length=1000)
    time_of_plan = serializers.CharField(max_length=1000)
    day_of_plan = serializers.CharField(max_length=1000)
    time_of_planned = serializers.CharField(max_length=1000)
    day_of_planned = serializers.CharField(max_length=1000)
