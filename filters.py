"""Jinja2 template filters used across the site's templates."""

import re

from extensions import mongo
from i18n import translate
from badges import filter_badges, full_badge_names, transform_badges
from modes import MMR_FIELDS, is_aa_mode

# Rating thresholds, ascending. The last entry catches everything above.
RANK_TIERS = [
    (801, "Disciple", "badge_1"),
    (1000, "Cleric", "badge_2"),
    (1100, "Cleric Supreme", "badge_3"),
    (1200, "Grand Cleric", "badge_4"),
    (1400, "Grand Master Cleric", "badge_6"),
    (None, "Supreme Overlord Cleric", "badge_5"),
]


def _tier(elo):
    for threshold, name, badge in RANK_TIERS:
        if threshold is None or elo < threshold:
            return name, badge
    raise AssertionError("RANK_TIERS must end with a None threshold")


def _ratio(numerator, denominator, fmt="{0:.2f}"):
    """Format a ratio, yielding a zero rather than raising on bad input."""
    try:
        return fmt.format(round(numerator / denominator, 2))
    except (TypeError, ZeroDivisionError):
        return fmt.format(0)


def winrate(w, l):
    return _ratio(w * 100, w + l, "{0:.2f}%")


def tierate(games, wins, losses):
    return _ratio((games - wins - losses) * 100, games, "{0:.2f}%")


def kdratio(k, d):
    return _ratio(k, d)


def avgscore(s, g):
    return _ratio(s, g)


def avgkills(k, g):
    return _ratio(k, g)


def avgdeaths(d, g):
    return _ratio(d, g)


def sub(a, b):
    return a - b


def try_value(entry, value):
    try:
        return entry[value]
    except (KeyError, IndexError, TypeError):
        return "Unknown"


def try_value_paran(entry, value):
    try:
        v = entry[value]
    except (KeyError, IndexError, TypeError):
        return ""
    if isinstance(v, (int, float)):
        v = "{0:+.2f}".format(v)
    return "(" + v + ")"


def try_rating_change(entry, value="mmrchange"):
    try:
        return "{0:+.2f}".format(entry[value])
    except (KeyError, IndexError, TypeError, ValueError):
        return "-"


def rank_title(elo):
    return translate(_tier(elo)[0])


def rank_pic_small(elo):
    return _tier(elo)[1] + "_small.png"


def rank_pic_big(elo):
    return _tier(elo)[1] + "_big.png"


def top_rating(player):
    """A player's highest rating across all modes."""
    return max((player[f] for f in MMR_FIELDS if player.get(f) is not None), default=800)


def top_rank_pic(player, size="small"):
    """Badge for a player's highest rating across all modes."""
    values = [player[f] for f in MMR_FIELDS if player.get(f) is not None]
    if not values:
        return None
    return rank_pic_big(max(values)) if size == "big" else rank_pic_small(max(values))


def name_in_db(name):
    """Link a name to its profile, if it belongs to a visible player."""
    pattern = re.compile(f"^{re.escape(name)}$", re.IGNORECASE)
    player = mongo.db.players.find_one({"name": pattern})
    if player is None:
        player = mongo.db.players.find_one({"ign": pattern})
    if player is None:
        return name
    if player["hidden"]:
        return "HIDDEN"
    return f"<a href=\"/profile/{player['name']}\">{player['name']}</a>"


def is_hidden(name):
    player = mongo.db.players.find_one({"name": name})
    return bool(player and player["hidden"])


FILTERS = {
    "winrate": winrate,
    "kdratio": kdratio,
    "avgscore": avgscore,
    "avgkills": avgkills,
    "avgdeaths": avgdeaths,
    "sub": sub,
    "tierate": tierate,
    "try_value": try_value,
    "try_value_paran": try_value_paran,
    "try_rating_change": try_rating_change,
    "rank_title": rank_title,
    "rank_pic_small": rank_pic_small,
    "rank_pic_big": rank_pic_big,
    "top_rank_pic": top_rank_pic,
    "name_in_db": name_in_db,
    "full_badge_names": full_badge_names,
    "transform_badges": transform_badges,
    "top_rating": top_rating,
    "is_aa_mode": is_aa_mode,
    "filter_badges": filter_badges,
    "is_hidden": is_hidden,
}


def register_filters(app):
    for name, func in FILTERS.items():
        app.add_template_filter(func, name)
