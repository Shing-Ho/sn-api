from api.models.models import CityMap, ProviderCity, Provider, Geoname

urban_adventures_simplenight_city_map = {
    "154": {"ua_name": "Accra", "sn_name": "Accra", "sn_id": 2306104},
    "151": {"ua_name": "Adelaide", "sn_name": "Adelaide", "sn_id": 2078025},
    "216": {"ua_name": "Agra", "sn_name": "Agra", "sn_id": 1279259},
    "88": {"ua_name": "Amsterdam", "sn_name": "Amsterdam", "sn_id": 2759794},
    "118": {"ua_name": "Annapolis", "sn_name": "Annapolis", "sn_id": 4347242},
    "70": {"ua_name": "Apia", "sn_name": "Apia", "sn_id": 4035413},
    "76": {"ua_name": "Arusha", "sn_name": "Arusha", "sn_id": 161325},
    "87": {"ua_name": "Athens", "sn_name": "Athens", "sn_id": 264371},
    "68": {"ua_name": "Auckland", "sn_name": "Auckland", "sn_id": 2193733},
    "215": {"ua_name": "Bali", "sn_name": "Denpasar", "sn_id": 1645528},
    "55": {"ua_name": "bangkok", "sn_name": "Bangkok", "sn_id": 1609350},
    "93": {"ua_name": "Barcelona", "sn_name": "Barcelona", "sn_id": 3128760},
    "123": {"ua_name": "Beijing", "sn_name": "Beijing", "sn_id": 1816670},
    "115": {"ua_name": "Beirut", "sn_name": "Beirut", "sn_id": 276781},
    "145": {"ua_name": "Berlin", "sn_name": "Berlin", "sn_id": 2950159},
    "155": {"ua_name": "Boston", "sn_name": "Boston", "sn_id": 4930956},
    "82": {"ua_name": "Brisbane", "sn_name": "Brisbane", "sn_id": 2174003},
    "177": {"ua_name": "Bucharest", "sn_name": "Bucharest", "sn_id": 683506},
    "90": {"ua_name": "Budapest", "sn_name": "Budapest", "sn_id": 3054643},
    "100": {"ua_name": "Buenos Aires", "sn_name": "Buenos Aires", "sn_id": 3435910},
    "131": {"ua_name": "Cairns", "sn_name": "Cairns", "sn_id": 2172797},
    "128": {"ua_name": "Cairo", "sn_name": "Cairo", "sn_id": 360630},
    "109": {"ua_name": "Charlotte", "sn_name": "Charlotte", "sn_id": 4460243},
    "77": {"ua_name": "Chiang Mai", "sn_name": "Chiang Mai", "sn_id": 1153671},
    "113": {"ua_name": "Copenhagen", "sn_name": "Copenhagen", "sn_id": 2618425},
    "72": {"ua_name": "Cusco", "sn_name": "Cusco", "sn_id": 3941584},
    "53": {"ua_name": "Delhi", "sn_name": "Delhi", "sn_id": 1273294},
    "112": {"ua_name": "Detroit", "sn_name": "Detroit", "sn_id": 4990729},
    "166": {"ua_name": "Dubai", "sn_name": "Dubai", "sn_id": 292223},
    "153": {"ua_name": "Durban", "sn_name": "Durban", "sn_id": 1007311},
    "176": {"ua_name": "Essaouira", "sn_name": "Essaouira", "sn_id": 2549263},
    "86": {"ua_name": "Florence", "sn_name": "Florence", "sn_id": 3176959},
    "54": {"ua_name": "Hanoi", "sn_name": "Hanoi", "sn_id": 1581130},
    "164": {"ua_name": "Havana", "sn_name": "Havana", "sn_id": 3553478},
    "58": {"ua_name": "Ho Chi Minh City", "sn_name": "Ho Chi Minh City", "sn_id": 1566083},
    "120": {"ua_name": "Hoi An", "sn_name": "Hoi An", "sn_id": 1580541},
    "135": {"ua_name": "Hong Kong", "sn_name": "Hong Kong", "sn_id": 1819729},
    "142": {"ua_name": "Houston", "sn_name": "Houston", "sn_id": 4699066},
    "119": {"ua_name": "Hue", "sn_name": "Hue", "sn_id": 1580240},
    "64": {"ua_name": "Istanbul", "sn_name": "Istanbul", "sn_id": 745044},
    "63": {"ua_name": "Johannesburg", "sn_name": "Johannesburg", "sn_id": 993800},
    "210": {"ua_name": "Kampala", "sn_name": "Kampala", "sn_id": 232422},
    "66": {"ua_name": "Kathmandu", "sn_name": "Kathmandu", "sn_id": 1283240},
    "152": {"ua_name": "Krakow", "sn_name": "Krakow", "sn_id": 3094802},
    "162": {"ua_name": "Kuala Lumpur", "sn_name": "Kuala Lumpur", "sn_id": 1735161},
    "158": {"ua_name": "Kumasi", "sn_name": "Kumasi", "sn_id": 2298890},
    "205": {"ua_name": "La Paz", "sn_name": "La Paz", "sn_id": 3911925},
    "71": {"ua_name": "Lima", "sn_name": "Lima", "sn_id": 3936456},
    "149": {"ua_name": "Lisbon", "sn_name": "Lisbon", "sn_id": 2267057},
    "203": {"ua_name": "Ljubljana", "sn_name": "Ljubljana", "sn_id": 3196359},
    "61": {"ua_name": "Los Angeles", "sn_name": "Los Angeles", "sn_id": 5368361},
    "207": {"ua_name": "Madrid", "sn_name": "Madrid", "sn_id": 3117735},
    "103": {"ua_name": "Melbourne", "sn_name": "Melbourne", "sn_id": 2158177},
    "127": {"ua_name": "Mendoza", "sn_name": "Mendoza", "sn_id": 3844421},
    "78": {"ua_name": "Merida", "sn_name": "Merida", "sn_id": 3523349},
    "170": {"ua_name": "Mexico City", "sn_name": "Mexico City", "sn_id": 3530597},
    "144": {"ua_name": "Moscow", "sn_name": "Moscow", "sn_id": 524901},
    "159": {"ua_name": "Mumbai", "sn_name": "Mumbai", "sn_id": 1275339},
    "217": {"ua_name": "Nadi", "sn_name": "Nadi", "sn_id": 2202064},
    "75": {"ua_name": "Nairobi", "sn_name": "Nairobi", "sn_id": 184745},
    "60": {"ua_name": "New York", "sn_name": "New York City", "sn_id": 5128581},
    "240": {"ua_name": "Nha Trang", "sn_name": "Nha Trang", "sn_id": 1572151},
    "111": {"ua_name": "Panama City", "sn_name": "Panama City", "sn_id": 4167694},
    "150": {"ua_name": "Paris", "sn_name": "Paris", "sn_id": 2988507},
    "95": {"ua_name": "Philadelphia", "sn_name": "Philadelphia", "sn_id": 4560349},
    "67": {"ua_name": "Pokhara", "sn_name": "Pokhara", "sn_id": 1282898},
    "167": {"ua_name": "Porto", "sn_name": "Porto", "sn_id": 2735943},
    "136": {"ua_name": "Prague", "sn_name": "Prague", "sn_id": 3067696},
    "116": {"ua_name": "Quito", "sn_name": "Quito", "sn_id": 3652462},
    "96": {"ua_name": "Riga", "sn_name": "Riga", "sn_id": 456172},
    "65": {"ua_name": "Rio de Janeiro", "sn_name": "Rio de Janeiro", "sn_id": 3451190},
    "91": {"ua_name": "Rome", "sn_name": "Rome", "sn_id": 3169070},
    "202": {"ua_name": "Samarkand", "sn_name": "Samarkand", "sn_id": 1216265},
    "62": {"ua_name": "San Francisco", "sn_name": "San Francisco", "sn_id": 5391959},
    "169": {"ua_name": "San Jose", "sn_name": "San Jose", "sn_id": 3621841},
    "171": {"ua_name": "San Sebastian", "sn_name": "San Sebastian de los Reyes", "sn_id": 3110040},
    "224": {"ua_name": "Santiago de Cuba", "sn_name": "Santiago de Cuba", "sn_id": 3536729},
    "156": {"ua_name": "Seoul", "sn_name": "Seoul", "sn_id": 1835848},
    "161": {"ua_name": "Shanghai", "sn_name": "Shanghai", "sn_id": 1796236},
    "56": {"ua_name": "Siem Reap", "sn_name": "Siem Reap", "sn_id": 1822214},
    "206": {"ua_name": "Singapore", "sn_name": "Singapore", "sn_id": 1880252},
    "168": {"ua_name": "Sofia", "sn_name": "Sofia", "sn_id": 727011},
    "208": {"ua_name": "Split", "sn_name": "Split", "sn_id": 3190261},
    "98": {"ua_name": "St. Petersburg", "sn_name": "Saint Petersburg", "sn_id": 498817},
    "59": {"ua_name": "Sydney", "sn_name": "Sydney", "sn_id": 2147714},
    "172": {"ua_name": "Taipei", "sn_name": "Taipei", "sn_id": 1668341},
    "108": {"ua_name": "Thessaloniki", "sn_name": "Thessaloniki", "sn_id": 734077},
    "163": {"ua_name": "Tokyo", "sn_name": "Tokyo", "sn_id": 1850147},
    "81": {"ua_name": "Toronto", "sn_name": "Toronto", "sn_id": 6167865},
    "80": {"ua_name": "Vancouver", "sn_name": "Vancouver", "sn_id": 6173331},
    "139": {"ua_name": "Venice", "sn_name": "Venice", "sn_id": 3164603},
    "304": {"ua_name": "Vienna", "sn_name": "Vienna", "sn_id": 2761369},
    "143": {"ua_name": "Vilnius", "sn_name": "Vilnius", "sn_id": 593116},
    "117": {"ua_name": "Washington, D.C.", "sn_name": "Washington", "sn_id": 4140963},
    "157": {"ua_name": "Xian", "sn_name": "Xianyang", "sn_id": 1790353},
    "175": {"ua_name": "Yangon", "sn_name": "Yangon", "sn_id": 1298824},
    "213": {"ua_name": "Zanzibar", "sn_name": "Zanzibar", "sn_id": 148730},
}


