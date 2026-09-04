import secrets
from functools import wraps
from urllib.parse import urlencode

import requests
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pymongo import MongoClient

from .countries import DEFAULT_NATION, NATIONS
from .validation import (
    PLATFORM_CHOICES,
    check_invite,
    consume_invite,
    name_taken,
    new_player_doc,
    normalize_code,
    normalize_igns,
    normalize_platforms,
    refund_invite,
    validate_link,
    validate_name,
    validate_nation,
)

accounts_bp = Blueprint("accounts", __name__)

_client = MongoClient("mongodb://localhost:27017")
db = _client.public

DISCORD_AUTHORIZE_URL = "https://discord.com/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_USER_URL = "https://discord.com/api/users/@me"

# how long a signed oauth state token stays valid in s
STATE_MAX_AGE = 600


def _state_serializer():
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"], salt="discord-oauth-state"
    )


def current_player():
    """Return the logged-in player's doc, or None. Cached per request."""
    if "player" not in session:
        return None

    player = db.players.find_one({"name": session["player"]})

    if not player or player.get("revoked"):
        session.pop("player", None)
        return None

    return player


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_player():
            flash("Please sign in to continue.", "error")
            return redirect(url_for("accounts.login"))
        return view(*args, **kwargs)

    return wrapper


@accounts_bp.app_context_processor
def inject_current_user():
    """Expose the logged-in player to every template (nav bar, etc.)."""
    return {"current_user": current_player()}


@accounts_bp.route("/login")
def login():
    if current_player():
        return redirect(url_for("accounts.account"))
    return render_template("login.html", title="Sign In | Assassins' Network")


@accounts_bp.route("/auth/discord/start")
def discord_start():
    client_id = current_app.config.get("DISCORD_CLIENT_ID")
    if not client_id or not current_app.config.get("DISCORD_CLIENT_SECRET"):
        flash("Discord sign-in is not configured on this server.", "error")
        return redirect(url_for("accounts.login"))

    state = _state_serializer().dumps({"nonce": secrets.token_hex(8)})
    session["oauth_state"] = state

    params = {
        "client_id": client_id,
        "redirect_uri": current_app.config["DISCORD_REDIRECT_URI"],
        "response_type": "code",
        "scope": "identify",
        "state": state,
    }
    return redirect(f"{DISCORD_AUTHORIZE_URL}?{urlencode(params)}")


