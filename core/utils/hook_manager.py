import inspect

class HookManager:
    def __init__(self):
        self._hooks = {}

    def register_hook(self, module_name: str, hook_name: str, func):
        if not inspect.iscoroutinefunction(func):
            raise ValueError(f"Le hook '{hook_name}' doit être une fonction asynchrone (async def).")
        if module_name not in self._hooks:
            self._hooks[module_name] = {}
        if hook_name not in self._hooks[module_name]:
            self._hooks[module_name][hook_name] = []
        
        self._hooks[module_name][hook_name].append(func)

    async def execute_hook(self, module_name: str, hook_name: str, payload=None):
        """
        Exécute les hooks en mode pipeline. Chaque hook prend un "payload" 
        (objet ou dict), le modifie, et sa valeur de retour devient le payload 
        pour le hook suivant.
        """
        if module_name in self._hooks and hook_name in self._hooks[module_name]:
            for func in self._hooks[module_name][hook_name]:
                payload = await func(payload)
                
        return payload

    def remove_hook(self, module_name: str, hook_name: str, func):
        """Supprime un callback spécifique d'un hook."""
        if module_name in self._hooks and hook_name in self._hooks[module_name]:
            if func in self._hooks[module_name][hook_name]:
                self._hooks[module_name][hook_name].remove(func)

    def clear_hooks(self, module_name: str = None, hook_name: str = None):
        """Supprime les hooks. Si module_name est fourni sans hook_name, supprime tous les hooks du module."""
        if module_name:
            if hook_name:
                if module_name in self._hooks and hook_name in self._hooks[module_name]:
                    self._hooks[module_name][hook_name] = []
            else:
                self._hooks.pop(module_name, None)
        else:
            self._hooks.clear()