from flask import Blueprint, abort, render_template

import an_api
from markdown_page import MATH_EXTENSIONS, render_markdown
from modes import title

from .map_data import *

guides_bp = Blueprint("guides", __name__, url_prefix="/guides")

@guides_bp.route("/")
def overview_page():
    return render_markdown("guides/content/overview.md", title("Guides Overview"))


@guides_bp.route("/spawns/<map_name>")
def spawns_page(map_name):
    sx, ox, sy, oy = compute_affine_from_corners(world_corners[map_name][0], world_corners[map_name][1], pixel_corners[map_name][0], pixel_corners[map_name][1])
    data = an_api.get(f"/maps/{map_name}") or {}
    if "spawns" in data:
        s = dict(
                sorted(data["spawns"].items(), key=lambda item: item[1]["index"])
            )
        map_spawns = [world_to_pixel(i["x"], i["y"], sx, ox, sy, oy) for i in s.values()]
    elif map_name in spawns:
        s = spawns[map_name]
        map_spawns = [world_to_pixel(i[0], i[1], sx, ox, sy, oy) for i in s]
    else:
        return "File not found", 404

    # accounting for error
    scale = (abs(sx) + abs(sy)) / 2.0
    minR = [30 * scale, 4 * scale, 30 * scale]
    smallR = [40 * scale, 5 * scale, 40 * scale]
    largeR = [60 * scale, 15 * scale, 60 * scale]
    maxR = [90 * scale, 100 * scale, 90 * scale]
    w = [0.2, 0.2, 0.5]
    try:
        image_file = f"{map_name}.jpg"
        return render_template("spawns.html", name=map_name.title(), title=f"{map_name.title()} Spawns | Assassins\' Network", points=map_spawns, smallR=smallR, largeR=largeR, minR=minR, maxR=maxR, w=w, image_file=image_file)
    except FileNotFoundError:
        return "File not found", 404


@guides_bp.route("/routes/<map_name>")
def routes_page(map_name):
    sx, ox, sy, oy = compute_affine_from_corners(world_corners[map_name][0], world_corners[map_name][1], pixel_corners[map_name][0], pixel_corners[map_name][1])
    data = an_api.get(f"/maps/{map_name}")
    if not data or "routes" not in data:
        abort(404)
    checkpoints = data["routes"]
    map_routes = {
            j["name"]: [list(world_to_pixel(i["x"], i["y"], sx, ox, sy, oy)) + [i["isCheckpoint"]] for i in j["points"]] for j in checkpoints
            }

    checkpoint_radius = 3 * (abs(sx) + abs(sy)) / 2
    try:
        image_file = f"{map_name}.jpg"
        return render_template("routes.html", name=map_name.title(), title=f"{map_name.title()} Routes | Assassins\' Network", routes=map_routes, image_file=image_file, checkpoint_radius=checkpoint_radius)
    except FileNotFoundError:
        return "File not found", 404


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
