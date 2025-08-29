"""
An entity type
"""
import enum
class Type(enum):
    """ The type an entity can be """
    "Person" = 0,
    "Place" = 1,
    "Event" = 2,


class Entity():
    def __init__(self, names: list[str], translation, description, type: enum):
        self.names=names
        self.translation=translation
        self.description=description
        self.type=type

    def add_names(self, names):
        new_names = self.names.append(names)
        self.names = new_names
