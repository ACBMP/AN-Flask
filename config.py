import os


class Config:
    """Site configuration. Mirrors AN-API's ``app.config`` so both services on
    this host read the same environment variables."""

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/public")

    # Server-side sessions (Discord login, flash messages) need a signing key.
    # The dev default is intentionally insecure; set SECRET_KEY in production.
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-change-me")

    # Discord OAuth application credentials. The client secret must only ever
    # live here (server-side), never in a template. Mirrors AN-API's config.
    DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "")
    DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "")
    DISCORD_REDIRECT_URI = os.getenv(
        "DISCORD_REDIRECT_URI",
        "https://assassins.network/auth/discord/callback",
    )

    # AN-API runs on this same host (gunicorn on 127.0.0.1:8000), so server-side
    # calls go straight there instead of out to the public hostname and back in
    # through the reverse proxy. Set AN_API_URL when the API isn't reachable on
    # loopback - from a container, or a dev machine working against production.
    AN_API_URL = os.getenv("AN_API_URL", "http://127.0.0.1:8000").rstrip("/")
    # How long to wait on AN-API before giving up, in seconds.
    AN_API_TIMEOUT = float(os.getenv("AN_API_TIMEOUT", "5"))

    # Hard ceiling on a request body. Sits just above avatars.MAX_UPLOAD_BYTES
    # so an oversized profile picture gets the friendly message from there
    # rather than a bare 413; anything past this is refused unread.
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
