from django.db import models, connection


class Geoname(models.Model):
    class Meta:
        app_label = "api"

    geoname_id = models.IntegerField(unique=True)
    iso_country_code = models.CharField(max_length=2)
    location_name = models.TextField()
    latitude = models.DecimalField(decimal_places=6, max_digits=9)
    longitude = models.DecimalField(decimal_places=6, max_digits=9)


class GeonameAlternateName(models.Model):
    class Meta:
        app_label = "api"

    alternate_name_id = models.IntegerField()
    iso_language_code = models.CharField(max_length=2)
    name = models.TextField()
    is_colloquial = models.BooleanField()
    iatacode = models.CharField(max_length=3)


    geoname = models.ForeignKey(
        Geoname, to_field="geoname_id", on_delete=models.CASCADE, null=True, related_name="lang"
    )
