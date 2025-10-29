from flask import Blueprint, jsonify
from flask import render_template

core_routes = Blueprint("core_routes", __name__)

@core_routes.route("/", methods=["GET"])
def home():    
    return render_template("/home.html")

@core_routes.route("/login", methods=["GET"])
def signin():
    return render_template("/login.html")

@core_routes.route("/api", methods=["GET"])
def api():
    return jsonify({"message": "API is working!","status":200})
