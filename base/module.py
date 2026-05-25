from quart import Response
from core.module import ApplicationModule
from core.router import WebRouter, APIRouter
from core.utils import join_paths
import json
class Base(ApplicationModule):
    async def load(self):
        print(f"DEBUG: Base module load() called on instance {id(self)}")
        self.init_load()
        from base.routes import BaseRoutes, BaseApiRoutes

        routes = BaseRoutes(name="base", app=self.app, module=self)
        api_routes = BaseApiRoutes(name="base", app=self.app, module=self)

        await routes.load()
        api_routes.load()

        self.add_router(routes) 
        self.add_api_router(api_routes) 
        
        super().load()
    
    async def load_installer(self):
        print(f"DEBUG: Base module load_installer() called on instance {id(self)}")
        self.init_load()

        from base.routes import BaseRoutes, BaseApiRoutes

        routes = BaseRoutes(name="base", app=self.app, module=self)
        api_routes = BaseApiRoutes(name="base", app=self.app, module=self)

        routes.load_installer()
        api_routes.load_installer()

        self.add_router(routes) 
        self.add_api_router(api_routes)

    def init_load(self):
        self.init_translation("fr")
        self.add_404_not_found()
        self.add_widgets()
        self.add_navigation()
        self.add_ws_function()
        self.add_middlewares()
        # ------------------------------------------------------------------
        # Context Processor: User info available in all templates
        # ------------------------------------------------------------------

        self.add_context_processor(self.inject_user_context)

    async def inject_user_context(self):
        """
        Injecte dans tous les templates Jinja2 :
            - current_user      : dict complet du payload utilisateur (ou None)
            - is_authenticated  : bool — True si une session utilisateur est active
            - user_role         : str  — rôle de l'utilisateur (ex. 'admin', 'user') ou None
            - user_permissions  : list — liste des permissions de l'utilisateur ou []
        """
        from quart import session
        raw = session.get("user_payload")
        if raw:
            try:
                user = json.loads(raw) if isinstance(raw, str) else raw
            except (ValueError, TypeError):
                user = None
        else:
            user = None

        return {
            "current_user":          user,
            "user_is_authenticated":  user is not None,
            "user_role":             user.get("role") if user else None,
            "user_is_sudo":             user.get("is_sudo") if user else None,
            "user_permissions":      user.get("permissions", []) if user else [],
        }

    def add_404_not_found(self):
        PATH_DIR_BASE_MODULE = self.app.config.PATH_DIR_BASE_MODULE
        self.app.config.path_template_404_not_found = join_paths(PATH_DIR_BASE_MODULE, 'templates', 'base', '404.html')
        
    def add_widgets(self):
        self.register_dashboard_widget(
            title="Base Widget",
            component=self.render_widget_template("dashboard"),
            dimensions={"w": 4, "h": 2},
            priority=10
        )

        # StatusBar Zone (Top Admin Header)
        self.register_statusbar_item(component=self.render_widget_template("ws_status"), priority=100)

    def add_navigation(self):
        # ------------------------------------------------------------------
        # Contribution Registry: Layout Injection
        # ------------------------------------------------------------------
        
        # Dashboard item
        self.register_navigation(label="Tableau de bord", icon="name=dashboard&fill=white", url="/admin", priority=100)
        
        # Gestion with Sub-menus
        self.register_navigation(
            label="Gestion",
            icon="name=admin_panel_settings&fill=white",
            priority=90,
            children=[
                {"label": "Utilisateurs", "icon": "name=people&fill=white", "url": "/admin/base/users", "children": [
                    {"label": "Tous les utilisateurs", "icon": "name=people&fill=white", "url": "/admin/base/users"},
                    {"label": "Ajouter un utilisateur", "icon": "name=person_add&fill=white", "url": "/admin/base/users/add"},
                    {"label": "Rôles et permissions", "icon": "name=security&fill=white", "url": "/admin/base/users/roles"},
                    {"label": "Sessions actives", "icon": "name=devices&fill=white", "url": "/admin/base/users/sessions"},
                    {"label": "Logs d'activité", "icon": "name=history&fill=white", "url": "/admin/base/users/activity-logs"},
                ]},
                {"label": "Modules", "icon": "name=extension&fill=white", "url": "/admin/base/modules", "children": [
                    {"label": "Tous les modules", "icon": "name=extension&fill=white", "url": "/admin/base/modules"},
                    {"label": "Ajouter un module", "icon": "name=add&fill=white", "url": "/admin/base/modules/add"},
                ]},
                {"label": "Paramètres globaux", "icon": "name=tune&fill=white", "url": "/admin/base/settings"},
                {"label": "Mise à jour", "icon": "name=update&fill=white", "url": "/admin/base/update"}
            ]
        )
        
        # System with Permissions and Sub-menus
        self.register_navigation(
            label="Système",
            icon="name=settings_applications&fill=white",
            priority=40,
            required_role="admin",
            children=[
                {"label": "Paramètres", "icon": "name=settings&fill=white", "url": "/admin/base/settings"},
                {"label": "Journaux", "icon": "name=list_alt&fill=white", "url": "/admin/base/logs"}
            ]
        )

    def add_ws_function(self):
        @self.register_ws_function()
        async def ping(params, client):
            import asyncio

            await asyncio.sleep(2)

            # send broadcast message to all connected clients
            await self.app.websocket_manager.broadcast(f"Ping received from client {client.id}")
           
            await asyncio.sleep(2)

            await self.app.websocket_manager.send_to(client.id, f"Direct response to client {client.id}")

            return {"message": "pong", "received": params}

        @self.register_ws_function("base.ping")
        async def ping(params, client):
            await asyncio.sleep(2)

            # send broadcast message to all connected clients
            await self.app.websocket_manager.broadcast(f"Ping received from client {client.id}")
           
            await asyncio.sleep(2)

            await self.app.websocket_manager.send_to(client.id, f"Direct response to client {client.id}")

            return {"message": "pong", "received": params}
        
    def add_middlewares(self):
        def auth_required_middleware(router:WebRouter):
            user = router.get_session("user_payload")
            if not user:
                return router.redirect("/login") 
            payload = json.loads(user)
            router.set_scope_attr("user_payload", payload)

        def guest_only_middleware(router:WebRouter):
            user = router.get_session("user_payload")

            if user:
                return router.redirect("/")
                
        def api_auth_required_middleware(router:APIRouter):
            payload = None

            user = router.get_session("user_payload")

            if user:
                payload = json.loads(user)
                return None
            
            auth_header = router.get_header("Authorization")

            if auth_header and auth_header.startswith("Bearer "):
                jwt_token = auth_header.split(" ")[1]
                
                payload = router.jwt_decode(jwt_token)
                
                if payload:
                    router.set_scope_attr("user_payload", payload)
                    return None
                
            return router.render_json({"error": "Unauthorized"}, status_code=401)
            
        def api_guest_only_middleware(router:APIRouter):
            user = router.get_session("user_payload")

            if user:
                return router.render_json({"error": "Unauthorized"}, status_code=400)
            
            if router.get_header("Authorization"):
                return router.render_json({"error": "Unauthorized"}, status_code=400)
            
        def admin_only_middleware(router:WebRouter):
            user = router.get_scope_attr("user_payload")

            if not user or user.get("role") != "admin":
                return router.redirect("/")

        def api_admin_only_middleware(router:APIRouter):
            user = router.get_scope_attr("user_payload")

            if not user or user.get("role") != "admin":
                return router.render_json({"error": "Unauthorized"}, status_code=403)
            
        def deny_iframe_middelware(response: Response) -> Response:
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        
        def check_maintenance_middleware():
            if not self.app.config.allow_request:
                return "Service Unavailable for maintenance", 503

        self.register_middlewares({
            "auth_required": auth_required_middleware,
            "guest_only": guest_only_middleware,
            "api_auth_required": api_auth_required_middleware,
            "api_guest_only": api_guest_only_middleware,
            "deny_iframe": deny_iframe_middelware,
            "check_maintenance": check_maintenance_middleware,
            "admin_only": admin_only_middleware,
            "api_admin_only": api_admin_only_middleware,
        })
        
module = Base(
    name="base", 
    router_name="base", 
)