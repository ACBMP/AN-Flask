"""Per-mode leaderboards plus the aggregate and achievement boards."""

from flask import Blueprint, redirect, render_template

from extensions import mongo
from badges import badge_score
from modes import (
    AA_ROLE_OF,
    LEGACY_RANKING_PATHS,
    MODES,
    RANKING_MODES,
    RANKING_TITLES,
    TOTAL_COLUMNS,
    mode_defaults,
    title,
)

rankings_bp = Blueprint("rankings", __name__)

# A player needs this many games in a mode before they're ranked; below it they
# are listed separately as "to be determined".
RANKED_GAMES = 10


def _dedupe(*results):
    """Chain cursors, dropping players already yielded by an earlier one."""
    seen = set()
    for result in results:
        for player in result:
            if player["_id"] not in seen:
                seen.add(player["_id"])
                yield player


def extract_mode_data(mode):
    """Ranked players for ``mode``, highest rating first, followed by the
    players who haven't played enough games to be ranked yet."""
    ranked = mongo.db.players.find(
        {f"{mode}games.total": {"$gte": RANKED_GAMES}, "hidden": False}
    ).sort(f"{mode}mmr", -1)
    tbd = mongo.db.players.find(
        {
            f"{mode}games.total": {"$gt": 0, "$lt": RANKED_GAMES},
            "hidden": False,
        }
    ).sort(f"{mode}mmr", -1)
    return list(_dedupe(ranked, tbd))


def _totals(average):
    """Players ranked across every mode, by summed (or mean) rating.

    Only modes where the player is actually ranked contribute to the rating,
    but games/wins/losses are counted everywhere.
    """
    players = list(
        mongo.db.players.find(
            {
                "$or": [{f"{m}games.total": {"$gte": RANKED_GAMES}} for m in MODES],
                "hidden": False,
            }
        )
    )
    for p in players:
        for m in MODES:
            # players from before a mode existed don't carry its fields yet
            for field, value in mode_defaults(m).items():
                p.setdefault(field, value)
        ranked_modes = 0
        p["totalmmr"] = 0
        p["totalgames"] = 0
        p["totalwins"] = 0
        p["totallosses"] = 0
        for m in MODES:
            games = p[m + "games"]
            if games["total"] >= RANKED_GAMES:
                ranked_modes += 1
                p["totalmmr"] += p[m + "mmr"]
            p["totalgames"] += games["total"]
            p["totalwins"] += games["won"]
            p["totallosses"] += games["lost"]
        if average and ranked_modes:
            p["totalmmr"] /= ranked_modes
    players.sort(key=lambda p: p["totalmmr"], reverse=True)
    for i, p in enumerate(players):
        p["totalrank"] = i + 1
    return players


def ranking(mode, name):
    return render_template(
        "ranking.html",
        data=extract_mode_data(mode),
        title=title(RANKING_TITLES[mode]),
        mode=name,
        key=mode,
        aa_role=AA_ROLE_OF.get(mode),
    )


# One route per mode rather than a single "/<mode>" rule, so an unknown path
# stays a plain 404 instead of being caught here.
for _path, (_mode, _name) in RANKING_MODES.items():
    rankings_bp.add_url_rule(
        f"/{_path}",
        endpoint=_path.replace("/", "_"),
        view_func=(lambda mode=_mode, name=_name: ranking(mode, name)),
    )

# ACR's AA boards moved; keep old links and bookmarks working.
for _old, _new in LEGACY_RANKING_PATHS.items():
    rankings_bp.add_url_rule(
        f"/{_old}", endpoint=f"legacy_{_old}", view_func=(lambda new=_new: redirect(f"/{new}", 301))
    )


@rankings_bp.route("/allmodes")
def allmodes():
    return render_template(
        "ranking.html", data=_totals(average=False), title=title("All Modes"), mode="All Modes",
        total_columns=TOTAL_COLUMNS,
    )


@rankings_bp.route("/average")
def average():
    return render_template(
        "ranking.html", data=_totals(average=True), title=title("Average"), mode="Average",
        total_columns=TOTAL_COLUMNS,
    )


@rankings_bp.route("/virtualtraining")
def vtraining():
    return render_template("vranking.html", data=mongo.db.vtraining.find({}))


@rankings_bp.route("/achievements")
def achievements():
    badged = []
    for p in mongo.db.players.find():
        if p.get("badges"):
            p["score"] = badge_score(p["badges"])
            badged.append(p)
    badged.sort(key=lambda p: p["score"], reverse=True)
    for i, p in enumerate(badged):
        p["rank"] = i + 1
    return render_template("achievements.html", data=badged, title=title("Achievements"))


@rankings_bp.route("/<mode>/statistics")
def statistics(mode):
    mode = mode.title()
    return render_template("statistics.html", mode=mode, title=title(f"{mode} Statistics"))
