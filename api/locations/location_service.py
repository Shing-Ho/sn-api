from typing import List, Optional

from api.locations.models import LocationResponse
from api.models.models import Geoname


def find_by_prefix(prefix: str, language_code="en", limit=10) -> List[LocationResponse]:
    if prefix is None:
        return []

    language_code = language_code.lower()
    matching_cities = Geoname.objects.filter(lang__name__startswith=prefix, lang__iso_language_code=language_code)
    matching_cities = matching_cities.order_by("-population")
    matching_cities = matching_cities.distinct()
    matching_cities.prefetch_related("lang")

    return list(_geoname_to_location_response(city, language_code) for city in matching_cities[:limit])


def find_by_id(geoname_id: int, language_code="en") -> Optional[LocationResponse]:
    matching_locations = Geoname.objects.filter(geoname_id=geoname_id, lang__iso_language_code=language_code)
    if not matching_locations:
        return None

    return _geoname_to_location_response(matching_locations.first(), language_code)


def find_all(country_code=None, language_code="en") -> List[LocationResponse]:
    locations = Geoname.objects.filter(lang__iso_language_code=language_code)
    if country_code:
        locations = locations.filter(iso_country_code=country_code)

    return list(_geoname_to_location_response(location, language_code) for location in locations)


def _geoname_to_location_response(geoname: Geoname, language_code: str):
    localization = geoname.lang.filter(iso_language_code=language_code).first()
    if not localization:
        localization = geoname.lang.filter(iso_language_code="en").first()

    if localization:
        displayed_language_code = localization.iso_language_code
        displayed_location_name = localization.name
    else:
        displayed_language_code = "en"
        displayed_location_name = geoname.location_name

    return LocationResponse(
        location_id=geoname.geoname_id,
        language_code=displayed_language_code,
        location_name=displayed_location_name,
        province_code=geoname.province_code,
        iso_country_code=geoname.iso_country_code,
        latitude=geoname.latitude,
        longitude=geoname.longitude
    )
