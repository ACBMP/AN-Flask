"""Match history listing and per-match detail, plus corrections for admins.

Players with privilege 5 or better can correct or undo a match. The work is
done by AN-API (which runs the Scripts' rating code), called with the admin's
own API key so the API's privilege check applies.
"""

import secrets

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

import an_api
from accounts.routes import current_player
from extensions import mongo
from i18n import translate as _
from modes import is_aa_mode, title

matches_bp = Blueprint("matches", __name__)

PAGE_SIZE = 20
# admins: lower privilege numbers are more powerful
EDIT_PRIVILEGE = 5
FFA_MODES = ("Deathmatch", "Assassinate brotherhood")
# corrections replay later matches; give the API longer than a page render
EDIT_TIMEOUT = 40


def can_edit_matches():
    player = current_player()
    return player is not None and player.get("privilege", 99) <= EDIT_PRIVILEGE


def csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = session["csrf_token"] = secrets.token_urlsafe(32)
    return token


def check_csrf():
    sent = request.form.get("csrf_token", "")
    if not sent or not secrets.compare_digest(sent, session.get("csrf_token", "")):
        abort(400)


@matches_bp.app_context_processor
def inject_match_admin():
    return {"can_edit_matches": can_edit_matches, "csrf_token": csrf_token}


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


def _find(match_id):
    try:
        return mongo.db.matches.find_one({"_id": ObjectId(match_id)})
    except InvalidId:
        return None


@matches_bp.route("/match/<match_id>")
def match_detail(match_id):
    entry = _find(match_id)
    if not entry:
        return redirect("/matches", code=302)
    return render_template("match_detail.html", entry=entry, title=title("Match Details"))


# --- corrections -----------------------------------------------------------------

def _admin_token():
    """The signed-in admin's API key (minted like AN-API does if they never had one)."""
    player = current_player()
    if player is None or player.get("privilege", 99) > EDIT_PRIVILEGE:
        abort(403)
    if not player.get("api_key"):
        player["api_key"] = secrets.token_hex(32)
        mongo.db.players.update_one({"_id": player["_id"], "api_key": {"$exists": False}},
                                    {"$set": {"api_key": player["api_key"]}})
        player = mongo.db.players.find_one({"_id": player["_id"]})
    return player["api_key"]


def _report(status, body, success):
    """Flash the API's answer; returns True when the change is done."""
    if status == 200:
        replayed = (body.get("result") or {}).get("replayed", 0)
        flash(success + " " + _("%(n)s later match(es) recalculated.", n=replayed), "success")
        return True
    if status == 202:
        flash(_("The ratings are being recalculated; this can take a minute. Refresh the page to see the result."),
              "info")
        return True
    flash(_("Nothing was changed: %(error)s", error=body.get("error", _("unknown error"))), "error")
    return False


def _stat(value):
    value = (value or "").strip()
    if not value.lstrip("-").isdigit():
        raise ValueError(value)
    return int(value)


def _rows(prefix, count, aa):
    """Player rows from the correction form (blank names are skipped)."""
    rows = []
    for i in range(count):
        name = request.form.get(f"{prefix}-{i}-player", "").strip()
        if not name:
            continue
        row = {"player": name}
        fields = ("score", "kills", "deaths") + (("scored",) if aa else ())
        for field in fields:
            try:
                row[field] = _stat(request.form.get(f"{prefix}-{i}-{field}"))
            except ValueError:
                raise ValueError(_("%(player)s: %(field)s must be a whole number", player=name, field=_(field)))
        rows.append(row)
    return rows


def _changes(entry):
    """Only what the form actually changed."""
    aa = is_aa_mode(entry.get("mode"))
    keys = ("player", "score", "kills", "deaths") + (("scored",) if aa else ())
    changes = {}
    if entry.get("mode") in FFA_MODES:
        rows = _rows("p", len(entry.get("players") or []), False)
        if rows != [{k: p.get(k) for k in keys} for p in entry.get("players") or []]:
            changes["players"] = rows
    else:
        for team in ("team1", "team2"):
            rows = _rows(team, len(entry.get(team, [])), aa)
            if rows != [{k: p.get(k) for k in keys} for p in entry.get(team, [])]:
                changes[team] = rows
        outcome = request.form.get("outcome", "")
        if outcome.isdigit() and int(outcome) != entry.get("outcome"):
            changes["outcome"] = int(outcome)
    for field in ("map", "host"):
        value = request.form.get(field, "").strip()
        if value != (entry.get(field) or ""):
            changes[field] = value
    return changes


@matches_bp.route("/match/<match_id>/correct", methods=["GET", "POST"])
def correct_match(match_id):
    if not can_edit_matches():
        abort(403)
    entry = _find(match_id)
    if not entry:
        flash(_("That match no longer exists."), "error")
        return redirect("/matches", code=302)
    if request.method == "POST":
        check_csrf()
        try:
            changes = _changes(entry)
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("match_correct.html", entry=entry, form=request.form,
                                   title=title("Correct Match"))
        if not changes:
            flash(_("Nothing to change."), "info")
            return redirect(url_for("matches.match_detail", match_id=match_id))
        status, body = an_api.post(f"matches/{match_id}/edit", changes, token=_admin_token(), timeout=EDIT_TIMEOUT)
        if _report(status, body, _("Match corrected.")):
            return redirect(url_for("matches.match_detail", match_id=match_id))
        return render_template("match_correct.html", entry=entry, form=request.form, title=title("Correct Match"))
    return render_template("match_correct.html", entry=entry, form=None, title=title("Correct Match"))


@matches_bp.route("/match/<match_id>/undo", methods=["POST"])
def undo_match(match_id):
    if not can_edit_matches():
        abort(403)
    check_csrf()
    status, body = an_api.post(f"matches/{match_id}/undo", token=_admin_token(), timeout=EDIT_TIMEOUT)
    if _report(status, body, _("Match undone.")):
        return redirect("/matches", code=302)
    return redirect(url_for("matches.match_detail", match_id=match_id))
