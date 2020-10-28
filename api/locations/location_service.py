from decimal import Decimal
from typing import List, Optional

from api import logger
from api.locations import airports
from api.locations.models import LocationResponse, LocationType
from api.models.models import Geoname, Airport, CityMap


def find_by_prefix(prefix: str, language_code="en", limit=10) -> List[LocationResponse]:
    if prefix is None:
        return []

    # Search Geoname Alternate Names for locale-specific matches
    language_code = language_code.lower()
    matching_cities = Geoname.objects.filter(lang__name__istartswith=prefix, lang__iso_language_code=language_code)
    matching_cities = matching_cities.order_by("-population")
    matching_cities = matching_cities.distinct()
    matching_cities.prefetch_related("lang")

    city_matches = list(_geoname_to_location_response(city, language_code) for city in matching_cities[:limit])
    airport_matches = {
        _airport_to_location_response(airport): None for airport in airports.find_by_prefix(name_prefix=prefix)
    }

    # Sort airport code exact match to the top,
    airport_code_match = airports.find_by_airport_code(prefix)
    if airport_code_match:
        airport_code_match = _airport_to_location_response(airport_code_match)
        if airport_code_match in airport_matches:
            del airport_matches[airport_code_match]

        return [airport_code_match] + list(city_matches) + list(airport_matches.keys())

    return list(city_matches) + list(airport_matches.keys())


def find_city_by_simplenight_id(geoname_id: int, language_code="en") -> Optional[LocationResponse]:
    matching_locations = Geoname.objects.filter(geoname_id=geoname_id, lang__iso_language_code=language_code)
    if not matching_locations:
        return None

    return _geoname_to_location_response(matching_locations.first(), language_code)


def find_all_cities(country_code=None, language_code="en") -> List[LocationResponse]:
    locations = Geoname.objects.filter(lang__iso_language_code=language_code)
    if country_code:
        locations = locations.filter(iso_country_code=country_code)

    return list(_geoname_to_location_response(location, language_code) for location in locations)


def find_provider_location(provider: str, simplenight_location_id):
    try:

        return CityMap.objects.get(provider__name=provider, simplenight_city_id=simplenight_location_id).provider_city
    except CityMap.DoesNotExist:
        logger.error(f"Could not find city mapping for SimplenightID={simplenight_location_id} provider={provider}")
        return None


def _geoname_to_location_response(geoname: Geoname, language_code: str):
    localization = geoname.lang.filter(iso_language_code=language_code).order_by("-is_preferred").first()
    if not localization:
        localization = geoname.lang.filter(iso_language_code="en").first()

    if localization:
        displayed_language_code = localization.iso_language_code
        displayed_location_name = localization.name
    else:
        displayed_language_code = "en"
        displayed_location_name = geoname.location_name

    return LocationResponse(
        location_id=str(geoname.geoname_id),
        language_code=displayed_language_code,
        location_name=displayed_location_name,
        province=geoname.province,
        iso_country_code=geoname.iso_country_code,
        latitude=geoname.latitude,
        longitude=geoname.longitude,
        location_type=LocationType.CITY,
    )


def _airport_to_location_response(airport: Airport):
    return LocationResponse(
        location_id=airport.airport_code,
        language_code="en",
        location_name=airport.airport_name,
        province=None,
        iso_country_code=airport.iso_country_code,
        latitude=Decimal(airport.latitude),
        longitude=Decimal(airport.longitude),
        location_type=LocationType.AIRPORT,
    )
