from core.router import WebRouter, RequestContext

class BaseRoutes(WebRouter):
    def load (self):
        self.before_request()(self.br)
        self.before_request()(self.br2)
        self.add_route("/", methods=["GET"])(self.home)
        self.add_route("/login", methods=["GET"])(self.login)
        self.add_route("/register", methods=["GET"])(self.register)
        self.add_route("/logout", methods=["GET"])(self.logout)
        self.add_route("/admin", methods=["GET"])(self.admin_dashboard)
        self.add_route('/admin/users', methods=['GET'])(self.admin_users)
        self.add_route('/admin/profile', methods=['GET'])(self.profile)
        self.add_route('/admin/settings/widgets', methods=['GET'])(self.settings_widgets)
        self.add_route('/admin/settings/home_page', methods=['GET'])(self.settings_home_page)
        self.add_route('/admin/settings/home_page/<path:home_page>/on', methods=['GET'])(self.settings_home_page_on)
        self.add_route('/admin/settings/home_page_clear', methods=['GET'])(self.settings_home_page_clear)
        self.add_route('/admin/modules', methods=['GET'])(self.admin_modules)
        self.add_route('/admin/modules/<path:mod>/off', methods=['GET'])(self.off_module)
        self.add_route('/admin/settings', methods=['GET'])(self.admin_settings)
        self.add_route('/admin/modules/<path:mod>/on', methods=['GET'])(self.on_module)

    def br(self):
        def sr(ctx:RequestContext):
            ctx.data["hello"] = "hello wordl"
            return ctx
        
        self.set_request_context(callback=sr)

    def br2(self):
        ctx = self.get_request_context()
        print(ctx.data["hello"])

    def login(self):
        return self.render_template("login.html")
    
    def register(self):
        return self.render_template("register.html")
    
    def logout(self):
        return self.render_template("logout.html")

    def admin_dashboard(self):
        widgets=self.app.widget_manager.list_widgets()
        return self.render_template("admin_dashboard.html",widgets=widgets)

    def admin_users(self):
        return self.render_template("admin_users.html")

    def profile(self):
        return self.render_template("profile.html")

    def settings_widgets(self):
        widgets = self.app.widget_manager.list_widgets()
        return self.render_template("admin_widgets.html", widgets=widgets)

    def settings_home_page(self):
            home_page_on = self.app.home_page_manager.home_page_on
            home_pages = self.app.home_page_manager.list_home_pages()
            home_pages_len = len(home_pages)
            return self.render_template("admin_home_page.html", home_pages=home_pages, home_pages_len=home_pages_len, home_page_on=home_page_on)

    def settings_home_page_on(self, home_page):
        self.app.home_page_manager.set_home_page_on(name=home_page)
        return self.redirect("/admin/settings/home_page")
    
    def settings_home_page_clear(self):
        self.app.home_page_manager.clear()
        return self.redirect("/admin/settings/home_page")

    def admin_modules(self):
        modules = self.app.module_manager.list_modules()
        modules_len= len(modules)
        return self.render_template("admin_modules.html",modules=modules, modules_len=modules_len)

    def on_module(self,mod:str):
        self.app.module_manager.on_module(mod)
        return self.redirect("/admin/modules")

    def off_module(self, mod:str):
        self.app.module_manager.off_module(mod)
        return self.redirect("/admin/modules")
    

    def admin_settings(self):
        return self.render_template("admin_settings.html")

    def home(self): 
        self.app.event_listener.notify_event("hi")

        home_page = self.app.home_page_manager.render_home_page() 
        
        if home_page: 
            return home_page

        return self.render_template("home.html")
