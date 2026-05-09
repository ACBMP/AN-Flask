import markdown
from flask import Blueprint, render_template
from .map_data import *
import requests

guides_bp = Blueprint("guides", __name__, url_prefix="/guides")

@guides_bp.route("/")
def overview_page():
    try:
        with open(f"guides/content/overview.md", "r") as f:
            md_content = f.read()
        configs = {"toc": {"permalink": True}}
        html_content = markdown.markdown(md_content, extensions=["toc", "attr_list", "tables"], extension_configs=configs)
        return render_template("layout.html", content=html_content, title=f"Guides Overview | Assassins\' Network")
    except FileNotFoundError:
        return "File not found", 404


@guides_bp.route("/spawns/<map_name>")
def spawns_page(map_name):
    sx, ox, sy, oy = compute_affine_from_corners(world_corners[map_name][0], world_corners[map_name][1], pixel_corners[map_name][0], pixel_corners[map_name][1])
    map_spawns = [world_to_pixel(i[0], i[1], sx, ox, sy, oy) for i in spawns[map_name]]

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
    r = requests.get(f"https://api.assassins.network/maps/{map_name}")
    data = r.json()
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
    try:
        with open(f"guides/content/{filename}.md", "r") as f:
            md_content = f.read()
        configs = {"toc": {"permalink": True}}
        html_content = markdown.markdown(md_content, extensions=["toc", "attr_list", "tables", "pymdownx.arithmatex"], extension_configs=configs)
        return render_template("layout.html", content=html_content, title=f"{filename.title()} Guide | Assassins\' Network")
    except FileNotFoundError:
        return "File not found", 404

@guides_bp.route("/modes")
def modes_page():
    try:
        with open(f"guides/content/modes.md", "r") as f:
            md_content = f.read()
        configs = {"toc": {"permalink": True}}
        html_content = markdown.markdown(md_content, extensions=["toc", "attr_list", "tables"], extension_configs=configs)
        return render_template("modes.html", content=html_content, title=f"Modes Overview | Assassins\' Network")
    except FileNotFoundError:
        return "File not found", 404
