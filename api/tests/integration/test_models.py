from api.models.models import Geoname, GeonameAlternateName


def create_geoname_model(geoname_id, location_name, province_code, country_code, population=0):
    geoname = Geoname(
        geoname_id=geoname_id,
        location_name=location_name,
        province_code=province_code,
        iso_country_code=country_code,
        latitude=50.0,
        longitude=50.0,
        population=population,
        timezone="US/Pacific"
    )

    geoname.save()
    return geoname


def create_altname_model(pk_id, geoname, lang_code, name):
    alternate_name = GeonameAlternateName(
        alternate_name_id=pk_id,
        geoname=geoname,
        geoname_id=geoname.geoname_id,
        iso_language_code=lang_code,
        name=name,
        is_colloquial=False,
    )

    alternate_name.save()
    return alternate_name
