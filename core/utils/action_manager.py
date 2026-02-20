class ActionManager:
    def __init__(self):
        self._actions = {}

    def register_action(self, action_name, action_func):
        self._actions[action_name] = action_func

    def execute_action(self, action_name, *args, **kwargs):
        if action_name in self._actions:
            return self._actions[action_name](*args, **kwargs)
        else:
            raise ValueError(f"Action '{action_name}' not found.")