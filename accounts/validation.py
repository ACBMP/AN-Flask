import re
import secrets
from datetime import datetime, timedelta

from .countries import DEFAULT_NATION, NATIONS

NAME_RE = re.compile(r"^[A-Za-z0-9_.\- ]{2,24}$")

MAX_IGNS = 5
MAX_IGN_LENGTH = 32

# Existing player docs contain messy platform values ("PC ", "ps4", "PS4;",
# "XBOX"). New registrations are normalised to these canonical spellings.
_PLATFORM_ALIASES = {
    "PC": "PC",
    "PS3": "PS3",
    "PLAYSTATION 3": "PS3",
    "PS4": "PS4",
    "PLAYSTATION 4": "PS4",
    "XBOX": "Xbox",
}

PLATFORM_CHOICES = ["PC", "PS3", "PS4", "Xbox"]

MAX_LINK_LENGTH = 200


def validate_name(name):
    """Return ``(name, error)`` for a proposed account name."""
    if not isinstance(name, str):
        return None, "Account name is required"

    cleaned = " ".join(name.split())

    if not cleaned:
        return None, "Account name is required"

    if not NAME_RE.match(cleaned):
        return None, (
            "Account names must be 2-24 characters, using letters, numbers, "
            "spaces, and . _ - only"
        )

    return cleaned, None


def normalize_igns(raw):
    """Return ``(igns, error)``. Accepts a single string or a list."""
    if isinstance(raw, str):
        raw = [raw]

    if not isinstance(raw, list):
        return [], "In-game name is required"

    out = []
    for entry in raw:
        if not isinstance(entry, str):
            return [], "Invalid in-game name"

        cleaned = entry.strip()
        if not cleaned:
            continue

        if len(cleaned) > MAX_IGN_LENGTH:
            return [], f"In-game names must be {MAX_IGN_LENGTH} characters or fewer"

        if cleaned not in out:
            out.append(cleaned)

    if not out:
        return [], "In-game name is required"

    if len(out) > MAX_IGNS:
        return [], f"At most {MAX_IGNS} in-game names"

    return out, None


def normalize_platforms(raw):
    """Return ``(platforms, error)``; unknown platforms are rejected."""
    if raw is None:
        return [], "Select at least one platform"

    if isinstance(raw, str):
        raw = [raw]

    if not isinstance(raw, list) or not raw:
        return [], "Select at least one platform"

    out = []
    for entry in raw:
        if not isinstance(entry, str):
            return [], "Invalid platform"

        key = re.sub(r"[^A-Za-z0-9 ]", "", entry).strip().upper()
        canonical = _PLATFORM_ALIASES.get(key)

        if not canonical:
            return [], f"Unsupported platform: {entry}"

        if canonical not in out:
            out.append(canonical)

    return out, None


def validate_nation(raw):
    """Return ``(code, error)``.

    Accepts a value iff it's a key in :data:`NATIONS` (the gosquared/flags set).
    Two-letter codes are matched case-insensitively / upper-cased to match how
    they're stored; the underscore specials are matched verbatim.
    """
    if not isinstance(raw, str):
        return None, "Select a country"

    cleaned = raw.strip()
    if not cleaned:
        return None, "Select a country"

    if cleaned in NATIONS:
        return cleaned, None

    upper = cleaned.upper()
    if upper in NATIONS:
        return upper, None

    return None, "Select a country"


def validate_link(raw):
    """Return ``(link, error)``. Link is optional; empty is fine."""
    if raw is None:
        return "", None

    if not isinstance(raw, str):
        return None, "Invalid link"

    return raw.strip()[:MAX_LINK_LENGTH], None


def name_taken(db, name):
    """Case-insensitive check so "Try" and "try" can't both exist."""
    return bool(
        db.players.find_one(
            {"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}}
        )
    )


NEVER = datetime(9999, 1, 1)

_CODE_RE = re.compile(r"^[A-Z0-9]{4}-[A-Z0-9]{4}$")


def normalize_code(raw):
    """Accept sloppy user input: whitespace, lowercase, missing dash."""
    if not isinstance(raw, str):
        return ""

    cleaned = re.sub(r"[^A-Za-z0-9]", "", raw).upper()

    if len(cleaned) != 8:
        return cleaned

    return f"{cleaned[:4]}-{cleaned[4:]}"


def check_invite(db, code):
    """Validate a code without consuming it.

    Returns ``(invite, error)``; exactly one is non-None.
    """
    if not code:
        return None, "An invite code is required"

    if not _CODE_RE.match(code):
        return None, "That doesn't look like a valid invite code"

    invite = db.invites.find_one({"code": code})

    if not invite:
        return None, "Unknown invite code"

    if invite.get("disabled"):
        return None, "This invite code has been revoked"

    if invite.get("expires_at", NEVER) <= datetime.utcnow():
        return None, "This invite code has expired"

    if invite.get("uses_remaining", 0) <= 0:
        return None, "This invite code has already been used"

    return invite, None


def consume_invite(db, code, used_by):
    """Atomically burn one use of `code`.

    The filter re-checks every condition so two simultaneous registrations
    can't both claim the last use. Returns True if a use was claimed.
    """
    result = db.invites.update_one(
        {
            "code": code,
            "disabled": False,
            "uses_remaining": {"$gt": 0},
            "expires_at": {"$gt": datetime.utcnow()},
        },
        {
            "$inc": {"uses_remaining": -1, "uses": 1},
            "$push": {"used_by": {**used_by, "at": datetime.utcnow()}},
        },
    )

    return result.matched_count == 1


def refund_invite(db, code):
    """Give back a use after a failed registration. Best-effort."""
    db.invites.update_one({"code": code}, {"$inc": {"uses_remaining": 1, "uses": -1}})


STARTING_MMR = 800
MODE_PREFIXES = ("e", "mh", "aar", "aad", "do", "dm", "asb")
_FFA_MODES = ("dm", "asb")
_OBJECTIVE_MODES = ("aar", "aad")
DEFAULT_PRIVILEGE = 10


def new_player_doc(
    name, ign, discord_id, link="", nation="", platforms=None, api_key=None
):
    """Build a complete, zeroed player document.

    Mirrors ``AN-API/src/app/routes/util.new_player_doc`` so website-created and
    launcher-created accounts can't drift apart as modes are added.
    """
    now = datetime.utcnow()

    doc = {
        "name": name,
        "ign": ign,
        "link": link,
        "nation": nation or DEFAULT_NATION,
        "platforms": platforms or [],
        "badges": [],
        "discord_id": discord_id,
        "hidden": False,
        "api_key": api_key or secrets.token_hex(32),
        "privilege": DEFAULT_PRIVILEGE,
        "revoked": False,
        "created_at": now,
    }

    for mode in MODE_PREFIXES:
        doc[f"{mode}mmr"] = STARTING_MMR
        doc[f"{mode}history"] = {"dates": [now], "mmrs": [STARTING_MMR]}
        doc[f"{mode}rank"] = 0
        doc[f"{mode}rankchange"] = 0

        games = {"total": 0, "won": 0, "lost": 0}
        if mode in _FFA_MODES:
            games |= {"podium": 0, "finishes": 0}
        doc[f"{mode}games"] = games

        if mode in _OBJECTIVE_MODES:
            doc[f"{mode}stats"] = {
                "totalscore": 0,
                "kills": 0,
                "deaths": 0,
                "scored": 0,
                "conceded": 0,
            }
        else:
            doc[f"{mode}stats"] = {
                "totalscore": 0,
                "highscore": 0,
                "kills": 0,
                "deaths": 0,
            }

    return doc
