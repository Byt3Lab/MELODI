from core import Module

class ModuleSell(Module):
    def load(self):

        @self.app.event_listener.add_event_listener("hi")
        def h():
            print("hiii from sell")

        @self.router.add_route("/sell", methods=["GET"])
        def index():
            return self.router.render_template("index.html", hide_header=True, hide_footer=True)
        
        super().load()

module = ModuleSell(
    name="sell", router_name="sell", version="0.1"
)