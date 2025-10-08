"""Language detection node for the translation workflow."""

# type hints
from __future__ import annotations

# imports
import logging
from ..states import SetupState
from lingua import LanguageDetectorBuilder, Language
from src.core import LanguageType

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detects the language of input text"""

    def __init__(self):
        logger.debug("Initializing language detector")

        languages_mapped = {lang.value: lang.name for lang in LanguageType}

        self.detector = LanguageDetectorBuilder.from_languages(
            *languages_mapped.keys()
        ).build()

    def detect_language(self, state: SetupState) -> dict:
        """Detect the language of the input text.

        Args:
            state: Current translation state containing the text to analyze

        Returns:
            Dictionary with detected language
        """
        logger.debug("Detecting language for text of length %d", len(state["text"]))

        detected = self.detector.detect_language_of(state["text"])

        # Convert lingua.Language to LanguageType enum
        language_type = None
        for lang_type in LanguageType:
            if lang_type.value == detected:
                language_type = lang_type
                break

        if language_type is None:
            logger.warning(
                "Detected language %s not supported, defaulting to English", detected
            )
            language_type = LanguageType.ENGLISH

        logger.info("Detected language: %s", language_type)
        return {"language": language_type}


'''
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from ...config import config

# LLM variation, shouldn't be needed though
print("Detecting language...")

llm = config.get_llm()

prompt = PromptTemplate(
    input_variables=["text"],
    template="""
    Detect the language of the following, outputting one word.
    Text: {text}
    Language:
    """,
)

message = HumanMessage(content=prompt.format(text=state["text"]))
language = llm.invoke([message]).strip()

return {"language": language}
'''
