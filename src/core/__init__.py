from flask import Blueprint
from src.core.routes import core_routes

prefix_url_core = ""

core_bp = Blueprint("core", __name__, template_folder="templates", static_folder="static", static_url_path="/static")

core_bp.register_blueprint(core_routes)