@accounts_bp.route("/auth/discord/callback")
def discord_callback():
    code = request.args.get("code")
    state = request.args.get("state")
    expected = session.pop("oauth_state", None)

    if not code or not state or state != expected:
        flash("Sign-in could not be verified. Please try again.", "error")
        return redirect(url_for("accounts.login"))

    try:
        _state_serializer().loads(state, max_age=STATE_MAX_AGE)
    except SignatureExpired:
        flash("Sign-in timed out. Please try again.", "error")
        return redirect(url_for("accounts.login"))
    except BadSignature:
        flash("Sign-in could not be verified. Please try again.", "error")
        return redirect(url_for("accounts.login"))

    try:
        token_res = requests.post(
            DISCORD_TOKEN_URL,
            data={
                "client_id": current_app.config["DISCORD_CLIENT_ID"],
                "client_secret": current_app.config["DISCORD_CLIENT_SECRET"],
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": current_app.config["DISCORD_REDIRECT_URI"],
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
    except requests.RequestException:
        flash("Could not reach Discord. Please try again.", "error")
        return redirect(url_for("accounts.login"))

    if not token_res.ok:
        flash("Discord rejected the sign-in. Please try again.", "error")
        return redirect(url_for("accounts.login"))

    access_token = token_res.json().get("access_token")
    if not access_token:
        flash("Discord returned no access token. Please try again.", "error")
        return redirect(url_for("accounts.login"))

    try:
        me_res = requests.get(
            DISCORD_USER_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
    except requests.RequestException:
        flash("Could not reach Discord. Please try again.", "error")
        return redirect(url_for("accounts.login"))

    if not me_res.ok:
        flash("Could not read your Discord profile. Please try again.", "error")
        return redirect(url_for("accounts.login"))

    profile = me_res.json()
    discord_id = profile.get("id")
    if not discord_id:
        flash("Discord returned no user id. Please try again.", "error")
        return redirect(url_for("accounts.login"))

    player = db.players.find_one({"discord_id": discord_id})

    if player:
        if player.get("revoked"):
            flash("This account has been revoked.", "error")
            return redirect(url_for("accounts.login"))

        session.pop("pending_discord", None)
        session["player"] = player["name"]
        flash(f"Welcome back, {player['name']}!", "success")
        return redirect(url_for("accounts.account"))

    session["pending_discord"] = {
        "id": discord_id,
        "name": profile.get("global_name") or profile.get("username") or "",
    }
    return redirect(url_for("accounts.register"))


@accounts_bp.route("/register", methods=["GET", "POST"])
def register():
    pending = session.get("pending_discord")
    if not pending:
        flash("Please sign in with Discord to register.", "error")
        return redirect(url_for("accounts.login"))

    if request.method == "GET":
        return render_template(
            "register.html",
            title="Register | Assassins' Network",
            nations=NATIONS,
            default_nation=DEFAULT_NATION,
            platform_choices=PLATFORM_CHOICES,
            form={"name": pending.get("name", "")},
            selected_platforms=[],
        )

    form = {
        "name": request.form.get("name", ""),
        "nation": request.form.get("nation", DEFAULT_NATION),
        "link": request.form.get("link", ""),
    }
    igns_raw = [i for i in request.form.getlist("ign") if i.strip()]
    selected_platforms = request.form.getlist("platforms")

    def rerender():
        return render_template(
            "register.html",
            title="Register | Assassins' Network",
            nations=NATIONS,
            default_nation=DEFAULT_NATION,
            platform_choices=PLATFORM_CHOICES,
            form={**form, "ign": igns_raw},
            selected_platforms=selected_platforms,
        )

    name, error = validate_name(form["name"])
    if error:
        flash(error, "error")
        return rerender()

    igns, error = normalize_igns(igns_raw)
    if error:
        flash(error, "error")
        return rerender()

    nation, error = validate_nation(form["nation"])
    if error:
        flash(error, "error")
        return rerender()

    platforms, error = normalize_platforms(selected_platforms)
    if error:
        flash(error, "error")
        return rerender()

    link, error = validate_link(form["link"])
    if error:
        flash(error, "error")
        return rerender()

    code = normalize_code(request.form.get("invite_code"))
    _, error = check_invite(db, code)
    if error:
        flash(error, "error")
        return rerender()

    # guard against dupe accounts
    existing = db.players.find_one({"discord_id": pending["id"]})
    if existing:
        if existing.get("revoked"):
            flash("This account has been revoked.", "error")
            return redirect(url_for("accounts.login"))
        session.pop("pending_discord", None)
        session["player"] = existing["name"]
        flash("An account is already linked to your Discord.", "success")
        return redirect(url_for("accounts.account"))

    if name_taken(db, name):
        flash("That name is already taken.", "error")
        return rerender()

    if not consume_invite(db, code, {"name": name, "discord_id": pending["id"]}):
        flash("This invite code has already been used.", "error")
        return rerender()

    player = new_player_doc(
        name=name,
        ign=igns,
        discord_id=pending["id"],
        link=link,
        nation=nation,
        platforms=platforms,
    )

    try:
        db.players.insert_one(player)
    except Exception:
        refund_invite(db, code)
        flash("Could not create the account, please try again.", "error")
        return rerender()

    session.pop("pending_discord", None)
    session["player"] = name
    flash("Your account has been created!", "success")
    return redirect(url_for("display_profile", name=name))


@accounts_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    player = current_player()

    if request.method == "POST":
        igns_raw = [i for i in request.form.getlist("ign") if i.strip()]
        selected_platforms = request.form.getlist("platforms")

        igns, error = normalize_igns(igns_raw)
        if not error:
            nation, error = validate_nation(request.form.get("nation", DEFAULT_NATION))
        if not error:
            platforms, error = normalize_platforms(selected_platforms)
        if not error:
            link, error = validate_link(request.form.get("link", ""))

        if error:
            flash(error, "error")
        else:
            db.players.update_one(
                {"name": player["name"]},
                {
                    "$set": {
                        "ign": igns,
                        "nation": nation,
                        "platforms": platforms,
                        "link": link,
                    }
                },
            )
            flash("Your profile has been updated.", "success")

        player = current_player()

    nations = dict(NATIONS)
    current_nation = player.get("nation", DEFAULT_NATION)
    if current_nation not in nations:
        nations[current_nation] = current_nation

    return render_template(
        "account.html",
        title="My Account | Assassins' Network",
        player=player,
        nations=nations,
        current_nation=current_nation,
        platform_choices=PLATFORM_CHOICES,
    )


@accounts_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("player", None)
    session.pop("pending_discord", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))
