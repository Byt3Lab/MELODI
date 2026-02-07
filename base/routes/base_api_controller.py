from core.router import APIController
from base.services import UserService

class BaseAPIController(APIController):
    def load(self):
        self.user_service = UserService(module=self.module)
   
    async def login(self):
        req = self.router.get_request()  # Example of accessing session
        method = req.method
        user_has_auth = False

        if method == "POST":
            data = await req.json
            username = data.get("username")
            password = data.get("password")

            user_has_auth = await self.user_service.authenticate(username=username, password=password)
            
            if user_has_auth:
                token = self.router.jwt_encode(user_has_auth)
                return self.router.render_json({"message": "Login successful", "token": token}, status_code=200)
        
        return self.router.render_json({"message": "Login page"}, status_code=404)