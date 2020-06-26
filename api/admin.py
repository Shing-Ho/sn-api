from django.contrib import admin
<<<<<<< HEAD
from api.models.models import hotelmappingcodes, sn_hotel_map
=======
from api.models.models import hotelmappingcodes
>>>>>>> d980c5612b59558f4cd02be12d62991a9ad024ef


class HotelbedsAdmin(admin.ModelAdmin):
    list_per_page = 100


<<<<<<< HEAD
class sn_hotel_mapAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display = ('simplenight_id', 'provider', 'provider_id',)


admin.site.register(hotelmappingcodes, HotelbedsAdmin)
admin.site.register(sn_hotel_map, sn_hotel_mapAdmin)
=======
admin.site.register(hotelmappingcodes, HotelbedsAdmin)
>>>>>>> d980c5612b59558f4cd02be12d62991a9ad024ef
