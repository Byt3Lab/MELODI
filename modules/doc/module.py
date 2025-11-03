from core import Module

class MelodiDoc(Module):
    def load(self):
        def home():
            return self.router.render_template("index.html")
        
        self.app.home_page_manager.register_home_page("melodi_doc", home)

        @self.router.add_route("/doc", methods=["GET"])
        def index():
            return self.router.render_template("index.html")
        
        super().load()

module = MelodiDoc(
    name="melodi doc" , router_name="melodi_doc", version="0.1"
)