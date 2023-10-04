from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'api'

router = DefaultRouter()
router.register('get_cost', CostOfTaxi, basename='get_cost')

urlpatterns = [
    path('', include(router.urls)),
    path('get_cost/', CostOfTaxi.as_view(), name='get_cost'),
]