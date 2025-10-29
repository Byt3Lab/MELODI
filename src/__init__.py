from flask import Flask
from src.core import core_bp, prefix_url_core
from src.core.melodi import MelodiAppInit

melodi_app = MelodiAppInit()

apps = []

app = Flask(__name__)

app.register_blueprint(core_bp, url_prefix=prefix_url_core)