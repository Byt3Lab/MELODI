from core.base_router import BaseRouter

class APIRouter(BaseRouter):
    def render_json(self, data: dict, status_code: int = 200):
        from flask import jsonify
        response = jsonify(data)
        response.status_code = status_code
        return response