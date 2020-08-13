from typing import List, Optional

from api.locations.models import LocationResponse
from api.models.models import Geoname, GeonameAlternateName


def find_by_prefix(prefix: str, language_code="en", limit=10) -> List[LocationResponse]:
    if prefix is None:
        return []

    lang_code = language_code.lower()
    matching_cities = Geoname.objects.filter(lang__name__startswith=prefix, lang__iso_language_code=lang_code)
    matching_cities.order_by("population")
    matching_cities.distinct()
    matching_cities.prefetch_related("lang")

    locations = []
    for city in matching_cities[:limit]:
        localization = GeonameAlternateName.objects.filter(
            name__startswith=prefix, iso_language_code=language_code, geoname_id=city.geoname_id,
        )
        locations.append(_geoname_to_location_response(city, localization.first()))

    return locations


def find_by_id(geoname_id: int, language_code="en") -> Optional[LocationResponse]:
    matching_locations = Geoname.objects.filter(geoname_id=geoname_id, lang__iso_language_code=language_code)
    localization = GeonameAlternateName.objects.filter(iso_language_code=language_code, geoname_id=geoname_id)

    if not matching_locations:
        return None

    return _geoname_to_location_response(matching_locations.first(), localization.first())


def _geoname_to_location_response(geoname: Geoname, localization: GeonameAlternateName):
    return LocationResponse(
        location_id=geoname.geoname_id,
        language_code=localization.iso_language_code,
        location_name=localization.name,
        province_code=geoname.province_code,
        iso_country_code=geoname.iso_country_code,
    )
