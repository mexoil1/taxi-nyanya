from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'api'

router = DefaultRouter()
router.register('get_cost', CostOfTaxi, basename='get_cost')
router.register('get_cities', GetAvailableCities, basename='get_cities')
router.register('send_tg_mes', SendMessageToTg, basename='send_tg_mes')

urlpatterns = [
    path('', include(router.urls)),
    path('get_cost/', CostOfTaxi.as_view(), name='get_cost'),
    path('send_tg_mes/', SendMessageToTg.as_view(), name='send_tg_mes'),
    path('get_data_of_trip/', GetDataOfTrip.as_view(), name='get_data_of_trip'),
    path('get_traffic_jams/', GetTrafficJams.as_view(), name='get_traffic_jams'),
    path('get_min_prices/', GetMinPrices.as_view(), name='get_min_prices'),
]
