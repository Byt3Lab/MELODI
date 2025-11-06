from core.router import APIRouter

class AdminApiRoutes(APIRouter):
    def load(self):
        @self.add_route("/", methods=["GET"])
        def status():
            return self.render_json(data={"status": "Admin API is working!", "code": 200}, status_code=200)