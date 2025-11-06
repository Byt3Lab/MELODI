from __future__ import annotations

import threading

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.application import Application

class TimerManager:
    def __init__(self, app:Application | None = None):
        self.app = app

    def set_timeout(self, func, delay, *args, **kwargs):
        """
        Exécute une fonction une seule fois après un délai (ms)
        """
        timer = threading.Timer(delay / 1000, func, args, kwargs)
        timer.start()
        return timer

    def set_interval(self, func, interval, *args, **kwargs):
        """
        Exécute une fonction de manière répétée toutes les X ms
        """
        def wrapper():
            func(*args, **kwargs)
            self.set_interval(func, interval, *args, **kwargs)
        
        timer = threading.Timer(interval / 1000, wrapper)
        timer.start()
        return timer

    def clear_timer(self, timer: threading.Timer):
        """
        Annule un timer (timeout ou interval)
        """
        timer.cancel()


# tm = TimerManager()

# ✅ Exécuter une seule fois après 2 secondes
# tm.set_timeout(lambda: print("Hello après 2s"), 2000)

# ✅ Répéter toutes les 3 secondes
# interval = tm.set_interval(lambda: print("Tick"), 3000)

# ✅ Arrêter après 10 secondes
# tm.set_timeout(lambda: tm.clear_timer(interval), 10000)