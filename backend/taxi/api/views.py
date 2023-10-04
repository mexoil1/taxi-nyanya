from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import CostSerializer
from .models import Constants, City

@extend_schema(
    description='Рассчет цены',
    request=CostSerializer,
)
class CostOfTaxi(APIView):
    
    def post(self, request):
        time = request.data.get('time')
        distance = request.data.get('distance')
        city = request.data.get('city')
        constants = Constants.objects.first()
        cost_of_km_by_time = constants.cost_of_km_by_time
        cost_of_km_by_dist = constants.cost_of_km_by_dist
        city_koeff = City.objects.get(title=city).city_koeff
        j = constants.j
        result = time/cost_of_km_by_time*distance*cost_of_km_by_dist*city_koeff/j
        data = {'cost': result} 
        return Response(data, status=200)
    
    @staticmethod
    def get_extra_actions():
        return []
