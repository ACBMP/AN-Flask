"""Shared rendering for the markdown-backed pages (guides, patch notes)."""

import os

import markdown
from flask import render_template

import i18n

# Base extensions every markdown page gets.
EXTENSIONS = ["toc", "attr_list", "tables"]
# Pages containing LaTeX also need arithmatex.
MATH_EXTENSIONS = EXTENSIONS + ["pymdownx.arithmatex"]

EXTENSION_CONFIGS = {"toc": {"permalink": True}}


def translated_path(path):
    """Path to the active language's version of a content file.

    ``guides/content/overview.md`` is looked for at
    ``guides/content/<lang>/overview.md`` first, so a translated page can be
    dropped in beside the English one. Falls back to the English file, which
    means a half-translated set of guides still renders.
    """
    lang = i18n.current_language()
    if lang == i18n.DEFAULT_LANGUAGE:
        return path
    directory, name = os.path.split(path)
    localized = os.path.join(directory, lang, name)
    return localized if os.path.exists(localized) else path


def render_markdown(path, title, template="layout.html", extensions=EXTENSIONS):
    """Render a markdown file into ``template``, or 404 if it doesn't exist."""
    try:
        with open(translated_path(path), "r") as f:
            md_content = f.read()
    except FileNotFoundError:
        return "File not found", 404
    content = markdown.markdown(
        md_content, extensions=extensions, extension_configs=EXTENSION_CONFIGS
    )
    return render_template(template, content=content, title=title)
