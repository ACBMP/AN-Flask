"""Site translations.

Strings are keyed by their English text, so a template reads as English even
before you look at the catalog, and anything without a translation falls back
to the English rather than showing a missing-key marker.

The active language lives on ``flask.g`` for the request and in a cookie
between them, so it survives for signed-out visitors too. Resolution order is:
an explicit choice (the cookie), then the browser's Accept-Language, then
English.
"""

from flask import g, has_request_context, request

from translations import CATALOGS

# Language code -> the name shown in the picker, in that language.
LANGUAGES = {"en": "English", "es": "Español"}

DEFAULT_LANGUAGE = "en"
COOKIE_NAME = "lang"
# Remember an explicit choice for a year.
COOKIE_MAX_AGE = 365 * 24 * 60 * 60


def is_supported(code):
    return code in LANGUAGES


def resolve_language():
    """The language this request should render in."""
    if not has_request_context():
        return DEFAULT_LANGUAGE
    chosen = request.cookies.get(COOKIE_NAME)
    if is_supported(chosen):
        return chosen
    best = request.accept_languages.best_match(LANGUAGES.keys())
    return best or DEFAULT_LANGUAGE


def current_language():
    if not has_request_context():
        return DEFAULT_LANGUAGE
    if not hasattr(g, "lang"):
        g.lang = resolve_language()
    return g.lang


def translate(text, **kwargs):
    """Translate ``text`` into the active language.

    Keyword arguments are substituted into the result, so a string with a
    placeholder can be reordered by the translation:
    ``_("%(mode)s Statistics", mode=...)``.
    """
    catalog = CATALOGS.get(current_language(), {})
    result = catalog.get(text, text)
    if kwargs:
        result = result % kwargs
    return result


def register(app):
    """Wire the translator into templates and set the language per request."""

    @app.before_request
    def _set_language():
        g.lang = resolve_language()

    app.jinja_env.globals["_"] = translate
    app.jinja_env.globals["current_language"] = current_language
    app.jinja_env.globals["LANGUAGES"] = LANGUAGES
