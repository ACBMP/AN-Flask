from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from accounts.routes import current_player, login_required

from . import store

spectator_bp = Blueprint("spectator", __name__, url_prefix="/spectator")


def _format_mmss(seconds):
    seconds = int(max(0, seconds or 0))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def _serialize_frame(frame):
    return {
        "seq": frame["seq"],
        "t": frame["t"],
        "players": frame.get("players", []),
        "vips": frame.get("vips", []),
        "abilities": frame.get("abilities", []),
        "kills": frame.get("kills", []),
        "timer_seconds_remaining": frame.get("timer_seconds_remaining"),
        "player_stats": frame.get("player_stats", []),
    }


@spectator_bp.route("/")
@login_required
def live_index():
    live = store.list_live_recordings()
    if len(live) == 1:
        return redirect(url_for("spectator.live_page", match_id=live[0]["match_id"]))
    recent = store.list_recent_recordings()
    return render_template(
        "spectator_index.html",
        live_matches=live,
        recent_recordings=recent,
        title="Spectator | Assassins' Network",
    )


@spectator_bp.route("/positions")
@login_required
def live_poll():
    match_id = request.args.get("match_id", "")
    since_seq = request.args.get("since_seq", 0, type=int)

    recording = store.get_live_recording(match_id)
    if recording is None:
        return jsonify({"live": False})

    recording = store.finalize_if_stale(recording)
    if recording is None or recording.get("ended_at") is not None:
        return jsonify({"live": False})

    latest = store.latest_frame(recording["_id"]) or {}
    if store.is_participant(latest.get("player_stats", []), current_player() or {}):
        return jsonify({"error": "locked"}), 403

    frames = store.frames_since(recording["_id"], since_seq)
    return jsonify({"live": True, "frames": [_serialize_frame(f) for f in frames]})


@spectator_bp.route("/<match_id>")
@login_required
def live_page(match_id):
    recording = store.get_live_recording(match_id)
    if recording is None:
        flash("There's no live match with that ID right now.", "error")
        return redirect(url_for("spectator.live_index"))

    recording = store.finalize_if_stale(recording)
    if recording is None or recording.get("ended_at") is not None:
        flash("That match has ended.", "error")
        return redirect(url_for("spectator.live_index"))

    frame = store.latest_frame(recording["_id"]) or {}
    player_stats = frame.get("player_stats", [])

    if store.is_participant(player_stats, current_player() or {}):
        return render_template(
            "spectator_locked.html",
            map=recording.get("map") or "Unknown",
            mode=recording.get("mode", "Unknown"),
            title="Spectator | Assassins' Network",
        )

    seed = {
        "seq": frame.get("seq", 0),
        "t": frame.get("t", 0),
        "players": frame.get("players", []),
        "vips": frame.get("vips", []),
        "abilities": frame.get("abilities", []),
        "kills": frame.get("kills", []),
        "timer_seconds_remaining": frame.get("timer_seconds_remaining"),
        "player_stats": player_stats,
    }
    return render_template(
        "spectator_live.html",
        match_id=match_id,
        map=recording.get("map") or "Unknown",
        map_key=recording.get("map_key") or "",
        mode=recording.get("mode", "Unknown"),
        seed=seed,
        title="Spectator | Assassins' Network",
    )


@spectator_bp.route("/replay/<recording_id>")
def replay_page(recording_id):
    recording = store.get_recording(recording_id)
    if recording is None:
        flash("That replay could not be found.", "error")
        return redirect(url_for("matches"))

    if recording.get("ended_at") and recording.get("started_at"):
        duration_s = (recording["ended_at"] - recording["started_at"]).total_seconds()
    else:
        last = store.latest_frame(recording["_id"])
        duration_s = last["t"] if last else 0

    return render_template(
        "spectator_replay.html",
        recording_id=str(recording["_id"]),
        map=recording.get("map") or "Unknown",
        map_key=recording.get("map_key") or "",
        mode=recording.get("mode", "Unknown"),
        duration_s=duration_s,
        duration_label=_format_mmss(duration_s),
        title="Spectator Replay | Assassins' Network",
    )


@spectator_bp.route("/replay/<recording_id>/frames")
def replay_frames(recording_id):
    recording = store.get_recording(recording_id)
    if recording is None:
        return jsonify({"error": "not found"}), 404

    rate_hz = request.args.get("rate_hz", 4, type=int)
    frames = store.frames_for_replay(recording["_id"], rate_hz)

    duration_s = None
    if recording.get("ended_at") and recording.get("started_at"):
        duration_s = (recording["ended_at"] - recording["started_at"]).total_seconds()

    return jsonify(
        {
            "recording_id": str(recording["_id"]),
            "duration_s": duration_s,
            "frames": [_serialize_frame(f) for f in frames],
        }
    )
