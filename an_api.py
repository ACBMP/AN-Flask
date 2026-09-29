"""Thin client for AN-API, which runs alongside this site on the same host.

Calls go to ``AN_API_URL`` (loopback by default) rather than the public
hostname, so a page render doesn't make a round trip out through the reverse
proxy. ``get`` returns ``None`` instead of raising when the API is unreachable
or answers with an error, letting pages degrade rather than 500.
"""

import requests
from flask import current_app


def get(path, **params):
    base = current_app.config["AN_API_URL"]
    timeout = current_app.config["AN_API_TIMEOUT"]
    try:
        r = requests.get(f"{base}/{path.lstrip('/')}", params=params or None, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except (requests.RequestException, ValueError):
        current_app.logger.exception("AN-API request failed: %s", path)
        return None


def post(path, payload=None, token=None, params=None, timeout=None):
    """POST to AN-API as a player. Returns ``(status, json)``; status 0 if unreachable.

    Unlike ``get`` this reports errors, because the caller shows them.
    """
    base = current_app.config["AN_API_URL"]
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        r = requests.post(f"{base}/{path.lstrip('/')}", json=payload, params=params, headers=headers,
                          timeout=timeout or current_app.config["AN_API_TIMEOUT"])
    except requests.RequestException:
        current_app.logger.exception("AN-API request failed: %s", path)
        return 0, {"error": "The API could not be reached."}
    try:
        body = r.json()
    except ValueError:
        body = {"error": r.text[:200]}
    return r.status_code, body
