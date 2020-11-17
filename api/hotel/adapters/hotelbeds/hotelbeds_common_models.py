HOTELBEDS_LANGUAGE_MAP = {
    "en": "ENG",
}


def get_language_mapping(language):
    return HOTELBEDS_LANGUAGE_MAP.get(language, "ENG")
