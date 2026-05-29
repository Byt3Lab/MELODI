import inspect

class ActionManager:
    def __init__(self):
        self._actions = {}

    def register_action(self, module_name: str, action_name: str, action_func):
        if not inspect.iscoroutinefunction(action_func):
            raise ValueError(f"L'action '{action_name}' doit être une fonction asynchrone (async def).")
        if module_name not in self._actions:
            self._actions[module_name] = {}
        if action_name in self._actions[module_name]:
            raise ValueError(f"L'action '{action_name}' existe déjà pour le module '{module_name}'.")
        self._actions[module_name][action_name] = action_func

    async def execute_action(self, module_name: str, action_name: str, payload:dict):
        if module_name in self._actions and action_name in self._actions[module_name]:
            return await self._actions[module_name][action_name](payload)
        else:
            raise ValueError(f"Action '{action_name}' non trouvée pour le module '{module_name}'.")

    def remove_action(self, module_name: str, action_name: str):
        """Supprime une action spécifique d'un module."""
        if module_name in self._actions and action_name in self._actions[module_name]:
            del self._actions[module_name][action_name]

    def clear_actions(self, module_name: str = None):
        """Supprime toutes les actions. Si un module_name est fourni, ne supprime que celles du module."""
        if module_name:
            self._actions.pop(module_name, None)
        else:
            self._actions.clear()