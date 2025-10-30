from core import Module

class ModulStock(Module):
    def load(self):
        def xample_widget():
            tpl= "<div><h3>stock Widget</h3><p>This is a sample widget from the stock module.</p> {{msg}} </div>"

            return self.router.render_template_string(tpl, msg="Hello from stock widget")
        
        self.app.widget_manager.register_widget("stock", xample_widget)
    
        def index():
            return self.router.render_template("index.html")
        self.router.add_route("/stock", methods=["GET"])(index)
        
        super().load()

module = ModulStock(
    name="stock", router_name="stock", version="0.1"
)