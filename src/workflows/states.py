"""The state inputs for workflows"""
# TODO short term memory after database is dealt with

from typing import TypedDict, List
from src.core import Entity, InputTriplet, Genre, LanguageType


class AnnotationState(TypedDict):
    """
    State object for the annotation workflow

    Attributes:
        text: The original text for annotation
        keyword_replaced_text: The original text with translation name tags inside
        text_database_tagged: Translation tagged text with translation tags inside
        header: A header for a chapter informing translation
    """

    text: str
    keyword_replaced_text: str
    text_database_tagged: str
    header: str


class SetupState(TypedDict):
    """
    State object for setup workflow

    Attributes:
        text: The original text for classification
        language: Language of the text
        genres: List of genres of the text
        style_guide: Description of what a translators style should be
        tags: List of content tags extracted from the text
        all_chapters: List of all chapters for novel-level processing
    """

    text: str
    language: LanguageType
    genres: List[Genre]
    style_guide: str
    tags: List[str]
    all_chapters: List[str]


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
    triplets: List[InputTriplet]


class TranslationState(TypedDict):
    """
    State object for the translation workflow.

    Attributes:
        text: The original text to be translated
        language: The original texts language
        translation: The current translation
        fluent_translation: The final fluency-optimized translation
        feedback: Feedback from the junior editor
        feedback_rout_loops: Number of feedback loops completed
    """

    text: str
    language: str
    translation: str
    fluent_translation: str
    feedback: str
    feedback_rout_loops: int
