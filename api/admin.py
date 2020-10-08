from django.contrib import admin
from api.models.models import PaymentTransaction


class PaymentTransactionAdmin(admin.ModelAdmin):
    list_per_page = 100


admin.site.register(PaymentTransaction, PaymentTransactionAdmin)
