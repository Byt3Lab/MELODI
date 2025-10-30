from core import Module

class ModuleCRM(Module):
    def load(self):
        def index():
            return self.router.render_template("indedx.html")
        self.router.add_route("/crm", methods=["GET"])(index)
        
        super().load()

module = ModuleCRM(
    name="crm", router_name="crm", version="0.1"
)