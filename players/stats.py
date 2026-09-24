"""Bonus-stat aggregation for player profiles.

The newer per-match bonus stats aren't rolled up onto the player document, so
they're computed on the fly. Our match collection is small enough that this
isn't a problem.
"""

from collections import Counter

from extensions import mongo

# Groups of related bonus stats shown together in the profile's "Detailed
# Stats" card, in the order they should be laid out (two per row: 1&2, 3&4,
# 5&6, then Lobby & Characters). Each stat only appears if it's actually
# present in the computed averages for that mode.
BONUS_STAT_GROUPS = [
    ("Kills", ["Kill", "VIP", "Incognito", "Silent", "Discreet"]),
    ("Types", ["Acrobatic", "Hidden", "Focus", "Grab", "Slow Poison"]),
    ("Defense", ["Stun", "Escape", "Lure"]),
    ("Teamplay", ["Co-Op Kill", "Co-Op Stun", "Knockout", "Multi-Kill", "Diversion", "Intercepted"]),
    ("Variety", ["Variety", "Greater Variety", "Extreme Variety"]),
    ("Other", ["Checkpoint", "Chest", "Other"]),
]

# Bonuses too rare in Manhunt/Escort to be worth a column.
MH_E_EXCLUDED_BONUSES = {
    "Chain", "Chest", "Close Call", "Double Escape", "Fast Poison", "Final Chest",
    "First Blood", "Grounded", "Mid-Air", "Poacher", "Poison", "Rescue", "Revenge",
    "Savior", "Triple Escape",
}

# Games on a character before its average rating change is meaningful.
MIN_CHARACTER_GAMES = 5


def match_query(igns, mode=None, ffa=False):
    """Query matching any match one of ``igns`` played in."""
    if ffa:
        fields = ["players"]
    else:
        fields = ["team1", "team2"]
    query = {"$or": [{f: {"$elemMatch": {"player": ign}}} for f in fields for ign in igns]}
    if mode:
        query["mode"] = mode
    return query


def _bonus_count(player, stat):
    return player.get("bonuses", {}).get(stat, {}).get("count", 0)


def _split_teams(match, igns, ffa):
    """Return (me, teammates, opponents) for the first of ``igns`` present."""
    teams = [match.get("players", [])] if ffa else [match.get("team1", []), match.get("team2", [])]
    me = None
    teammates = []
    opponents = []
    for team in teams:
        mine = [p for p in team if p.get("player") in igns]
        if mine:
            me = mine[0]
            teammates = [p for p in team if p.get("player") not in igns]
        else:
            opponents = team
    return me, teammates, opponents


def compute_extra_acb_stats(igns, mode, is_ffa, detection_basis="kills", excluded_bonuses=None):
    """Average bonus stats, character usage and detection breakdown for a
    player across every match of ``mode``.

    ``detection_basis`` selects what the Incognito/Discreet/Silent counts are
    measured against: the player's own kills, or their VIP kills in Escort.
    """
    excluded_bonuses = excluded_bonuses or set()

    games = 0
    bonus_totals = Counter()
    character_counts = Counter()
    character_rating_totals = Counter()
    coop_kills = 0
    kill_vip_total = 0
    own_kills_total = 0
    incognito = discreet = silent = vip_total = 0

    for match in mongo.db.matches.find(match_query(igns, mode, is_ffa)):
        me, teammates, opponents = _split_teams(match, igns, is_ffa)
        if me is None or "bonuses" not in me:
            continue

        games += 1
        bonuses = me["bonuses"]
        for stat, val in bonuses.items():
            if stat in excluded_bonuses:
                continue
            if stat == "Other":
                bonus_totals[stat] += val.get("score", 0)
            elif "count" in val:
                bonus_totals[stat] += val["count"]

        if me.get("character"):
            character_counts[me["character"]] += 1
            character_rating_totals[me["character"]] += me.get("mmrchange", 0)

        my_kills = me.get("kills", 0)
        my_vips = _bonus_count(me, "VIP")
        coop_kills += _bonus_count(me, "Co-Op Kill")
        kill_vip_total += my_kills + my_vips
        own_kills_total += my_kills

        # Only the last teammate's kills are attributed here; this matches how
        # the stat has always been reported (2v2 is the common case).
        team_vip_total = my_vips
        mate_kills = 0
        for mate in teammates:
            mate_kills = mate.get("kills", 0)
            kill_vip_total += mate_kills + _bonus_count(mate, "VIP")
            team_vip_total += _bonus_count(mate, "VIP")
        bonus_totals["Teammate Kills"] += mate_kills
        bonus_totals["Team VIP"] += team_vip_total

        # Assigned even when there are no opponents (free-for-all modes), so the
        # profile keeps showing the row rather than dropping it entirely.
        bonus_totals["Opponent Kills"] += sum(o.get("kills", 0) for o in opponents)
        bonus_totals["Opponent Deaths"] += sum(o.get("deaths", 0) for o in opponents)
        bonus_totals["Opponent VIP"] += sum(_bonus_count(o, "VIP") for o in opponents)

        incognito += _bonus_count(me, "Incognito")
        discreet += _bonus_count(me, "Discreet")
        silent += _bonus_count(me, "Silent")
        vip_total += my_vips

    avg_bonuses = (
        {stat: round(total / games, 2) for stat, total in sorted(bonus_totals.items())}
        if games
        else {}
    )
    character_avg_ratings = {
        char: total / character_counts[char]
        for char, total in character_rating_totals.items()
        if character_counts[char] >= MIN_CHARACTER_GAMES
    }
    detection_total = vip_total if detection_basis == "vip" else own_kills_total

    return {
        "games": games,
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


def _char_cell(character, note):
    if not character:
        return "-"
    icon = (
        '<img src="/static/char_svg/{0}.svg" alt="{1}" '
        'style="height:1.1em;vertical-align:middle;margin-right:0.35em">'
    ).format(character.lower(), character)
    return "{0}{1} ({2})".format(icon, character, note)


def bonus_stat_groups(extra):
    """Lay the computed stats out as (group name, [(label, value)]) rows."""
    avg = extra["avg_bonuses"]
    groups = []
    for name, keys in BONUS_STAT_GROUPS:
        row = [(key, avg[key]) for key in keys if key in avg]
        if name == "Kills" and extra["games"]:
            row.append(("Chase", round(extra["detection_share"]["none"] / extra["games"], 2)))
        if name == "Teamplay":
            row.append(("Co-op Kill %", "{0}%".format(extra["coop_percentage"])))
        if row:
            groups.append((name, row))

    lobby_keys = sorted(k for k in avg if k.startswith("Opponent ")) + [
        k for k in ("Team VIP", "Teammate Kills") if k in avg
    ]
    if lobby_keys:
        groups.append(("Lobby", [(key, avg[key]) for key in lobby_keys]))

    char_row = []
    if extra["character"]:
        count = extra["character_share"].get(extra["character"], 0)
        char_row.append(("Most Played", _char_cell(extra["character"], count)))
    for label, key in (("Best Performing", "best_character"), ("Worst Performing", "worst_character")):
        if extra[key]:
            name, total = extra[key]
            char_row.append((label, _char_cell(name, "{0:+.2f}".format(total))))
    if char_row:
        groups.append(("Characters", char_row))

    return groups
