"""The state inputs for workflows"""
# TODO short term memory after database is dealt with

from typing import TypedDict, List
from src.core import Entity, Triplet


class IngestionState(TypedDict):
    """
    State object for ingestion workflow

    Attributes:
        text: The original text to be translated
        entities: List of entities detected
        new_entities: New entities in the text detected
        triplets: Subject Object Predicate Triplets extracted from text
    """

    text: str
    entities: List[Entity]
    new_entities: List[Entity]
    triplets: List[Triplet]


class TranslationState(TypedDict):
    """
    State object for the translation workflow.

    Attributes:
        text: The original text to be translated
        language: The detected language of the original text
        translation: The current translation
        fluent_translation: The final fluency-optimized translation
        feedback: Feedback from the junior editor
        feedback_rout_loops: Number of feedback loops completed
    """

    text: str
    style_guide: str
    language: str
    translation: str
    fluent_translation: str
    feedback: str
    feedback_rout_loops: int
