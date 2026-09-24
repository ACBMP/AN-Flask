"""Bonus-stat aggregation for a single map.

The player profile aggregates a player's bonuses across their matches; this
does the same across every player in every match played on one map, so the map
page can show the same "Detailed Stats" card. Averages here are per
player-game, matching how the map listing divides its totals by ``players``.
"""

import re
from collections import Counter

from extensions import mongo
from modes import MAP_MODE_DETECTION_BASIS, MAP_MODE_MATCH_PREFIXES
from players.stats import MIN_CHARACTER_GAMES


def name_query(names):
    """Case-insensitive exact match against any of ``names``."""
    return {"$in": [re.compile(f"^{re.escape(n)}$", re.I) for n in names]}


def match_modes(map_names, mode_key):
    """Match ``mode`` values on this map belonging to ``mode_key``.

    Read off the data rather than hardcoded, since a map document's key ("asb")
    and a match's mode ("Assassinate brotherhood") are spelled differently.
    """
    prefixes = MAP_MODE_MATCH_PREFIXES.get(mode_key, ())
    modes = mongo.db.matches.distinct("mode", {"map": name_query(map_names)})
    return [m for m in modes if m and m.lower().startswith(prefixes)]


def _entries(match):
    """Every player row in a match, team-based or free-for-all."""
    return match.get("players") or (match.get("team1", []) + match.get("team2", []))


def compute_map_stats(map_names, mode_key):
    """Aggregate bonus stats over every match played on this map in this mode.

    Returns the same shape as ``players.stats.compute_extra_acb_stats`` so
    ``bonus_stat_groups`` can lay it out identically, with ``games`` counting
    player-games (every average is per player per game) and ``matches``
    counting the matches behind them.
    """
    modes = match_modes(map_names, mode_key)
    detection_basis = MAP_MODE_DETECTION_BASIS.get(mode_key, "kills")

    matches = 0
    player_games = 0
    bonus_totals = Counter()
    character_counts = Counter()
    character_rating_totals = Counter()
    coop_kills = 0
    kill_vip_total = 0
    own_kills_total = 0
    incognito = discreet = silent = vip_total = 0

    if modes:
        cursor = mongo.db.matches.find({"map": name_query(map_names), "mode": {"$in": modes}})
    else:
        cursor = []

    for match in cursor:
        counted = False
        for entry in _entries(match):
            bonuses = entry.get("bonuses")
            if not bonuses:
                continue
            counted = True
            player_games += 1

            for stat, val in bonuses.items():
                if stat == "Other":
                    bonus_totals[stat] += val.get("score", 0)
                elif "count" in val:
                    bonus_totals[stat] += val["count"]

            if entry.get("character"):
                character_counts[entry["character"]] += 1
                character_rating_totals[entry["character"]] += entry.get("mmrchange", 0)

            kills = entry.get("kills", 0)
            vips = bonuses.get("VIP", {}).get("count", 0)
            coop_kills += bonuses.get("Co-Op Kill", {}).get("count", 0)
            kill_vip_total += kills + vips
            own_kills_total += kills
            incognito += bonuses.get("Incognito", {}).get("count", 0)
            discreet += bonuses.get("Discreet", {}).get("count", 0)
            silent += bonuses.get("Silent", {}).get("count", 0)
            vip_total += vips
        if counted:
            matches += 1

    avg_bonuses = (
        {stat: round(total / player_games, 2) for stat, total in sorted(bonus_totals.items())}
        if player_games
        else {}
    )
    character_avg_ratings = {
        char: total / character_counts[char]
        for char, total in character_rating_totals.items()
        if character_counts[char] >= MIN_CHARACTER_GAMES
    }
    detection_total = vip_total if detection_basis == "vip" else own_kills_total

    return {
        "games": player_games,
        "matches": matches,
        "modes": modes,
        "avg_bonuses": avg_bonuses,
        "character": character_counts.most_common(1)[0][0] if character_counts else None,
        "character_share": dict(character_counts.most_common()),
        "best_character": max(character_avg_ratings.items(), key=lambda kv: kv[1])
        if character_avg_ratings
        else None,
        "worst_character": min(character_avg_ratings.items(), key=lambda kv: kv[1])
        if character_avg_ratings
        else None,
        "coop_percentage": round(coop_kills / kill_vip_total * 100, 2) if kill_vip_total else 0,
        "detection_share": {
            "incognito": incognito,
            "discreet": discreet,
            "silent": silent,
            "none": max(detection_total - incognito - discreet - silent, 0),
        },
        "detection_total": detection_total,
        "detection_basis": detection_basis,
    }
