"""Service status page and the UDP reachability probe the launcher calls."""

from flask import Blueprint, jsonify, render_template, request

from modes import title

status_bp = Blueprint("status", __name__)

MIN_PORT = 1
MAX_PORT = 65535


# The checks pull in psutil and shell out to nmap, so they're imported inside
# the views: a missing optional dependency takes out this page, not the site.
@status_bp.route("/status")
def status_page():
    from . import status

    return render_template("status.html", data=status.main(), title=title("Status Page"))


@status_bp.route("/check_udp_route", methods=["GET"])
def check_udp_route():
    from .status import check_udp

    try:
        port = int(request.args.get("port"))
        if not MIN_PORT <= port <= MAX_PORT:
            raise ValueError("port out of range")
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing 'port' parameter"}), 400

    requester_ip = request.remote_addr
    return jsonify(
        {
            "checked_ip": requester_ip,
            "port": port,
            "udp_reachable": check_udp(requester_ip, port),
        }
    )
