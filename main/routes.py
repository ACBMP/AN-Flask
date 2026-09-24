"""Landing page and the static informational pages."""

import re

from flask import Blueprint, render_template

from extensions import mongo
from modes import title

main_bp = Blueprint("main", __name__)

PATCH_NOTES_FILE = "patch/content/patch-notes.md"
# Number of news entries shown on the landing page.
HOME_ENTRIES = 7


def latest_patch_notes(limit=5):
    """First (most recent) ``### version`` section of the patch notes, as a
    version plus up to ``limit`` bullet points. ``None`` if unavailable."""
    try:
        with open(PATCH_NOTES_FILE, "r") as f:
            content = f.read()
    except FileNotFoundError:
        return None
    match = re.search(r"^### ([^\n]+)\n(.*?)(?=\n### |\Z)", content, re.S | re.M)
    if not match:
        return None
    bullets = re.findall(r"^\*\s+(.+)$", match.group(2), re.M)
    return {"version": match.group(1).strip(), "notes": bullets[:limit]}


@main_bp.route("/")
@main_bp.route("/home")
def home():
    data = mongo.db.home.find().sort("_id", -1).limit(HOME_ENTRIES)
    return render_template("home.html", data=data, latest_patch=latest_patch_notes())


@main_bp.route("/elo")
def elo():
    return render_template("elo.html", title=title("Elo Explained"))


@main_bp.route("/about")
def about():
    return render_template("about.html", title="About Assassins' Network")


@main_bp.route("/donate")
def donate():
    return render_template("donate.html", title=title("Donate"))


@main_bp.route("/spawnguesser")
def train():
    return render_template("train.html")


@main_bp.route("/418")
def teapot():
    return render_template("418.html")
