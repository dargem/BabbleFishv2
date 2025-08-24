"""Language detection node for the translation workflow."""
# add lingua for quick & efficient detection

from ..models import TranslationState

from lingua import LanguageDetectorBuilder, Language

def language_detector_node(state: TranslationState) -> dict:
    """Detect the language of the input text.

    Args:
        state: Current translation state containing the text to analyze

    Returns:
        Dictionary with detected language
    """

    languages_mapped = {
        Language.ENGLISH: "English", 
        Language.CHINESE: "Chinese", 
        Language.JAPANESE: "Japanese", 
        Language.KOREAN: "Korean", 
        Language.SPANISH: "Spanish", 
        Language.FRENCH: "French"
    }

    detector = LanguageDetectorBuilder.from_languages(*languages_mapped.keys()).build()

    detected = detector.detect_language_of(state["text"])

    return {"language": languages_mapped[detected]}


'''
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from ..config import config

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
