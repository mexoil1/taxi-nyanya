import requests
import json
from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .consts import Constants


class City(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    city_koeff = models.FloatField(default=1, verbose_name='Коэффицент города')
    latitude = models.FloatField(null=True, blank=True, verbose_name='Широта (заполнятеся автоматически)')
    longitude = models.FloatField(
        null=True, blank=True, verbose_name='Долгота (заполняется автоматически)')

    def save(self, *args, **kwargs):
        api_key = settings.GEO_KEY
        url = f'https://geocode-maps.yandex.ru/1.x?apikey={api_key}&geocode={self.title}&results=1&format=json&lang=ru_RU'
        req = requests.get(url)
        coordinates = json.loads(req.content)[
            'response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' ')
        self.latitude = coordinates[1]
        self.longitude = coordinates[0]
        super(City, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class Constant(models.Model):
    cost_of_km_by_time = models.FloatField(
        default=1, verbose_name='Стоимость километра в минуту')
    j = models.FloatField(default=1, verbose_name='J')
    econom = models.FloatField(
        default=1, verbose_name='Цена за километр эконом')
    comfort = models.FloatField(
        default=1, verbose_name='Цена за километр комфорт')
    business = models.FloatField(
        default=1, verbose_name='Цена за километр бизнес')
    miniven = models.FloatField(
        default=1, verbose_name='Цена за километр минивен')
    premium = models.FloatField(
        default=1, verbose_name='Цена за километр премиум')
    is_traffic = models.BooleanField(default=True, verbose_name='Учитывать ли пробки')
    radius = models.FloatField(default=3, verbose_name='Радиус поиска')

    def __str__(self):
        return 'Константы'

    class Meta:
        verbose_name = 'Константы'
        verbose_name_plural = 'Константы'


class Order(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    address_by = models.CharField(max_length=100)
    address_to = models.CharField(max_length=100)
    price_eco = models.FloatField()
    price_comf = models.FloatField()
    price_mini = models.FloatField()
    price_busi = models.FloatField()
    price_prem = models.FloatField()
    time = models.CharField(max_length=50)
    day = models.CharField(max_length=100)
    status = models.CharField(max_length=300)
    time_of_plan = models.CharField(max_length=200, null=True, blank=True)
    day_of_plan = models.CharField(max_length=200, null=True, blank=True)
    
    
class MinPriceOfTrip(models.Model):
    econom = models.IntegerField()
    comfort = models.IntegerField()
    business = models.IntegerField()
    miniven = models.IntegerField()
    premium = models.IntegerField()
    
    class Meta:
        verbose_name = 'Минимальные цены за поездку'
        verbose_name_plural = 'Минимальные цены за поездку'
        
    def __str__(self) -> str:
        return "Минимальные цены за поездку"
    
    
class PriceByChildren(models.Model):
    '''Зависимость цены от количества детей'''
    rate = models.CharField(max_length=200, choices=Constants.CHOICES_RATES, verbose_name='Тариф')
    children_count = models.IntegerField(default=0, verbose_name='Количество детей')
    price_koeff = models.FloatField(default=0, verbose_name='Коэффицент цены')
    
    class Meta:
        verbose_name = 'Коэфицент цены'
        verbose_name_plural = 'Коэфиценты цен в зависимости от количества детей'
    
    def __str__(self) -> str:
        return f'Коэффицент цены {self.rate} на {self.children_count} детей'
        
    
    
@receiver(pre_save, sender=Constant)
def update_min_price(sender, instance, **kwargs):
    if not instance._state.adding:  # Проверяем, что объект не создается
        try:
            old_constant = Constant.objects.get(pk=instance.pk)
            if instance.econom != old_constant.econom:
                # Вычисляем коэффициент пропорции между старым и новым значением econom
                coefficient_eco = instance.econom / old_constant.econom
                coefficient_comf = instance.comfort / old_constant.comfort
                coefficient_busi = instance.business / old_constant.business
                coefficient_mini = instance.miniven / old_constant.miniven
                coefficient_prem = instance.premium / old_constant.premium

                # Обновляем MinPriceOfTrip
                min_price = MinPriceOfTrip.objects.first()
                min_price.econom *= coefficient_eco
                min_price.comfort *= coefficient_comf
                min_price.business *= coefficient_busi
                min_price.miniven *= coefficient_mini
                min_price.premium *= coefficient_prem
                min_price.save()
        except Constant.DoesNotExist:
            pass

# Регистрируем сигнал
pre_save.connect(update_min_price, sender=Constant)
