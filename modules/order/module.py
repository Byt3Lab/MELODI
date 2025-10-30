from core import Module

class ModuleOder(Module):
    def load(self):
        def index():
            return self.router.render_template("index.html")
        self.router.add_route("/order", methods=["GET"])(index)
        
        super().load()

module = ModuleOder(
    name="oder", router_name="oder", version="0.1"
)