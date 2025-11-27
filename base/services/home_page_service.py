from core.service import Service

class HomePageService(Service):
    def on(self, home_page):
        self.app.home_page_manager.on(name_module=home_page)
        return self.response()
    
    def clear(self):
        self.app.home_page_manager.clear()
        return self.response()
