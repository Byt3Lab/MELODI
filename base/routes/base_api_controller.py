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
            
            print(self.router.get_session("user_id"))
            if user_has_auth:
                r = self.router.set_session("user_id", "True")
                print("Session set:", r)
                return self.router.redirect("/admin")
        
        return await self.router.render_template("login.html")