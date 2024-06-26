"""
This type stub file was generated by pyright.
"""

from . import ModelDecoder

class Mesh:
    def __init__(self, name) -> None:
        ...
    


def load_material_library(filename): # -> dict[Any, Any]:
    ...

def parse_obj_file(filename, file=...):
    ...

class OBJModelDecoder(ModelDecoder):
    def get_file_extensions(self): # -> list[str]:
        ...
    
    def decode(self, filename, file, batch, group=...): # -> Model:
        ...
    


def get_decoders(): # -> list[OBJModelDecoder]:
    ...

def get_encoders(): # -> list[Any]:
    ...

