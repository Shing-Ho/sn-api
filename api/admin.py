from django.contrib import admin
from api.models.models import mappingcodes


class HotelbedsAdmin(admin.ModelAdmin):
    list_per_page = 100


admin.site.register(mappingcodes, HotelbedsAdmin)
