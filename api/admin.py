from django.contrib import admin
from api.models.models import supplier_hotels, sn_hotel_map, PaymentTransaction


class HotelbedsAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display = ('country_name', 'provider_name',
                    'destination_name', 'address',)


class sn_hotel_mapAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display = ('simplenight_id', 'provider', 'provider_id',)


class pmt_transactionadmin(admin.ModelAdmin):
    list_per_page = 100


admin.site.register(PaymentTransaction, pmt_transactionadmin)
admin.site.register(supplier_hotels, HotelbedsAdmin)
admin.site.register(sn_hotel_map, sn_hotel_mapAdmin)
