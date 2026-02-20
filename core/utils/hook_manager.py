class HookManager:
    def __init__(self):
        self._hooks = {}

    def register_hook(self, hook_name, func):
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(func)

    def execute_hook(self, hook_name, *args, **kwargs):
        if hook_name in self._hooks:
            for func in self._hooks[hook_name]:
                func(*args, **kwargs)