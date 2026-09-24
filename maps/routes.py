"""Per-map statistics, one table per game mode."""

from flask import Blueprint, render_template

from extensions import mongo
from modes import MAP_MODES, title

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


@maps_bp.route("/maps")
def maps():
    data = {}
    for mode, name in MAP_MODES.items():
        map_stats = [
            dict({"name": d["name"]}, **d[mode])
            for d in mongo.db.maps.find({f"{mode}.games": {"$gt": 0}})
        ]
        _relative_host_ratings(map_stats)
        data[name] = map_stats
    return render_template(
        "maps.html", modes=MAP_MODES.values(), data=data, title=title("Map Statistics")
    )
