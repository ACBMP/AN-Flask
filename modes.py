"""Game mode definitions shared by the ranking, profile and map pages."""

# Artifact assault is rated per game, running and defending apart: player
# documents carry ``<key>r...`` / ``<key>d...`` ("acraa" gives "acraar" /
# "acraad"). Mirrors util.AA_GAMES in the Scripts. ACR's used to be the plain
# "aa" / "aar" / "aad"; the Scripts' migrate_acr_aa.py renamed the data.
AA_GAMES = {"acraa": "ACR", "ac3aa": "AC3", "ac4aa": "AC4"}
AA_ROLES = {"r": "Running", "d": "Defending"}


def _aa_boards():
    """One entry per Artifact assault leaderboard."""
    boards = []
    for key, game in AA_GAMES.items():
        for role, word in AA_ROLES.items():
            boards.append({
                "key": key + role,
                "game": game,
                "role": word.lower(),
                # the mode selector's id: "ACR AA Running", ...
                "name": f"{game} AA {word}",
                "title": f"{game} Artifact Assault {word}",
                "path": f"{game.lower()}/{word.lower()}",
                "card_title": f"{game} Artifact Assault ({word})",
                "tile_label": f"{game} AA {'Runner' if role == 'r' else 'Defender'} Rank",
            })
    return boards


AA_BOARDS = _aa_boards()
# role key ("acraar", "ac3aad", ...) -> "running" / "defending"
AA_ROLE_OF = {b["key"]: b["role"] for b in AA_BOARDS}

# Short mode keys as stored on player documents (``<key>mmr``, ``<key>games``).
MODES = ["mh", "e", "do", "dm", "asb"] + [b["key"] for b in AA_BOARDS]

MMR_FIELDS = [m + "mmr" for m in MODES]

# url path -> (short mode key, display name) for the per-mode ranking pages.
RANKING_MODES = {
    "manhunt": ("mh", "Manhunt"),
    "escort": ("e", "Escort"),
    "domination": ("do", "Domination"),
    "deathmatch": ("dm", "Deathmatch"),
    "assassinate": ("asb", "Assassinate"),
    **{b["path"]: (b["key"], b["name"]) for b in AA_BOARDS},
}

# ACR's AA boards' old addresses -> their new ones.
LEGACY_RANKING_PATHS = {"running": "acr/running", "defending": "acr/defending"}

# Page titles differ from the short display name for the AA modes.
RANKING_TITLES = {
    "mh": "Manhunt",
    "e": "Escort",
    "do": "Domination",
    "dm": "Deathmatch",
    "asb": "Assassinate",
    **{b["key"]: b["title"] for b in AA_BOARDS},
}

# Columns of the aggregate ("All Modes" / "Average") boards.
TOTAL_COLUMNS = [
    ("acraad", "ACR AA Defending"),
    ("acraar", "ACR AA Running"),
    ("do", "Domination"),
    ("e", "Escort"),
    ("mh", "Manhunt"),
    ("dm", "Deathmatch"),
    ("asb", "Assassinate"),
] + [(b["key"], b["name"]) for b in AA_BOARDS if b["game"] != "ACR"]

# How match documents spell each mode -> the mode selector ids it counts for.
MATCH_MODE_PANELS = {
    "Escort": ["Escort"],
    "Manhunt": ["Manhunt"],
    "Assassinate brotherhood": ["Assassinate"],
    "Domination": ["Domination"],
    "Deathmatch": ["Deathmatch"],
    **{
        f"{game} Artifact assault": [f"{game} AA Running", f"{game} AA Defending"]
        for game in AA_GAMES.values()
    },
}


def is_aa_mode(mode):
    """Whether a match document's mode is one of the Artifact assault games."""
    return bool(mode) and mode.lower().endswith("artifact assault")


def mode_defaults(key):
    """Empty stats for a mode a player document doesn't have yet (it gains
    them when the Scripts' add_mode.py runs, or with their first game)."""
    stats = {"totalscore": 0, "highscore": 0, "kills": 0, "deaths": 0}
    if key in AA_ROLE_OF:
        stats = {"totalscore": 0, "kills": 0, "deaths": 0, "scored": 0, "conceded": 0}
    games = {"total": 0, "won": 0, "lost": 0}
    if key in ("dm", "asb"):
        games.update(podium=0, finishes=0)
    return {
        key + "mmr": 800, key + "games": games, key + "stats": stats, key + "rank": 0,
        key + "rankchange": 0, key + "history": {"dates": [], "mmrs": [800]},
    }


def fill_mode_defaults(player):
    """Give a player document every mode field the pages read, in place.

    Covers modes the player doesn't have yet and counters missing inside ones
    they do (e.g. ``asbgames`` without ``podium``/``finishes`` for players who
    got the mode before those were tracked).
    """
    for mode in MODES:
        for field, default in mode_defaults(mode).items():
            current = player.get(field)
            if current is None:
                player[field] = default
            elif isinstance(default, dict) and isinstance(current, dict):
                for key, value in default.items():
                    current.setdefault(key, value)
    return player

# Short mode key -> display name, for the map statistics page. Artifact assault
# has one entry per game ("acraa", ...) because maps aren't split by
# running/defending.
MAP_MODES = {
    "e": "Escort",
    "mh": "Manhunt",
    "do": "Domination",
    "dm": "Deathmatch",
    "asb": "Assassinate Brotherhood",
    **{key: f"{game} Artifact Assault" for key, game in AA_GAMES.items()},
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
# brotherhood", "ACR Artifact assault"). Matched case-insensitively by prefix
# so a change in spelling on one side doesn't silently empty a page.
MAP_MODE_MATCH_PREFIXES = {
    "e": ("escort",),
    "mh": ("manhunt",),
    "do": ("domination",),
    "dm": ("deathmatch",),
    "asb": ("assassinate",),
    **{key: (f"{game.lower()} artifact",) for key, game in AA_GAMES.items()},
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
