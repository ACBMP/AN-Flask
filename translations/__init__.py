"""Translation catalogs, keyed by language code.

Each catalog maps an English source string to its translation. A string that
isn't in the catalog falls back to the English, so a partial catalog is fine
and adding a language is just adding a module here.
"""

from .es import CATALOG as ES

CATALOGS = {"es": ES}
