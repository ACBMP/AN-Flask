"""ACB 2.0 patch documentation pages."""

from flask import Blueprint

from markdown_page import render_markdown
from modes import title

patch_bp = Blueprint("patch", __name__, url_prefix="/patch")


@patch_bp.route("/")
def patch_overview():
    return render_markdown("patch/content/summary.md", title("ACB 2.0 Summary"))


@patch_bp.route("/<filename>")
def render_md(filename):
    return render_markdown(
        f"patch/content/{filename}.md", title(f"ACB 2.0 {filename.title()}")
    )
