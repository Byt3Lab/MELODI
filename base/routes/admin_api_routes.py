from core.router import APIRouter

class AdminApiRoutes(APIRouter):
    def load(self):
        self.add_route("/", methods=["GET"])(self.status)
        
    def status(self):
        return self.render_json(data={"status": "Admin API is working!", "code": 200}, status_code=200)
