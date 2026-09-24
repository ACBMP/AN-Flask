"""Player directory and individual profile pages."""

from flask import Blueprint, abort, render_template

from extensions import mongo
from modes import title

from .stats import (
    MH_E_EXCLUDED_BONUSES,
    bonus_stat_groups,
    compute_extra_acb_stats,
    match_query,
)

players_bp = Blueprint("players", __name__)

# Modes played free-for-all, where everyone is in a single "players" list
# instead of two teams.
FFA_MODES = ["Deathmatch", "Assassinate brotherhood"]

# Matches shown in a profile's history.
PROFILE_MATCHES = 100


def player_igns(player):
    """Every in-game name a player answers to, including their display name,
    so a profile's match history isn't empty for renamed players."""
    igns = player["ign"]
    if isinstance(igns, str):
        igns = [igns]
    if player["name"] not in igns:
        igns = igns + [player["name"]]
    return igns


def _format_change(value):
    return "+" + str(round(value, 2)) if value > 0 else str(round(value, 2))


def _annotate_ffa(match, name):
    """Record the player's rating change and result on a free-for-all match."""
    # The template reads team1 for every mode.
    match["team1"] = match["players"]
    me = next((p for p in match["players"] if p["player"] == name), None)
    change = me.get("mmrchange") if me else None
    if change is None:
        match["mmrchange"] = "Unknown"
        match["player_result"] = "unknown"
        return
    match["mmrchange"] = _format_change(change)
    match["player_result"] = "win" if change > 0 else "loss" if change < 0 else "tie"


def _annotate_team(match, name):
    """Record the player's rating change and result on a team match."""
    team_no = 2
    for j in (1, 2):
        me = next((p for p in match[f"team{j}"] if p["player"] == name), None)
        if me:
            team_no = j
            change = me.get("mmrchange")
            match["mmrchange"] = "Unknown" if change is None else _format_change(change)
            break
    else:
        match["mmrchange"] = "Unknown"

    outcome = match.get("outcome")
    if outcome == 0:
        match["player_result"] = "tie"
    elif outcome == team_no:
        match["player_result"] = "win"
    else:
        match["player_result"] = "loss"


def recent_matches(name, igns):
    """The player's latest matches, annotated with their own rating change and
    win/loss result so the template doesn't have to search the teams."""
    matches = list(
        mongo.db.matches.find(
            {"$or": [match_query(igns, ffa=False), match_query(igns, ffa=True)]}
        )
        .sort("_id", -1)
        .limit(PROFILE_MATCHES)
    )
    for match in matches:
        if match["mode"] in FFA_MODES:
            _annotate_ffa(match, name)
        else:
            _annotate_team(match, name)
    return matches


@players_bp.route("/players")
def players():
    data = mongo.db.players.find({"hidden": False}).sort("name")
    return render_template("players.html", data=data, title=title("Players"))


@players_bp.route("/profile/<name>")
def display_profile(name):
    data = mongo.db.players.find_one({"name": name, "hidden": False})
    if data is None:
        abort(404)
    igns = player_igns(data)

    mh_extra = compute_extra_acb_stats(
        igns, "Manhunt", False, detection_basis="kills", excluded_bonuses=MH_E_EXCLUDED_BONUSES
    )
    e_extra = compute_extra_acb_stats(
        igns, "Escort", False, detection_basis="vip", excluded_bonuses=MH_E_EXCLUDED_BONUSES
    )
    asb_extra = compute_extra_acb_stats(
        igns, "Assassinate brotherhood", True, detection_basis="kills"
    )
    for extra in (mh_extra, e_extra, asb_extra):
        extra["groups"] = bonus_stat_groups(extra)

    return render_template(
        "profile.html",
        data=data,
        data_matches=recent_matches(name, igns),
        mh_extra=mh_extra,
        e_extra=e_extra,
        asb_extra=asb_extra,
        mh_e_stat_keys=sorted(set(mh_extra["avg_bonuses"]) | set(e_extra["avg_bonuses"])),
        title=title("Player's Profile"),
    )
