"""State for the ingestion workflow"""

from typing import TypedDict, List, Tuple
from . import Entity


class IngestionState(TypedDict):
    """State object for ingestion workflow

    Attributes:
        text: The original text to be translated
        entities: List of entities detected
        new_entities: New entities in the text detected
        triplets: Subject Object Predicate Triplets extracted from text
    """

    text: str
    entities: List[Entity]
    new_entities: List[Entity]
    triplets: List[Tuple[str, str, str]]

