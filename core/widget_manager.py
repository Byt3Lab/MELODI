from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .application import Application

class WidgetManager:
    def __init__(self, app:Application | None = None):
        self.app = app
        self.widgets_on = self.app.config.widgets_on if self.app else []
        self.widgets = {}

    def register_widget(self, name: str, widget):
        self.widgets[name] = widget

    def remove_widget(self, name: str):
        if name in self.widgets:
            del self.widgets[name]  

    def list_widgets(self):
        return list(self.widgets.keys())
    
    def clear_widgets(self):
        self.widgets.clear()

    def get_widget(self, name:str):
        if name in self.widgets:
            return self.widgets[name] 
        return ""
    
    def render_widget(self, name: str):
        widget = self.get_widget(name)

        if callable(widget):
            widget = widget()

        if isinstance(widget, str):
            return widget
        else:
            return str(widget)
    
    def load_widgets_on(self):
        widgets = []

        for widget_name in self.widgets_on:
            widgets.append(self.render_widget(widget_name))

        return widgets