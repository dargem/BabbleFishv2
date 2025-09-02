"""State for the ingestion workflow"""

from typing import TypedDict, List, Tuple
from enum import Enum


class EntityType(Enum):
    """The type an entity can be"""

    PERSON = 0
    PLACE = 1
    EVENT = 2


class Entity:
    """An entity"""

    def __init__(self, names: list[str], translation, description, chapter_idx):
        self.names = names
        self.translation = translation
        self.description = description
        self.chapter_idx = chapter_idx

    def add_names(self, new_names: list[str]):
        self.names.extend(new_names)


class Person(Entity):
    """Child of an entity"""

    def __init__(
        self,
        names: list[str],
        translation,
        description,
        chapter_idx: int,
        age: int = None,
        gender: str = None,
    ):
        super().__init__(names, translation, description, chapter_idx)
        self.age = age
        self.gender = gender


class Triplet:
    """Triplet generation"""

    pass


class IngestionState(TypedDict):
    """State object for ingestion workflow

    Attributes:
        text: The original text to be translated
        entities: List of entities detected
        new_entities: New entities in the text detected
        triplets: Subject Object Predicate Triplets extracted from text
    """

    text: str
    triplets: List[Tuple[str, str, str]]


person = Person(["Test"], "testing", "about a test", 10, 20, "male")
print(person.__dict__)
