from django.contrib import admin
from api.models.models import hotelmappingcodes, sn_hotel_map


class HotelbedsAdmin(admin.ModelAdmin):
    list_per_page = 100


class sn_hotel_mapAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display = ('simplenight_id', 'provider', 'provider_id',)


admin.site.register(hotelmappingcodes, HotelbedsAdmin)
admin.site.register(sn_hotel_map, sn_hotel_mapAdmin)
