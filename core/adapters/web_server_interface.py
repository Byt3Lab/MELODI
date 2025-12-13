# adapters/web_interface.py
from abc import ABC, abstractmethod

class WebServerInterface(ABC):
    @abstractmethod
    def add_route(self, path: str, handler, methods=None):
        pass

    @abstractmethod
    def run(self, host: str = "127.0.0.1", port: int = 5000):
        pass

    @abstractmethod
    def serve_static_directory(self, directory: str, path: str):
        pass

    @abstractmethod
    def serve_template(self, template_name: str, **context):
        pass

    @abstractmethod
    def add_error_handler(self, error_code: int, handler):
        pass
    @abstractmethod
    def add_router(self, router):
        pass

    @abstractmethod
    def set_request_context(self, callback=None):
        pass
    @abstractmethod
    def get_request_context(self):
        pass
    @abstractmethod
    def before_request(self):
        pass
    @abstractmethod
    def after_request(self):
        pass