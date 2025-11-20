import pkgutil
import importlib
import inspect
import feedparser

from karapp.tools.rss.base import RssSearchTool

# Charger dynamiquement tous les modules du package rss
__all__ = ['get_tool_by_name', 'list_tools']

def get_tool_by_name(name: str):
    """
    Retourne la classe dont self.name == name
    """
    # Parcourir tous les sous-modules du package
    for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f"{__name__}.{module_name}")

        # Chercher les classes qui héritent de RssSearchTool
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, RssSearchTool) and obj is not RssSearchTool:
                instance = obj()
                if instance.name == name:
                    return obj

    raise ValueError(f"Aucune classe trouvée avec name='{name}'")


def list_tools():
    tools = []
    for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f"{__name__}.{module_name}")
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, RssSearchTool) and obj is not RssSearchTool:
                instance = obj()
                tools.append(instance.name)
    return tools


def get_infos(url):
    feed = feedparser.parse(url)
    return {
        'titre': feed.feed.get('title', 'Sans titre'),
        'description': feed.feed.get('subtitle', ''),
        'image': getattr(feed.feed, 'image', {}).get('href', '')
    }

def get_episodes_list(url):
    feed = feedparser.parse(url)
    return [
        {'titre': e.title, 'audio': e.enclosures[0].href if e.enclosures else None,
         'image': e.image.href if e.image else None, 'description': e.summary if e.summary else ''}
        for e in feed.entries]