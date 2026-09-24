"""Game mode definitions shared by the ranking, profile and map pages."""

# Short mode keys as stored on player documents (``<key>mmr``, ``<key>games``).
MODES = ["mh", "e", "aar", "aad", "do", "dm", "asb"]

MMR_FIELDS = [m + "mmr" for m in MODES]

# url path -> (short mode key, display name) for the per-mode ranking pages.
RANKING_MODES = {
    "manhunt": ("mh", "Manhunt"),
    "escort": ("e", "Escort"),
    "running": ("aar", "AA Running"),
    "defending": ("aad", "AA Defending"),
    "domination": ("do", "Domination"),
    "deathmatch": ("dm", "Deathmatch"),
    "assassinate": ("asb", "Assassinate"),
}

# Page titles differ from the short display name for the AA modes.
RANKING_TITLES = {
    "mh": "Manhunt",
    "e": "Escort",
    "aar": "Artifact Assault Running",
    "aad": "Artifact Assault Defending",
    "do": "Domination",
    "dm": "Deathmatch",
    "asb": "Assassinate",
}

# Short mode key -> display name, for the map statistics page. "aa" is a single
# combined entry here because maps aren't split by running/defending.
MAP_MODES = {
    "e": "Escort",
    "mh": "Manhunt",
    "do": "Domination",
    "aa": "Artifact Assault",
    "dm": "Deathmatch",
    "asb": "Assassinate Brotherhood",
}

SITE = "Assassins' Network"


def title(page):
    """Build a page title in the site's ``<page> | Assassins' Network`` style.

    The page part is translated; the site name is not, being a proper noun.
    """
    from i18n import translate

    return f"{translate(page)} | {SITE}"


# Map mode keys (as stored on map documents) matched against the ``mode`` field
# on match documents, which spells modes out in full ("Assassinate
# brotherhood", "Artifact Assault"). Matched case-insensitively by prefix so a
# change in spelling on one side doesn't silently empty a page.
MAP_MODE_MATCH_PREFIXES = {
    "e": ("escort",),
    "mh": ("manhunt",),
    "do": ("domination",),
    "dm": ("deathmatch",),
    "asb": ("assassinate",),
    "aa": ("artifact",),
}

# Escort measures stealth bonuses against VIP kills; every other mode uses the
# player's own kills.
MAP_MODE_DETECTION_BASIS = {"e": "vip"}


def map_slug(name):
    """URL form of a map name: ``Castel Gandolfo`` -> ``castel_gandolfo``."""
    return name.strip().lower().replace(" ", "_")


def map_key(slug):
    """Map-data form of a slug: ``castel_gandolfo`` -> ``castel gandolfo``.

    This is the spelling ``guides/map_data.py`` keys its calibration, spawn and
    route data by.
    """
    return slug.strip().lower().replace("_", " ")


def map_image(slug):
    """Static path of a map's overhead image."""
    return f"maps/{map_slug(slug)}.jpg"
