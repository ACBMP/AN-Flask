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
