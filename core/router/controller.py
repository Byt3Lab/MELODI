from .router import Router
from .web_router import WebRouter
from .api_router import APIRouter

class Controller:
    def __init__(self, router:Router):
        self.app = router.app
        self.module = router.module

    def load(self):
        pass


class WebController(Controller):
    def __init__(self, router:WebRouter):
        self.router = router
        super().__init__(router)

class APIController(Controller):
    def __init__(self, router:APIRouter):
        self.router = router
        super().__init__(router)