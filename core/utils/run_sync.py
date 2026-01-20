import asyncio

async def run_sync(func, *args, **kwargs):
    """Utilitaire pour transformer n'importe quoi en async non-bloquant"""
    return await asyncio.to_thread(func, *args, **kwargs)