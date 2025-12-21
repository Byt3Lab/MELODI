from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..module.module import Module

class Response:
    def __init__(self, data=None, status_code=200, message=""):
        self.data = data
        self.status_code = status_code
        self.message = message    

class Service:
    def __init__(self, module:Module):
        self.module = module
        self.app = self.module.app
        
    def response(self, data=None, status_code=200, message=""):
        return Response(data,status_code,message)