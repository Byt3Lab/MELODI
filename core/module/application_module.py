from .module import Module

class ApplicationModule(Module):
    def __init__(self, name:str, router_name:str):
        super().__init__(type_module="APPLICATION", name=name, router_name=router_name)

    def render_widget_template(self, template_name:str, **context):
        from os.path import join, exists

        """Render un template de widget."""
        PATH_DIR_RACINE = self.app.config.PATH_DIR_RACINE

        if self.dirname == "base":
            PATH_DIR_TEMPLATE = join(PATH_DIR_RACINE, 'base', 'widgets', template_name+".html")
        else:
            PATH_DIR_TEMPLATE = join(PATH_DIR_RACINE, self.dirname, 'widgets', template_name+".html")

        if exists(PATH_DIR_TEMPLATE):
            read_file = open(PATH_DIR_TEMPLATE, "r")
            return read_file.read()
        else:
            return None
  