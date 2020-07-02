from django.contrib import admin
from api.models.models import supplier_hotels, sn_hotel_map


class HotelbedsAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display = ('country_name', 'provider_name',)


class sn_hotel_mapAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display = ('simplenight_id', 'provider', 'provider_id',)


admin.site.register(supplier_hotels, HotelbedsAdmin)
admin.site.register(sn_hotel_map, sn_hotel_mapAdmin)
