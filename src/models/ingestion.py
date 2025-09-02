"""State for the ingestion workflow"""

from typing import TypedDict, List
from .graph_data import Entity, Triplet
from src.knowledge_graph import KnowledgeGraphManager


class IngestionState(TypedDict):
    """State object for ingestion workflow

    Attributes:
        text: The original text to be translated
        entities: List of entities detected
        new_entities: New entities in the text detected
        triplets: Subject Object Predicate Triplets extracted from text
    """

    knowledge_graph: KnowledgeGraphManager
    text: str
    entities: List[Entity]
    new_entities: List[Entity]
    triplets: List[Triplet]