def remove_old_mappings(provider):
    provider_city_mappings = CityMap.objects.filter(provider=provider)
    if provider_city_mappings:
        provider_city_mappings.delete()

    provider_cities = ProviderCity.objects.filter(provider=provider)
    if provider_cities:
        provider_cities.delete()


def insert_mappings(*_):
    # Cleanup an old migration
    old_provider = Provider.objects.filter(name="urban_adventures")
    if old_provider:
        remove_old_mappings(old_provider[0])

    new_provider = Provider.objects.get_or_create(name="urban")[0]
    remove_old_mappings(new_provider)

    old_provider.delete()

    try:
        for dest_id in urban_adventures_simplenight_city_map:
            geoname_id = urban_adventures_simplenight_city_map[dest_id]["sn_id"]
            sn_city = Geoname.objects.get(geoname_id=geoname_id)

            ua_city = ProviderCity.objects.get_or_create(
                provider=new_provider,
                location_name=urban_adventures_simplenight_city_map[dest_id]["ua_name"],
                provider_code=dest_id,
                country_code=sn_city.iso_country_code,
                latitude=sn_city.latitude,
                longitude=sn_city.longitude,
            )[0]

            CityMap.objects.get_or_create(
                provider=new_provider, provider_city=ua_city, simplenight_city=sn_city,
            )
    except (Geoname.DoesNotExist, CityMap.DoesNotExist):
        pass
