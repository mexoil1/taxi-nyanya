import requests
import json
import time
from typing import List, Dict
from rest_framework import status
from rest_framework.views import APIView
from django.conf import settings
from django.db.models.query import QuerySet
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from datetime import datetime

from .serializers import CostSerializer, CitySerializer, TgMessageSerializer,\
    GetDataOfTripSerializer
from .models import Constant, City, Order, MinPriceOfTrip, PriceByChildren
from .utils import send_tg_message


@extend_schema(
    description='Рассчет цены',
    request=CostSerializer,
)
class CostOfTaxi(APIView):

    def post(self, request):
        data = request.data
        rates = ['econom', 'comfort', 'business', 'miniven', 'premium']
        rates_db = ['eco', 'comf', 'busi', 'mini', 'prem']
        data['time'] = data['time'] / 60
        data['distance'] = data['distance'] / 1000
        constants = Constant.objects.values().first()
        try:
            city_model = City.objects.only(
                'city_koeff').get(title=data['city'])
        except:
            return Response({"exception": "Убедитесь в правильности введеных данных"}, status=status.HTTP_400_BAD_REQUEST)
        city_koeff = city_model.city_koeff
        time_of_order = datetime.now().hour
        if data['is_planned']:
            time_of_order = request.data.get('time_of_plan')
            orders = Order.objects.filter(city=city_model,
                                          address_by=data['address_by'],
                                          address_to=data['address_to'],
                                          time=data['time_of_order'],
                                          day=data['day_of_plan']
                                          ).only('price_eco',
                                                 'price_comf',
                                                 'price_busi',
                                                 'price_mini',
                                                 'price_prem')
            if orders.count() > 2:
                result = self.check_price_by_database(orders, rates, rates_db)
            else:
                return Response({"message": "Please write me at planned time"}, status=status.HTTP_306_RESERVED)
        else:
            result = self.calculate(constants, data, city_koeff, rates)
        result = self.get_price_by_children_count(result, data['children_count'])
        day = datetime.now().weekday()
        if data['is_planned']:
            Order.objects.create(city=city_model,
                                 address_by=data['address_by'],
                                 address_to=data['address_to'],
                                 price_eco=result['econom'],
                                 price_comf=result['comfort'],
                                 price_mini=result['miniven'],
                                 price_busi=result['business'],
                                 price_prem=result['premium'],
                                 time=time_of_order,
                                 day=day,
                                 status='Created',
                                 time_of_plan=data['time_of_planned'],
                                 day_of_plan=data['day_of_planned'])
        else:
            Order.objects.create(city=city_model,
                                 address_by=data['address_by'],
                                 address_to=data['address_to'],
                                 price_eco=result['econom'],
                                 price_comf=result['comfort'],
                                 price_mini=result['miniven'],
                                 price_busi=result['business'],
                                 price_prem=result['premium'],
                                 time=time_of_order,
                                 day=day,
                                 status='Completed')
        # send_tg_message(
        #    f'''🔥Новый заказ🔥\nГород: {city}\nНачальная точка: {address_by}\nКонечная точка: {address_to}\nЦены:\n- Эконом: {int(result_eco)}\n- Комфорт: {int(result_comf)}\n- Бизнес: {int(result_busi)}\n- Минивен: {int(result_mini)}\n- Премиум: {int(result_prem)}''')
        return Response(result, status=status.HTTP_200_OK)

    def calculate(self, constants: Dict[str, float], data: dict, city_koeff: float, rates: List[str]) -> Dict[str, int]:
        """Вычисление стоимости"""
        result = {}
        time_cost_divisor = constants['cost_of_km_by_time'] * \
            (data['distance'] + constants['radius'])
        for item in rates:
            base_result = data['time'] / time_cost_divisor * \
                constants[f'{item}'] * (city_koeff / constants['j'])
            result[f'{item}'] = int(
                base_result * 65 / 100) if data["with_friend"] else int(base_result)
        return result

    def check_price_by_database(self, orders: QuerySet[Order], rates: List[str], rates_db: List[str]) -> Dict[str, int]:
        """Собираем средние данные из истории заказов"""
        result: Dict[str, int] = {item: 0 for item in rates}
        n: int = 0
        orders_len: int = orders.count()
        for i, order in enumerate(orders):
            if orders_len <= 10 or i >= orders_len - 10:
                for item, item_db in zip(rates, rates_db):
                    result[f'{item}'] += getattr(order, item_db)
                    n += 1
        for item in rates:
            result[item] = int(result[f'{item}'] / n)
        return result
    
    def get_price_by_children_count(self, prices: dict, children_count: int) -> dict:
        result = {}
        for item in prices:
            if item == 'miniven':
                koeff = PriceByChildren.objects.filter(rate='miniven', children_count=children_count).first().price_koeff
            else:
                if children_count < 4:
                    koeff = PriceByChildren.objects.filter(rate='not miniven', children_count=children_count).first().price_koeff
                else:
                    koeff = 0
            result[item] = prices[item] * koeff
        return result
        

    @staticmethod
    def get_extra_actions():
        return []


