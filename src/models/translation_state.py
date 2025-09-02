"""State for the translation workflow"""

from typing import TypedDict


class TranslationState(TypedDict):
    """State object for the translation workflow.

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
