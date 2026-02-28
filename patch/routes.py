import markdown
from flask import Blueprint, render_template

patch_bp = Blueprint("patch", __name__, url_prefix="/patch")

@patch_bp.route("/<filename>")
def render_md(filename):
    try:
        with open(f"patch/content/{filename}.md", "r") as f:
            md_content = f.read()
        configs = {"toc": {"permalink": True}}
        html_content = markdown.markdown(md_content, extensions=["toc", "attr_list", "tables"], extension_configs=configs)
        return render_template("patch.html", content=html_content, title=f"ACB 2.0 {filename.title()} | Assassins\' Network")
    except FileNotFoundError:
        return "File not found", 404

@patch_bp.route("/")
def patch_overview():
    try:
        with open(f"patch/content/summary.md", "r") as f:
            md_content = f.read()
        configs = {"toc": {"permalink": True}}
        html_content = markdown.markdown(md_content, extensions=["toc", "attr_list", "tables"], extension_configs=configs)
        return render_template("patch.html", content=html_content, title=f"ACB 2.0 Summary | Assassins\' Network")
    except FileNotFoundError:
        return "File not found", 404
