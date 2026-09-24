from flask import Blueprint, abort, render_template

import an_api
from markdown_page import MATH_EXTENSIONS, render_markdown
from i18n import translate as _
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
    display = _(map_name.title())
    return render_template("spawns.html", name=display, title=title(_("%(name)s Spawns", name=display)), points=map_spawns, smallR=smallR, largeR=largeR, minR=minR, maxR=maxR, w=w, image_file=map_image(map_name))


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
    display = _(map_name.title())
    return render_template("routes.html", name=display, title=title(_("%(name)s Routes", name=display)), routes=map_routes, image_file=map_image(map_name), checkpoint_radius=checkpoint_radius)


@guides_bp.route("/<filename>")
def render_md(filename):
    return render_markdown(
        f"guides/content/{filename}.md",
        title(_("%(name)s Guide", name=_(filename.title()))),
        extensions=MATH_EXTENSIONS,
    )

@guides_bp.route("/modes")
def modes_page():
    # Rendered through the standard layout: this asked for a "modes.html" that
    # has never existed in the repo, so the page has only ever redirected away.
    # The mode comparison chart the content ends by promising still needs
    # building; it belongs in a template of its own once there's data for it.
    return render_markdown("guides/content/modes.md", title("Modes Overview"))
