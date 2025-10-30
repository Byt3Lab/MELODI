from core import Module
from core.utils import join_paths

class ModuleHR(Module):
    def load(self):
        def home():
            return self.router.render_template("home.html")
        
        self.app.home_page_manager.register_home_page("web_site", home)

        @self.router.add_route("/hr", methods=["GET"])
        def index():
            return self.router.render_template("index.html")
        
        super().load()

module = ModuleHR(
    name="web site" , router_name="web_site", version="0.1"
)