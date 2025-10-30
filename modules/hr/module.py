from core import Module
from core.utils import join_paths

class ModuleHR(Module):
    def load(self):
        @self.app.event_listener.add_event_listener("hi")
        def h():
            print("hiii from hr")

        def home():
            return self.router.render_template_string("{% extends t %} ", t="base/components/layout_admin.html",hide_header=True)
        

        self.app.home_page_manager.register_home_page("hr", home)

        @self.router.add_route("/hr", methods=["GET"])
        def index():
            return self.router.render_template("index.html")
        
        super().load()

module = ModuleHR(
    name="hr" , router_name="hr", version="0.1"
)