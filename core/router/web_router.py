from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from .router import Router
from core.utils import path_exist, read_file

if TYPE_CHECKING:
    from core import Application
    from core.module import Module

class WebRouter(Router):
    def __init__(self, name:str, app:Application, module:Module|None, template_folder=None):
        self.template_folder = template_folder
        self.dirname_module = ""
        self._context_processors: list[Callable] = []

        from core.module import Module

        if isinstance(module, Module):
            self.dirname_module = module.dirname
        
        super().__init__(app=app, name=name, module=module)
    
    def add_context_processor(self, processor: Callable) -> Callable:
        """Enregistre un processeur de contexte propre à cette instance du router.

        Le processeur doit être un callable (sync ou async) sans arguments qui
        retourne un dict. Ces données seront automatiquement fusionnées dans le
        contexte de chaque rendu de template effectué via cette instance.

        Usage ::

            @router.add_context_processor
            async def inject_user():
                return {"current_user": get_current_user()}
        """
        self._context_processors.append(processor)
        return processor

    async def _build_context(self, context: dict) -> dict:
        """Fusionne le contexte passé avec les données retournées par les processeurs."""
        import asyncio
        merged = {}
        for processor in self._context_processors:
            if asyncio.iscoroutinefunction(processor):
                extra = await processor()
            else:
                extra = processor()
            if isinstance(extra, dict):
                merged.update(extra)
        merged.update(context)  # les valeurs explicites ont la priorité
        return merged

    async def render_template(self, template_name: str, **context):
        from quart import render_template
        
        if not self.dirname_module == "":
            template_name = self.dirname_module + "/" + template_name

        return await render_template(template_name, **await self._build_context(context))
    
    async def render_template_(self, template_name: str, **context):
        from quart import render_template

        return await render_template(template_name, **await self._build_context(context))
    
    async def render_template_string(self, template_string: str, **context):
        from quart import render_template_string
        return await render_template_string(template_string, **await self._build_context(context))
    
    async def render_template_from_file(self, path_file: str, **context):
        template_string = ""
        if path_exist(path_file):
            template_string = read_file(path_file=path_file)
        return await self.render_template_string(template_string, **await self._build_context(context))