class GetAvailableCities(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Получение доступных городов."""
    queryset = City.objects.only("title", "latitude", "longitude").all()
    serializer_class = CitySerializer
    


@extend_schema(
    description='Отправка сообщения о заказе в телеграм',
    request=TgMessageSerializer,
)
class SendMessageToTg(APIView):

    def post(self, request):
        data = request.data
        send_tg_message(
            f'''🔥Новый заказ🔥\nИмя клиента: {data["name"]}\nНомер телефона клиента: {data["phone_number"]}\nГород: {data["city"]}\nНачальная точка: {data["address_by"]}\nКонечная точка: {data["address_to"]}\nВыбранный тариф: {data["rate"]}\nЦена: {data["price"]} руб.''')
        return Response({"message": "success"}, status=status.HTTP_200_OK)

    @staticmethod
    def get_extra_actions():
        return []


@extend_schema(
    description='Отложенный заказ',
    request=GetDataOfTripSerializer,
)
class GetDataOfTrip(APIView):

    def post(self, request):
        api_key = settings.GEO_KEY
        address_by = request.data.get('address_by')
        address_to = request.data.get('address_to')
        with_friend = request.data.get('with_friend')
        time_of_plan = request.data.get('time_of_plan')
        day_of_plan = request.data.get('day_of_plan')
        while True:
            current_hour = datetime.now().hour
            current_minute = datetime.now().minute
            cur_day = datetime.now().date
            if f'{current_hour}:{current_minute}' == time_of_plan and cur_day == day_of_plan:
                break
            time.sleep(60)
        if with_friend:
            address_by_friend = request.data.get('address_by_friend')
            address_to_friend = request.data.get('address_to_friend')
        else:
            url_geo = f'https://geocode-maps.yandex.ru/1.x?apikey={api_key}&geocode={address_by}&results=1&format=json&lang=ru_RU'
            req = requests.get(url_geo)
            coordinates = json.loads(req.content)[
                'response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' ')
            latitude_by = coordinates[1]
            longitude_by = coordinates[0]
            url_geo = f'https://geocode-maps.yandex.ru/1.x?apikey={api_key}&geocode={address_to}&results=1&format=json&lang=ru_RU'
            req = requests.get(url_geo)
            coordinates = json.loads(req.content)[
                'response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' ')
            latitude_to = coordinates[1]
            longitude_to = coordinates[0]
            waypoints = f'{latitude_by},{longitude_by}|{latitude_to},{longitude_to}'
            url = f'https://api.routing.yandex.net/v2/route?api_key={api_key}&waypoints={waypoints}&mode=driving'
            resp = requests.get(url)
            print(json.loads(resp.content))
        return Response({"message": "success"}, status=status.HTTP_200_OK)

    @staticmethod
    def get_extra_actions():
        return []



class GetTrafficJams(APIView):
    
    def get(self, request):  
        traffic = Constant.objects.values('is_traffic').first()['is_traffic']
        return Response({"is_traffic": traffic}, status=status.HTTP_200_OK)


class GetMinPrices(APIView):

    def get(self, request):
        min_prices = MinPriceOfTrip.objects.first()
        data = {}
        for item in ["econom", "comfort", "business", "miniven", "premium"]:
            data[f'min_price_{item}'] = getattr(min_prices, item)
        return Response(data,
                        status=status.HTTP_200_OK)
