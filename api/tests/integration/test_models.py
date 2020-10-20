from api.models.models import Geoname, GeonameAlternateName, ProviderCity, Provider, CityMap, Airport, ProviderHotel


def create_geoname(geoname_id, location_name, province, country_code, population=0, latitude=None, longitude=None):
    if latitude is None:
        latitude = 50.0

    if longitude is None:
        longitude = 50.0

    geoname = Geoname(
        geoname_id=geoname_id,
        location_name=location_name,
        province=province,
        iso_country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        population=population,
        timezone="US/Pacific",
    )

    geoname.save()
    return geoname


def create_geoname_altname(pk_id, geoname, lang_code, name):
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


def create_provider(provider_name: str):
    provider = Provider(name=provider_name)
    provider.save()

    return provider


def create_provider_city(
    provider_name: str,
    code: str,
    name: str,
    province: str,
    country: str,
    latitude: float = None,
    longitude: float = None,
):
    if latitude is None:
        latitude = 0.0
        longitude = 0.0

    provider = Provider.objects.get(name=provider_name)
    provider_city = ProviderCity(
        provider=provider,
        provider_code=code,
        location_name=name,
        province=province,
        country_code=country,
        latitude=latitude,
        longitude=longitude,
    )

    provider_city.save()
    return provider_city


def create_city_mapping(provider_name: str, simplenight_id: str, provider_id: str):
    provider = Provider.objects.get(name=provider_name)
    city_mapping = CityMap(provider=provider, simplenight_city_id=simplenight_id, provider_city_id=provider_id)
    city_mapping.save()

    return city_mapping


def create_airport(airport_id, airport_code, airport_name):
    airport = Airport(
        airport_id=airport_id, airport_code=airport_code, airport_name=airport_name, latitude=50.0, longitude=50.0
    )

    airport.save()
    return airport


def create_provider_hotel(provider, provider_code, hotel_name):
    provider_hotel = ProviderHotel(
        provider=provider,
        hotel_name=hotel_name,
        provider_code=provider_code
    )

    provider_hotel.save()
    return provider_hotel