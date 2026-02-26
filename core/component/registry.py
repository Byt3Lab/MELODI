from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core import Application

class Registry:
    """
    Central Registry (Le Chef d'Orchestre)
    Decouples the Application Shell from the Modules.
    Manages Injection Zones (Ancres) where modules can inject configuration.
    """
    def __init__(self, app: Application):
        self.app = app
        # Format: {"zone_name": {"module_name": [items...]}}
        self.zones: dict[str, dict[str, list[dict]]] = {
            "navigation": {},
            "dashboard": {},
            "statusbar": {}
        }

    def register(self, zone: str, module_name: str, item: dict):
        """
        Register a configuration item into a specific zone for a given module.
        """
        if zone not in self.zones:
            self.zones[zone] = {}
        
        if module_name not in self.zones[zone]:
            self.zones[zone][module_name] = []
            
        self.zones[zone][module_name].append(item)

    def unregister(self, module_name: str):
        """
        Remove all configuration items associated with a given module across all zones.
        Called when a module is uninstalled or disabled.
        """
        for zone_name in self.zones:
            if module_name in self.zones[zone_name]:
                del self.zones[zone_name][module_name]

    def get_zone(self, zone: str) -> list[dict]:
        """
        Retrieve all items mapped to a specific zone, sorted by priority (if provided).
        """
        if zone not in self.zones:
            return []

        all_items = []
        for module_name, items in self.zones[zone].items():
            all_items.extend(items)
            
        # Sort by priority, highest first (default 0)
        return sorted(all_items, key=lambda x: x.get("priority", 0), reverse=True)
