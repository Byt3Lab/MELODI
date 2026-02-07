from .router import Router
from quart import jsonify

class APIRouter(Router):
    def jwt_encode(self, payload, delay=3600):
        import jwt
        from datetime import datetime, timedelta, timezone
        
        now = datetime.now(timezone.utc)

        if isinstance(payload, dict):
            payload_copy = payload.copy()
            payload_copy["exp"] = now + timedelta(seconds=delay)
            payload_copy["iat"] = now

            return jwt.encode(payload = payload_copy, key=self.app.config.jwt_secret_key, algorithm="HS256")
        
        return None
    
    def jwt_decode(self, token):
        import jwt
        return jwt.decode(jwt=token, key=self.app.config.jwt_secret_key, algorithms=["HS256"])

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