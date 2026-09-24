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
    """Build a page title in the site's ``<page> | Assassins' Network`` style."""
    return f"{page} | {SITE}"
