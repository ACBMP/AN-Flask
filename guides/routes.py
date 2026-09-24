from flask import Blueprint, abort, render_template

import an_api
from markdown_page import MATH_EXTENSIONS, render_markdown
from modes import map_image, title

from .map_data import compute_affine_from_corners, pixel_corners, world_corners, world_to_pixel

guides_bp = Blueprint("guides", __name__, url_prefix="/guides")

@guides_bp.route("/")
def overview_page():
    return render_markdown("guides/content/overview.md", title("Guides Overview"))


def _calibration(map_name):
    """Affine world->pixel transform for a map, or 404 if it isn't calibrated."""
    if map_name not in world_corners:
        abort(404)
    return compute_affine_from_corners(
        world_corners[map_name][0], world_corners[map_name][1],
        pixel_corners[map_name][0], pixel_corners[map_name][1],
    )


@guides_bp.route("/spawns/<map_name>")
def spawns_page(map_name):
    sx, ox, sy, oy = _calibration(map_name)
    data = an_api.get(f"/maps/{map_name}") or {}
    if not data.get("spawns"):
        abort(404)
    ordered = sorted(data["spawns"].values(), key=lambda s: s["index"])
    map_spawns = [world_to_pixel(s["x"], s["y"], sx, ox, sy, oy) for s in ordered]

    # accounting for error
    scale = (abs(sx) + abs(sy)) / 2.0
    minR = [30 * scale, 4 * scale, 30 * scale]
    smallR = [40 * scale, 5 * scale, 40 * scale]
    largeR = [60 * scale, 15 * scale, 60 * scale]
    maxR = [90 * scale, 100 * scale, 90 * scale]
    w = [0.2, 0.2, 0.5]
    return render_template("spawns.html", name=map_name.title(), title=title(f"{map_name.title()} Spawns"), points=map_spawns, smallR=smallR, largeR=largeR, minR=minR, maxR=maxR, w=w, image_file=map_image(map_name))


@guides_bp.route("/routes/<map_name>")
def routes_page(map_name):
    sx, ox, sy, oy = _calibration(map_name)
    data = an_api.get(f"/maps/{map_name}") or {}
    if not data.get("routes"):
        abort(404)
    map_routes = {
            j["name"]: [list(world_to_pixel(i["x"], i["y"], sx, ox, sy, oy)) + [i["isCheckpoint"]] for i in j["points"]] for j in data["routes"]
            }

    checkpoint_radius = 3 * (abs(sx) + abs(sy)) / 2
    return render_template("routes.html", name=map_name.title(), title=title(f"{map_name.title()} Routes"), routes=map_routes, image_file=map_image(map_name), checkpoint_radius=checkpoint_radius)


@guides_bp.route("/<filename>")
def render_md(filename):
    return render_markdown(
        f"guides/content/{filename}.md",
        title(f"{filename.title()} Guide"),
        extensions=MATH_EXTENSIONS,
    )

@guides_bp.route("/modes")
def modes_page():
    return render_markdown(
        "guides/content/modes.md", title("Modes Overview"), template="modes.html"
    )
