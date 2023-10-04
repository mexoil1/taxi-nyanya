from django.db import models

class City(models.Model):
    title = models.CharField(max_length=200)
    city_koeff = models.FloatField(default=1)
    
class Constants(models.Model):
    cost_of_km_by_time = models.FloatField(default=1)
    cost_of_km_by_dist = models.FloatField(default=1)
    j = models.FloatField(default=1)
