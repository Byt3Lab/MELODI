from base.services.install_service import InstallService
from core.router import APIController
from base.services import UserService
from base.services.module_service import ModuleService

class BaseAPIController(APIController):
    def load(self):
        self.user_service = UserService(module=self.module)
        self.module_service = ModuleService(module=self.module)
   
    async def login(self):
        req = self.router.get_request()  # Example of accessing session
        method = req.method
        user_has_auth = False

        if method == "POST":
            data = await req.json
            username = data.get("username")
            password = data.get("password")

            user_has_auth = await self.user_service.authenticate(username=username, password=password)
            
            if user_has_auth:
                token = self.router.jwt_encode(user_has_auth)
                return self.router.render_json({"message": "Login successful", "token": token}, status_code=200)
        
        return self.router.render_json({"message": "Login page"}, status_code=404)
    
    async def upload_module_to_install(self, options: dict = {}):
        request = self.router.get_request()
        files = await request.files
        file_storage = files.get("file")

        # Retrieve optional module hash from form data and attach to the file_storage
        form = await request.form
        module_hash = form.get('module_hash') if form else None
        
        try:
            if module_hash and file_storage:
                setattr(file_storage, '_module_hash', module_hash)
        except Exception:
            pass
        
        options = {
            "allow_update": options.get("allow_update", True),
            "allow_backup": options.get("allow_backup", True),
        }
        
        success, message = await self.module_service.extract_and_install_zip(file_storage, options)
        
        if success:
            return self.router.render_json({"message": message}, status_code=200)
        else:
            return self.router.render_json({"error": message}, status_code=400)
    
    async def upload_module_to_update(self):
        request = self.router.get_request()
        params = await request.params
        allow_backup =  params.get("allow_backup", False)
        return await self.upload_module_to_install(options={"allow_update": True, "allow_backup": allow_backup})

    async def upload_core_to_update(self):
        request = self.router.get_request()
        files = await request.files
        file_storage = files.get("file")
        form = await request.form
        params = await request.params
        allow_backup =  params.get("allow_backup", False)

        module_hash = form.get('module_hash') if form else None
        try:
            if module_hash and file_storage:
                setattr(file_storage, '_module_hash', module_hash)
        except Exception:
            pass
        
        success, message = await self.module_service.extract_and_update_core_zip(file_storage, options={"allow_backup": allow_backup})
        
        if success:
            return self.router.render_json({"message": message}, status_code=200)
        else:
            return self.router.render_json({"error": message}, status_code=400)
     
    async def on_module(self,mod:str):
        await self.app.module_manager.on_module(mod)

        data = {"module":mod}

        return self.render_json(data)

    async def off_module(self, mod:str):
        await self.app.module_manager.off_module(mod)
        
        data = {mod}

        return self.render_json(data)

    async def remove_module(self, mod:str):
        success, message = await self.module_service.remove_module(mod)
        
        if success:
            return self.render_json({"message": message}, status_code=200)
        else:
            return self.render_json({"error": message}, status_code=400)

    async def settings_home_page_on(self, home_page):
        self.home_page_service.on(home_page)
        return self.render_json()
    
    async def settings_home_page_clear(self):
        self.home_page_service.clear()
        return self.render_json()

    async def admin_modules(self):
        modules = self.app.module_manager.list_modules()
        modules_len= len(modules)
        data = {"modules":modules,"modules_len":modules_len}

        return self.render_json(data)
    
    async def status(self):
        return self.router.render_json(data={"status": "Admin API is working!"}, status_code=200)

    async def install(self):
        req = self.router.get_request()

        data = await req.get_json()

        install_service = InstallService(self)

        res = await install_service.install(data)

        return self.render_json(data=res.data, status_code=res.status_code)
        
    async def not_found(self,path):
        data = {"end_point_not_found":path}

        return self.router.render_json(data,status_code=404) 

    async def restart_server(self):
        await self.app.restart()
        data = {"status": "Server restarted"}
        return self.router.render_json(data=data)

    async def test_async(self):
        import asyncio
        import time
        import threading

        threading_name = threading.current_thread().name
        print(f"Thread courant: {threading_name}")
        threading_id = threading.get_ident()
        print(f"ID du thread courant: {threading_id}")
        start = time.perf_counter()
        print(f"Début de la requête à {start}")
        await asyncio.sleep(3)  # Pause asynchrone de 5 secondes
        end = time.perf_counter()
        duration = end - start
        print(f"Fin de la requête à {end}, durée : {duration:.2f} secondes")
        return self.render_json({"start": start, "end": end, "duration": f"{duration:.2f}s", "thread_name": threading_name, "thread_id": threading_id})