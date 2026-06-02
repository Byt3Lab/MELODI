from core.router import WebController
from base.services import UserService
from core.utils import path_exist, read_file, read_binary_file, join_paths

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
                    return await self.router.redirect("/admin")
        
        return await self.router.render_template("login.html")
    
    async def register(self):
        return await self.router.render_template("register.html")
    
    async def logout(self):
        self.router.delete_session("user_payload")
        return await self.router.redirect("/login")
    
    async def update(self):
        return await self.router.render_template("update.html")
    
    async def update_module(self, mod:str):
            
        return await self.router.render_template("update_module.html", mod=mod)
        
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
        return await self.router.redirect("/admin/base/settings/home_page")
    
    async def settings_home_page_clear(self):
        self.app.home_page_manager.clear()
        return await self.router.redirect("/admin/base/settings/home_page")

    async def admin_modules(self):
        modules = self.app.module_manager.list_modules()
        modules_len= len(modules)
        return await self.router.render_template("admin_modules.html",modules=modules, modules_len=modules_len)

    async def admin_add_module(self):
        return await self.router.render_template("admin_add_module.html")

    async def on_module(self,mod:str):
        await self.app.module_manager.on_module(mod)
        return await self.router.redirect("/admin/base/modules")

    async def off_module(self, mod:str):
        await self.app.module_manager.off_module(mod)
        return await self.router.redirect("/admin/base/modules")
    
    async def delete_module(self, mod:str):
        from base.services import ModuleService
        module_service = ModuleService(self.module)
        
        succes, message = await module_service.remove_module(mod)

        print(f"Delete module result: success={succes}, message='{message}'")

        return await self.router.redirect("/admin/base/modules")
    
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

    async def static_base_icons(self):
        req = self.router.get_request()
        name = req.args.get('name')
        fill = req.args.get('fill', '')
        size = req.args.get('size', '')

        if not name:
            return await self.router.abort(400, "Missing name parameter")
        
        import re
        
        icon_path = join_paths(self.app.config.PATH_DIR_RACINE, "base", "static", "icons", f"{name}.svg")
        
        if not path_exist(icon_path):
            return await self.router. abort(404, "Icon not found")
        
        content = read_file(icon_path, "r", "utf-8")
            
        if size:
            content = re.sub(r'(<svg[^>]*?)\sheight="[^"]*"', r'\1', content)
            content = re.sub(r'(<svg[^>]*?)\swidth="[^"]*"', r'\1', content)
            content = re.sub(r'(<svg)', f'\\1 width="{size}" height="{size}"', content)

        if fill:
            # On vérifie si la balise <svg> possède déjà un attribut fill
            # Cette regex cherche un 'fill=' UNIQUEMENT à l'intérieur des chevrons <svg ...>
            if re.search(r'<svg[^>]*\sfill="[^"]*"', content):
                # Si oui, on remplace uniquement celui du <svg>
                content = re.sub(r'(<svg[^>]*\s)fill="[^"]*"', f'\\1fill="{fill}"', content)
            else:
                # Si non, on l'injecte juste après le mot '<svg'
                content = re.sub(r'(<svg)', f'\\1 fill="{fill}"', content)
                
        # Some Material icons have internal fill/stroke that might need override or the SVG itself will take fill.
        return await self.router.make_response(content, 200, {"Content-Type": "image/svg+xml"})
    
    async def static_module_img(self):
        req = self.router.get_request()
        name = req.args.get('name')
        target = req.args.get('target', 'icon')
    
        if not name:
            return await self.router.abort(400, "Missing name parameter")
        
        if target in ["icon", "banner"]:
            img_path = join_paths(self.app.config.PATH_DIR_RACINE, "modules", name, "static", f"{target}.png")
        else:
            return await self.router.abort(400, "Invalid target parameter")
        
        if not path_exist(img_path):
            return await self.router.abort(404, f"{target.capitalize()} not found")
        
        content = read_binary_file(img_path)
                
        return await self.router.make_response(content, 200, {"Content-Type": "image/png"})
    
    async def static_org_img(self):
        req = self.router.get_request()
        name = req.args.get('name')
    
        if not name:
            return await self.router.abort(400, "Missing name parameter")
        
        img_path = join_paths(self.app.config.PATH_DIR_RACINE, "static", "orgs", f"{name}.png")

        if not path_exist(img_path):
            return await self.router.abort(404, "Image not found")
        
        content = read_binary_file(img_path)
                
        return await self.router.make_response(content, 200, {"Content-Type": "image/png"})