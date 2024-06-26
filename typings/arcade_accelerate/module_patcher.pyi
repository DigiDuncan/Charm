"""
This type stub file was generated by pyright.
"""

from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Sequence

class AutoPopulatingDictionary(dict):
    def __missing__(self, key): # -> SimpleNamespace:
        ...
    


class PatchingMetaPathFinder(MetaPathFinder):
    def __init__(self, patches) -> None:
        ...
    
    def find_spec(self, fullname: str, path: Sequence[str] | None, target: ModuleType | None = ...) -> ModuleSpec | None:
        ...
    


class PatchingLoader(Loader):
    def __init__(self, loader: Loader, patches: dict) -> None:
        ...
    
    def create_module(self, spec: ModuleSpec) -> ModuleType | None:
        ...
    
    def exec_module(self, module: ModuleType) -> None:
        ...
    


