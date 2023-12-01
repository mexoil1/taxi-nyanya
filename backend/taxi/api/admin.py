from django.contrib import admin

from .models import City, Constant, MinPriceOfTrip, PriceByChildren

admin.site.register(City)
admin.site.register(Constant)
admin.site.register(MinPriceOfTrip)
admin.site.register(PriceByChildren)
