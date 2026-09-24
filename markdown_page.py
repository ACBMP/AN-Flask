"""Shared rendering for the markdown-backed pages (guides, patch notes)."""

import markdown
from flask import render_template

# Base extensions every markdown page gets.
EXTENSIONS = ["toc", "attr_list", "tables"]
# Pages containing LaTeX also need arithmatex.
MATH_EXTENSIONS = EXTENSIONS + ["pymdownx.arithmatex"]

EXTENSION_CONFIGS = {"toc": {"permalink": True}}


def render_markdown(path, title, template="layout.html", extensions=EXTENSIONS):
    """Render a markdown file into ``template``, or 404 if it doesn't exist."""
    try:
        with open(path, "r") as f:
            md_content = f.read()
    except FileNotFoundError:
        return "File not found", 404
    content = markdown.markdown(
        md_content, extensions=extensions, extension_configs=EXTENSION_CONFIGS
    )
    return render_template(template, content=content, title=title)
