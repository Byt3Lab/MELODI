class BaseService:
    def response(self, data=None, status="success", code=200, message=""):
        return {
            "data": data,
            "status": status,
            "code": code,
            "message": message
        }