from core.router import WebController
from base.services import UserService

class BaseController(WebController):
    def load(self):
        self.message = "BaseController initialized"
        self.user_service = UserService(module=self.module)

    async def login(self):
        req = self.router.get_request()  # Example of accessing session
        method = req.method
        user_has_auth = False

        if method == "POST":
            form = await req.form
            username = form.get("username")
            password = form.get("password")

            user_has_auth = await self.user_service.authenticate(username=username, password=password)
            
            if user_has_auth:
                import json
                if self.router.set_session("user_payload", json.dumps(user_has_auth)):
                    return self.router.redirect("/admin")
        
        return await self.router.render_template("login.html")
    
    async def register(self):
        return await self.router.render_template("register.html")
    
    async def logout(self):
        self.router.delete_session("user_payload")
        return self.router.redirect("/login")
    
    async def update(self):
        return await self.router.render_template("update.html")
    
    async def logs(self):
        return await self.router.render_template("admin_logs.html")

    async def admin_dashboard(self):
        return await self.router.render_template("admin_dashboard.html")

    async def admin_users(self):
        return await self.router.render_template("admin_users.html")

    async def profile(self):
        return await self.router.render_template("profile.html")

    async def settings_widgets(self):
        return await self.router.render_template("admin_widgets.html")

    async def settings_home_page(self):
            home_page_on = self.app.home_page_manager.home_page_on
            home_pages = self.app.home_page_manager.list_home_pages()
            home_pages_len = len(home_pages)
            return await self.router.render_template("admin_home_page.html", home_pages=home_pages, home_pages_len=home_pages_len, home_page_on=home_page_on)

    async def settings_home_page_on(self, home_page):
        self.app.home_page_manager.on(home_page)
        return self.router.redirect("/admin/settings/home_page")
    
    async def settings_home_page_clear(self):
        self.app.home_page_manager.clear()
        return self.router.redirect("/admin/settings/home_page")

    async def admin_modules(self):
        modules = self.app.module_manager.list_modules()
        modules_len= len(modules)
        return await self.router.render_template("admin_modules.html",modules=modules, modules_len=modules_len)

    async def on_module(self,mod:str):
        await self.app.module_manager.on_module(mod)
        return self.router.redirect("/admin/modules")

    async def off_module(self, mod:str):
        await self.app.module_manager.off_module(mod)
        return self.router.redirect("/admin/modules")
    
    async def admin_settings(self):
        return await self.router.render_template("admin_settings.html")

    async def home(self): 
        home_page = await self.app.home_page_manager.render_home_page() 

        if home_page: 
            return home_page

        return await self.router.render_template("home.html")

    async def home_welcome(self):
        return await self.router.render_template("home_welcome.html")
    
    async def install(self):
        return await self.router.render_template("install/install.html")

    async def notifications(self):
        return await self.router.render_template("admin_notifications.html")