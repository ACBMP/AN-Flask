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
    # calls can skip the public hostname and the round trip back in through the
    # reverse proxy by setting AN_API_URL=http://127.0.0.1:8000. The default
    # stays on the public URL so this works unchanged from a container or from a
    # dev machine.
    AN_API_URL = os.getenv("AN_API_URL", "https://api.assassins.network").rstrip("/")
    # How long to wait on AN-API before giving up, in seconds.
    AN_API_TIMEOUT = float(os.getenv("AN_API_TIMEOUT", "5"))
