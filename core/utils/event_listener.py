class EventListener:
    def __init__(self):
        # Dictionnaire {nom_evenement: [callbacks]}
        self._events:dict[str,list[object]] = {}

    def add_event_listener(self, event_name: str, callback):
        """Ajoute un callback pour un événement."""
        if event_name not in self._events:
            self._events[event_name] = []
        self._events[event_name].append(callback)

    def remove_event_listener(self, event_name: str, callback):
        """Supprime un callback d’un événement."""
        if event_name in self._events:
            self._events[event_name] = [
                cb for cb in self._events[event_name] if cb != callback
            ]

    def clear_event_listeners(self, event_name: str):
        """Supprime tous les callbacks d’un événement."""
        if event_name in self._events:
            self._events[event_name] = []

    def remove_all_listeners(self):
        """Supprime tous les callbacks de tous les événements."""
        self._events.clear()
        
    def notify_event(self, event_name: str, *args, **kwargs):
        """Déclenche l’événement et exécute tous les callbacks associés."""
        if event_name in self._events:
            for callback in self._events[event_name]:
                callback(*args, **kwargs)
