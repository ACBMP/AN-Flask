"""Map statistics: the per-mode listing, and a page per map."""

import re

from flask import Blueprint, abort, render_template

import an_api
from extensions import mongo
from guides.map_data import spawns as LOCAL_SPAWNS, world_corners
from modes import MAP_MODES, map_image, map_key, map_slug, title
from players.stats import bonus_stat_groups

from .stats import compute_map_stats

maps_bp = Blueprint("maps", __name__)


def _relative_host_ratings(map_stats):
    """Rewrite each map's absolute host rating as a signed percentage relative
    to the average across the mode, which is what the table displays."""
    rated = [m["hostrating"] for m in map_stats if "hostrating" in m]
    if not rated:
        return
    average = sum(rated) / len(rated)
    if not average:
        return
    for m in map_stats:
        if "hostrating" in m:
            relative = int(round((m["hostrating"] / average - 1) * 100))
            m["hostrating"] = f"+{relative}" if relative >= 0 else str(relative)


def mode_rows(mode_key):
    """Every map played in this mode, with host ratings made relative to the
    mode's average. Shared with the map page so a map's numbers there are the
    same ones the listing shows."""
    rows = [
        dict({"name": d["name"], "slug": map_slug(d["name"])}, **d[mode_key])
        for d in mongo.db.maps.find({f"{mode_key}.games": {"$gt": 0}})
    ]
    _relative_host_ratings(rows)
    return rows


@maps_bp.route("/maps")
def maps():
    data = {name: mode_rows(mode) for mode, name in MAP_MODES.items()}
    return render_template(
        "maps.html", modes=MAP_MODES.values(), data=data, title=title("Map Statistics")
    )


def _guide_links(key):
    """Which guide pages exist for this map.

    Both guide pages need calibration data to place anything on the image, and
    they take their points from AN-API with a local fallback for spawns, so ask
    the API once rather than linking somewhere that renders empty.
    """
    if key not in world_corners:
        return {}
    data = an_api.get(f"/maps/{key}") or {}
    links = {}
    if data.get("spawns") or key in LOCAL_SPAWNS:
        links["spawns"] = f"/guides/spawns/{key}"
    if data.get("routes"):
        links["routes"] = f"/guides/routes/{key}"
    return links


@maps_bp.route("/maps/<slug>")
def map_detail(slug):
    name = map_key(slug)
    doc = mongo.db.maps.find_one({"name": re.compile(f"^{re.escape(name)}$", re.I)})
    if doc is None:
        abort(404)

    # Match documents may spell the map differently from the map document, so
    # accept either spelling when aggregating.
    names = {doc["name"], name}

    modes = []
    for key, mode_name in MAP_MODES.items():
        if not (doc.get(key) or {}).get("games"):
            continue
        row = next((r for r in mode_rows(key) if r["slug"] == map_slug(doc["name"])), None)
        if row is None:
            continue
        extra = compute_map_stats(names, key)
        extra["groups"] = bonus_stat_groups(extra)
        modes.append({"key": key, "name": mode_name, "row": row, "extra": extra})

    return render_template(
        "map_detail.html",
        name=doc["name"],
        image=map_image(slug),
        links=_guide_links(name),
        modes=modes,
        title=title(f"{doc['name']} Map"),
    )
