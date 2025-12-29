from typing import Any
class EventListener:
    def __init__(self):
        self._events:dict[str,dict[str,list]] = {}

    def add_event_listener(self, module_name:str, event_name: str, callback):
        """Ajoute un callback pour un événement."""
        if module_name not in self._events:
            self._events[module_name] = {}
            self._events[module_name][event_name] = []
        elif event_name not in self._events[module_name]:
            self._events[module_name][event_name] = []

        self._events[module_name][event_name].append(callback)

    def remove_event_listener(self, module_name:str, event_name: str, callback):
        """Supprime un callback d’un événement."""
        if module_name in self._events:
            if event_name in self._events[module_name]:
                if callback in self._events[module_name][event_name]:
                    self._events[module_name][event_name].remove(callback)

    def clear_event_listeners(self, module_name:str, event_name: str):
        """Supprime tous les callbacks d’un événement."""
        if module_name in self._events:
            if event_name in self._events[module_name]:
                self._events[module_name][event_name] = []

    def remove_all_listeners(self):
        """Supprime tous les callbacks de tous les événements."""
        self._events.clear()
        
    def notify_event(self, module_name:str, event_name: str, data: Any = None):
        """Déclenche l’événement et exécute tous les callbacks associés."""

        for callback in self._events.get(module_name, {}).get(event_name, []):
            callback(data)
