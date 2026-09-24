"""Match history listing and per-match detail."""

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, redirect, render_template

from extensions import mongo
from modes import title

matches_bp = Blueprint("matches", __name__)

PAGE_SIZE = 20


def _page(page_no):
    data = mongo.db.matches.find().sort("_id", -1).skip(page_no * PAGE_SIZE).limit(PAGE_SIZE)
    return render_template(
        "matches.html", data=data, page_no=page_no, title=title("Match History")
    )


@matches_bp.route("/matches")
def matches():
    return _page(0)


@matches_bp.route("/matches/<page>")
def paged_matches(page):
    try:
        page_no = max(0, int(page))
    except ValueError:
        page_no = 0
    return _page(page_no)


@matches_bp.route("/match/<match_id>")
def match_detail(match_id):
    try:
        entry = mongo.db.matches.find_one({"_id": ObjectId(match_id)})
    except InvalidId:
        entry = None
    if not entry:
        return redirect("/matches", code=302)
    return render_template("match_detail.html", entry=entry, title=title("Match Details"))
