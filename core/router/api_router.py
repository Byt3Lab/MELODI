from .router import Router
from flask import jsonify

class APIRouter(Router):
    def render_json(self, data: dict = {}, status_code: int = 200):
        try:
            data["status_code"] = status_code
            response = jsonify(data)
            response.status_code = status_code
            return response
        except:
            data = {
                "status_code":500,
                "message": "error serveur"
            }

            response = jsonify(data)
            response.status_code = 500
            return response