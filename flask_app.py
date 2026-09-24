"""Application factory for the Assassins' Network website.

Structure mirrors AN-API, which runs on this same host: configuration lives in
``Config``, the Mongo handle in ``extensions``, and every page is a blueprint.
"""

import traceback

from flask import Flask, redirect
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from extensions import mongo
from filters import register_filters

from accounts.routes import accounts_bp
from guides.routes import guides_bp
from main.routes import main_bp
from maps.routes import maps_bp
from matches.routes import matches_bp
from patch.routes import patch_bp
from players.routes import players_bp
from rankings.routes import rankings_bp
from spectator.routes import spectator_bp
from status.routes import status_bp

BLUEPRINTS = [
    main_bp,
    rankings_bp,
    matches_bp,
    players_bp,
    maps_bp,
    status_bp,
    patch_bp,
    guides_bp,
    accounts_bp,
    spectator_bp,
]

HOME_URL = "https://assassins.network"


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.secret_key = app.config["SECRET_KEY"]

    mongo.init_app(app)
    register_filters(app)
    for bp in BLUEPRINTS:
        app.register_blueprint(bp)

    @app.errorhandler(Exception)
    def error_handler(e):
        # Anything unhandled - including a 404 - sends the visitor home rather
        # than showing a traceback or a bare error page.
        if not isinstance(e, HTTPException):
            traceback.print_exc()
        return redirect(HOME_URL, code=302)

    app.wsgi_app = ProxyFix(app.wsgi_app)
    return app


app = create_app()

# WE CAN'T RUN A LIVE APP IN DEBUG MODE!
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
