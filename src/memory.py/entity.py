"""
An entity type
"""

from enum import Enum


class EntityType(Enum):
    """The type an entity can be"""

    PERSON = 0
    PLACE = 1
    EVENT = 2


class Entity:
    def __init__(
        self, names: list[str], translation, description, type_: EntityType, chapter_idx
    ):
        self.names = names
        self.translation = translation
        self.description = description
        self.type = type_
        self.chapter_idx = chapter_idx

    def add_names(self, new_names: list[str]):
        self.names.extend(new_names)
