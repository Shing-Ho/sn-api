from django import forms
from django.contrib import admin
from django.forms import TextInput

from api.models.models import Booking, OrganizationFeatures


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_per_page = 100


@admin.register(OrganizationFeatures)
class OrganizationFeatureInline(admin.ModelAdmin):
    class Form(forms.ModelForm):
        class Meta:
            model = OrganizationFeatures
            fields = "__all__"
            widgets = {
                "value": TextInput(attrs={"size": 60}),
            }

    form = Form
    list_display = ("organization_name", "name", "value")
    list_filter = ("organization__name",)
    widgets = {
        "value": TextInput(attrs={"size": 20}),
    }
