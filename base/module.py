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

        self.register_dashboard_widget(
            title="Base Widget",
            component=self.base_widget,
            dimensions={"w": 4, "h": 2},
            priority=10
        )
        
        # ------------------------------------------------------------------
        # Contribution Registry: Layout Injection
        # ------------------------------------------------------------------
        
        # Dashboard item
        self.register_navigation(label="Tableau de bord", icon="fas fa-chart-pie", url="/admin", priority=100)
        
        # Gestion with Sub-menus
        self.register_navigation(
            label="Gestion",
            icon="fas fa-briefcase",
            priority=90,
            children=[
                {"label": "Utilisateurs", "icon": "fas fa-users", "url": "/admin/users"},
                {"label": "Modules", "icon": "fas fa-cubes", "url": "/admin/modules"},
                {"label": "Paramètres globaux", "icon": "fas fa-sliders-h", "url": "/admin/settings"},
                {"label": "Mise à jour", "icon": "fas fa-sliders-h", "url": "/admin/update"}
            ]
        )
        
        # System with Permissions and Sub-menus
        self.register_navigation(
            label="Système",
            icon="fas fa-cogs",
            priority=40,
            required_role="admin",
            children=[
                {"label": "Paramètres", "icon": "fas fa-cog", "url": "/admin/settings"},
                {"label": "Journaux", "icon": "fas fa-list-alt", "url": "/admin/logs"}
            ]
        )

        # StatusBar Zone (Top Admin Header)
        ws_status_html = """
        <div id="ws-status" class="d-flex align-items-center gap-2 px-2 py-1 rounded-pill bg-light border" title="WebSocket Status">
            <span class="ws-dot" style="width: 8px; height: 8px; border-radius: 50%; background-color: #94a3b8; display: inline-block;"></span>
            <span class="ws-text small text-muted fw-medium" style="font-size: 0.7rem;">Connecting...</span>
        </div>
        """
        self.register_statusbar_item(component=ws_status_html, priority=100)

        @self.register_ws_function()
        async def ping(params, client):
            import asyncio

            await asyncio.sleep(2)

            # send broadcast message to all connected clients
            await self.app.websocket_manager.broadcast(f"Ping received from client {client.id}")
           
            await asyncio.sleep(2)

            await self.app.websocket_manager.send_to(client.id, f"Direct response to client {client.id}")

            return {"message": "pong", "received": params}

        # ------------------------------------------------------------------
        # Context Processor: User info available in all templates
        # ------------------------------------------------------------------

        self.add_context_processor(self.inject_user_context)
        async def inject_user_context():
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

            def current_user():
                """Retourne le dict complet du payload utilisateur, ou None."""
                return user

            def user_is_authenticated():
                """Retourne True si un utilisateur est connecté, False sinon."""
                return user is not None

            def user_role():
                """Retourne le rôle de l'utilisateur (ex. 'admin', 'user') ou None."""
                return user.get("role") if user else None

            def user_permissions():
                """Retourne la liste des permissions de l'utilisateur, ou []."""
                return user.get("permissions", []) if user else []

            return {
                "current_user":          current_user,
                "user_is_authenticated": user_is_authenticated,
                "user_role":             user_role,
                "user_permissions":      user_permissions,
            }

        self.register_middlewares({
            "auth_required": self.auth_required_middleware,
            "guest_only": self.guest_only_middleware,
            "api_auth_required": self.api_auth_required_middleware,
            "api_guest_only": self.api_guest_only_middleware,
            "deny_iframe": self.deny_iframe_middelware,
            "check_maintenance": self.check_maintenance_middleware,
            "admin_only": self.admin_only_middleware,
            "api_admin_only": self.api_admin_only_middleware,
        })

    def add_404_not_found(self):
        PATH_DIR_BASE_MODULE = self.app.config.PATH_DIR_BASE_MODULE
        self.app.config.path_template_404_not_found = join_paths(PATH_DIR_BASE_MODULE, 'templates', 'base', '404.html')
        
    def base_widget(self):
        return "<div><h3>Base Widget</h3><p>This is a sample widget from the Base module.</p></div>"
    
    def auth_required_middleware(self,router:WebRouter):
        user = router.get_session("user_payload")
        if not user:
            return router.redirect("/login") 
        payload = json.loads(user)
        router.set_scope_attr("user_payload", payload)

    def guest_only_middleware(self, router:WebRouter):
        user = router.get_session("user_payload")

        if user:
            return router.redirect("/")
            
    def api_auth_required_middleware(self,router:APIRouter):
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
        
    def api_guest_only_middleware(self, router:APIRouter):
        user = router.get_session("user_payload")

        if user:
            return router.render_json({"error": "Unauthorized"}, status_code=400)
        
        if router.get_header("Authorization"):
            return router.render_json({"error": "Unauthorized"}, status_code=400)
        
    def admin_only_middleware(self, router:WebRouter):
        user = router.get_scope_attr("user_payload")

        if not user or user.get("role") != "admin":
            return router.redirect("/")

    def api_admin_only_middleware(self, router:APIRouter):
        user = router.get_scope_attr("user_payload")

        if not user or user.get("role") != "admin":
            return router.render_json({"error": "Unauthorized"}, status_code=403)
        
    def deny_iframe_middelware(self,response: Response) -> Response:
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    def check_maintenance_middleware(self):
        if not self.app.config.allow_request:
            return "Service Unavailable for maintenance", 503

module = Base(
    name="base", 
    router_name="base", 
)