"""Read-only Mongo access for the spectator pages.

Writes to `spectator_recordings`/`spectator_frames` are owned by AN-API's
ingest route (`POST /spectator/positions`, privilege-gated) — this module
only reads them, plus performs one narrow fallback write: closing out a
recording that's gone stale while a browser tab is still watching it (in case
the streaming machine crashed and never sent `match_ended`).

Uses its own `pymongo.MongoClient`, same escape hatch `accounts/routes.py`
uses, since a blueprint module can't import `flask_app.py`'s `mongo` without
a circular import.
"""

from datetime import datetime, timedelta

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient

_client = MongoClient("mongodb://localhost:27017")
db = _client.public

STALE_AFTER_SECONDS = 30


def _as_object_id(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


def get_live_recording(match_id):
    return db.spectator_recordings.find_one({"match_id": match_id, "ended_at": None})


def get_recording(recording_id):
    oid = _as_object_id(recording_id)
    if oid is None:
        return None
    return db.spectator_recordings.find_one({"_id": oid})


def list_live_recordings():
    return list(
        db.spectator_recordings.find({"ended_at": None}).sort("started_at", -1)
    )


def list_recent_recordings(limit=20):
    return list(
        db.spectator_recordings.find({"ended_at": {"$ne": None}})
        .sort("ended_at", -1)
        .limit(limit)
    )


def latest_frame(recording_id):
    return db.spectator_frames.find_one(
        {"recording_id": recording_id}, sort=[("seq", -1)]
    )


def frames_since(recording_id, since_seq):
    return list(
        db.spectator_frames.find(
            {"recording_id": recording_id, "seq": {"$gt": since_seq}}
        ).sort("seq", 1)
    )


def frames_for_replay(recording_id, rate_hz):
    """Downsample: ingest runs at ~20Hz, but a minimap doesn't need that many
    frames to read smoothly, so replay serves roughly every Nth frame by
    default (still full 20Hz fidelity in storage if ever needed)."""
    stride = max(1, round(20 / max(rate_hz, 1)))
    query = {"recording_id": recording_id}
    if stride > 1:
        # seq starts at 1, not 0 -- offset so frame 1 (and thus short
        # recordings shorter than one stride) is never filtered out entirely.
        query["$expr"] = {"$eq": [{"$mod": [{"$subtract": ["$seq", 1]}, stride]}, 0]}
    return list(db.spectator_frames.find(query).sort("seq", 1))


def is_stale(recording):
    last = latest_frame(recording["_id"])
    last_seen = recording["started_at"]
    if last is not None:
        last_seen = recording["started_at"] + timedelta(seconds=last["t"])
    return (datetime.utcnow() - last_seen) > timedelta(seconds=STALE_AFTER_SECONDS)


def finalize_if_stale(recording):
    """Fallback finalize for a still-open browser tab: AN-API's ingest route
    normally owns closing out a recording, but if the streaming machine
    crashed and never sent match_ended, nothing else will ever touch it."""
    if recording.get("ended_at") is not None:
        return recording
    if not is_stale(recording):
        return recording
    db.spectator_recordings.update_one(
        {"_id": recording["_id"]}, {"$set": {"ended_at": datetime.utcnow()}}
    )
    return get_recording(recording["_id"])


def is_participant(player_stats, viewer):
    """Case-insensitive: a missed match (false negative) would let an active
    player see the live feed, which is worse than a false positive."""
    viewer_names = {n.lower() for n in (viewer.get("ign") or []) if n}
    if viewer.get("name"):
        viewer_names.add(viewer["name"].lower())
    roster_names = {p["name"].lower() for p in player_stats if p.get("name")}
    return bool(viewer_names & roster_names)
