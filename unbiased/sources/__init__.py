import importlib
import pkgutil

from unbiased.sources.base import NewsSource

def get_sources():
    for loader, name, is_pkg in pkgutil.walk_packages(__path__):
        if name != 'base':
            importlib.import_module('unbiased.sources.' + name)
    return {x.shortname.lower(): x for x in NewsSource.__subclasses__()}
