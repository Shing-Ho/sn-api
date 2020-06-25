from django.contrib import admin
from api.models.models import hotelmappingcodes


class HotelbedsAdmin(admin.ModelAdmin):
    list_per_page = 100


admin.site.register(hotelmappingcodes, HotelbedsAdmin)
