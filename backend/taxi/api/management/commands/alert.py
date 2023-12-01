from datetime import datetime
import requests
import json
from django.conf import settings
from django.core.management.base import BaseCommand

from api.models import Order


class Command(BaseCommand):
    def handle(self, *args, **options):
        api_key = settings.GEO_KEY
        cur_year = datetime.now().year
        cur_month = datetime.now().month
        cur_day = datetime.now().day
        cur_date = f'{cur_year}-{cur_month}-{cur_day}'
        cur_hour = datetime.now().hour
        cur_minute = datetime.now().minute
        cur_time = f'{cur_hour}:{cur_minute}'
        print(api_key)
        print(cur_time)
        print(cur_date)
        no_completed_orders = Order.objects.filter(status="Created", day_of_plan=cur_date, time_of_plan=cur_time)
        for order in no_completed_orders:
            url_geo = f'https://geocode-maps.yandex.ru/1.x?apikey={api_key}&geocode={order.address_by}&results=1&format=json&lang=ru_RU'
            req = requests.get(url_geo)
            coordinates = json.loads(req.content)['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' ')
            latitude_by = coordinates[1]
            longitude_by = coordinates[0]
            print(coordinates)
            url_geo = f'https://geocode-maps.yandex.ru/1.x?apikey={api_key}&geocode={order.address_to}&results=1&format=json&lang=ru_RU'
            req = requests.get(url_geo)
            coordinates = json.loads(req.content)['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' ')
            latitude_to = coordinates[1]
            longitude_to = coordinates[0]
            print(coordinates)
            waypoints = f'{latitude_by},{longitude_by}|{latitude_to},{longitude_to}'
            url = f'https://api.routing.yandex.net/v2/route?apikey={api_key}&waypoints={waypoints}&mode=driving'
            resp = requests.get(url)
            print(json.loads(resp.content))
        