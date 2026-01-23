import asyncio
import inspect
from functools import wraps

# Mocking the Router class structure from core/router/router.py
class Router:
    def add_route(self, path: str):
        def decorator(f):
            print(f"DEBUG: Processing function {f.__name__}")
            print(f"DEBUG: asyncio.iscoroutinefunction(f) = {asyncio.iscoroutinefunction(f)}")
            print(f"DEBUG: inspect.iscoroutinefunction(f) = {inspect.iscoroutinefunction(f)}")
            
            if asyncio.iscoroutinefunction(f):
                print("DEBUG: Detected as ASYNC")
                @wraps(f)
                async def wrapper(*args, **kwargs):
                    return await f(*args, **kwargs)
                return wrapper
            else:
                print("DEBUG: Detected as SYNC")
                @wraps(f)
                def wrapper(*args, **kwargs):
                    return f(*args, **kwargs)
                return wrapper
        return decorator

# Mocking the usage in Application.register_route_not_found
async def main():
    router = Router()

    async def api_route_not_found_path(path):
        return {"status": "ok"}, 200

    print("\n--- Testing api_route_not_found_path ---")
    decorated = router.add_route("/<path:path>")(api_route_not_found_path)
    
    if asyncio.iscoroutinefunction(decorated):
        print("Result: Decorated function is ASYNC")
    else:
        print("Result: Decorated function is SYNC")

if __name__ == "__main__":
    asyncio.run(main())
