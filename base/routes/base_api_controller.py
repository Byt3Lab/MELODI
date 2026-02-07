from core.router import APIController
from base.services import UserService

class BaseController(APIController):
    def load(self):
        self.message = "BaseController initialized"
        user_service = UserService(module=self.module)
   
    async def login(self):
        req = self.router.get_request()  # Example of accessing session
        method = req.method
        user_has_auth = False

        if method == "POST":
            form = await req.form
            username = form.get("username")
            password = form.get("password")

            user_service = UserService(module=self.module)
            user_has_auth = await user_service.authenticate(username=username, password=password)
            
            if user_has_auth:
                from core.utils import jwt
                token = jwt.jwt_encode(user_has_auth, self.app.config.secret_key, algorithm="HS256")
                return self.router.render_json({"message": "Login successful", "token": token}, status_code=200)
        
        return await self.router.render_json({"message": "Login page"}, status_code=404)