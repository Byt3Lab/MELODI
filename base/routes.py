from __future__ import annotations

from flask import request, Request, g
from core import Router, APIRouter

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.request_context import RequestContext

class AdminRoutes(Router):
    def load (self):
        def get_theme(request:Request)->str:
            theme=request.cookies.get("theme")
            if theme is None:
                theme="light"
            return theme

        @self.before_request()
        def br():
            def sr(ctx:RequestContext):
                ctx.data["hello"] = "hello wordl"
                return ctx
            
            self.set_request_context(callback=sr)

        @self.before_request()
        def br2():
            ctx: RequestContext = self.get_request_context()
            print(ctx.data["hello"])

        @self.add_route("/", methods=["GET"])
        def home(): 
            self.app.event_listener.notify_event("hi")

            home_page = self.app.home_page_manager.render_home_page() 
          
            if home_page: 
                return home_page

            return self.render_template("home.html", theme=get_theme(request))

        @self.add_route("/login", methods=["GET"])
        def login():
            return self.render_template("login.html",hide_header=True,hide_footer=True, theme=get_theme(request))
        
        @self.add_route("/register", methods=["GET"])
        def register():
            return self.render_template("register.html",hide_header=True,hide_footer=True, theme=get_theme(request))
        
        @self.add_route("/logout", methods=["GET"])
        def logout():
            return self.render_template("logout.html",hide_header=True,hide_footer=True, theme=get_theme(request))

        @self.add_route("/admin", methods=["GET"])
        def ds():
            widgets=self.app.widget_manager.load_widgets_on()
            print(widgets)
            return self.render_template("admin_dashboard.html",widgets=widgets, theme=get_theme(request),hide_header=True,hide_footer=True)

        @self.add_route('/admin/dashboard', methods=['GET'])
        def admin_dashboard():
            return self.render_template('dashboard.html', theme=get_theme(request),hide_header=True,hide_footer=True)

        @self.add_route('/admin/users', methods=['GET'])
        def admin_users():
            return self.render_template("admin_users.html", theme=get_theme(request),hide_header=True,hide_footer=True)

        @self.add_route('/admin/profile', methods=['GET'])
        def profile():
            return self.render_template("profile.html", theme=get_theme(request),hide_header=True,hide_footer=True)

        @self.add_route('/admin/settings/widgets', methods=['GET'])
        def settings_widgets():
            return self.render_template("admin_widgets.html", theme=get_theme(request),hide_header=True,hide_footer=True)

        @self.add_route('/admin/settings/home_page', methods=['GET'])
        def settings_home_page():
            home_page_on = self.app.home_page_manager.home_page_on
            home_pages = self.app.home_page_manager.list_home_pages()
            home_pages_len = len(home_pages)
            return self.render_template("admin_home_page.html", theme=get_theme(request), home_pages=home_pages, home_pages_len=home_pages_len, home_page_on=home_page_on, hide_header=True,hide_footer=True)

        @self.add_route('/admin/settings/home_page/<path:home_page>/on', methods=['GET'])
        def settings_home_page_on(home_page):
            self.app.home_page_manager.set_home_page_on(name=home_page)
            return self.redirect("/admin/settings/home_page")
        
        @self.add_route('/admin/settings/home_page_clear', methods=['GET'])
        def settings_home_page_clear():
            self.app.home_page_manager.clear()
            return self.redirect("/admin/settings/home_page")

        @self.add_route('/admin/modules', methods=['GET'])
        def admin_modules():
            modules = self.app.module_manager.list_modules()
            modules_len= len(modules)
            return self.render_template("admin_modules.html", theme=get_theme(request), modules=modules, modules_len=modules_len, hide_header=True,hide_footer=True)

        @self.add_route('/admin/modules/<path:mod>/on', methods=['GET'])
        def on_module(mod:str):
            self.app.module_manager.on_module(mod)
            return self.redirect("/admin/modules")

        @self.add_route('/admin/modules/<path:mod>/off', methods=['GET'])
        def off_module(mod:str):
            self.app.module_manager.off_module(mod)
            return self.redirect("/admin/modules")
       
        @self.add_route('/admin/settings', methods=['GET'])
        def admin_settings():
            return self.render_template("admin_settings.html", theme=get_theme(request),hide_header=True,hide_footer=True)
        
        @self.add_route("/set_theme", methods=["GET"])
        def set_theme():
            theme=request.cookies.get("theme")

            if theme=="light":
                theme="nigth"
            else:
                theme="light"

            response = self.redirect("/")
            
            response.set_cookie("theme", theme)

            return response

class AdminApiRoutes(APIRouter):
    def load(self):
        @self.add_route("/", methods=["GET"])
        def status():
            return self.render_json(data={"status": "Admin API is working!", "code": 200}, status_code=200)
