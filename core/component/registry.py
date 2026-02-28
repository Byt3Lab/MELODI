from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from core import Application

class Registry:
    """
    Central Registry (Le Chef d'Orchestre)
    Decouples the Application Shell from the Modules.
    Manages Injection Zones (Ancres) where modules can inject configuration.
    Supports cross-module navigation nesting via parent_id.
    """
    def __init__(self, app: Application):
        self.app = app
        # Format: {"zone_name": {"module_name": [items or callables...]}}
        self.zones: dict[str, dict[str, list[dict | Callable]]] = {
            "navigation": {},
            "dashboard": {},
            "statusbar": {}
        }

    def register(self, zone: str, module_name: str, item: dict | Callable):
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

    def get_zone(self, zone: str, **context) -> list[dict]:
        """
        Retrieve all items mapped to a specific zone, sorted by priority (if provided).
        Evaluates callbacks dynamically, then resolves parent_id references to create
        a nested navigation tree (cross-module injection).
        """
        if zone not in self.zones:
            return []

        all_items = []
        for module_name, items in self.zones[zone].items():
            for item in items:
                try:
                    # Evaluate the item if it's a callback function
                    evaluated_item = item(**context) if callable(item) else item
                    
                    if evaluated_item is None:
                        continue
                        
                    # Callbacks can return a single dict or a list of dicts
                    if isinstance(evaluated_item, list):
                        all_items.extend(evaluated_item)
                    elif isinstance(evaluated_item, dict):
                        all_items.append(evaluated_item)
                except Exception as e:
                    print(f"Error evaluating registry item in module {module_name} for zone {zone}: {e}")

        # Sort by priority, highest first (default 0)
        all_items = sorted(all_items, key=lambda x: x.get("priority", 0), reverse=True)

        # --- Navigation Hook: parent_id merging ---
        if zone == "navigation":
            all_items = self._resolve_parent_ids(all_items)

        return all_items

    def _resolve_parent_ids(self, items: list[dict]) -> list[dict]:
        """
        Post-processing step: items with a 'parent_id' are removed from the root
        and injected into the 'children' list of the item whose 'id' matches parent_id.
        Allows cross-module navigation injection without editing another module's code.
        """
        # Build an index: id -> item for fast lookup
        id_index: dict[str, dict] = {}
        for item in items:
            nav_id = item.get("id")
            if nav_id:
                if "children" not in item:
                    item["children"] = []
                id_index[nav_id] = item

        # Separate root items from injected (parent_id) items
        root_items = []
        pending = []

        for item in items:
            if item.get("parent_id"):
                pending.append(item)
            else:
                root_items.append(item)

        # Inject pending items into their parent's children list
        for item in pending:
            parent_id = item["parent_id"]
            parent = id_index.get(parent_id)
            if parent is not None:
                parent.setdefault("children", []).append(item)
            else:
                # Parent not found: fall back to root level with a warning
                print(f"[Registry] Warning: parent_id='{parent_id}' not found. Adding to root.")
                root_items.append(item)

        return root_items
