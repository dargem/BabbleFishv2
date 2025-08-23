"""Language detection node for the translation workflow."""

from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

from ..models import TranslationState
from ..config import config


def language_detector_node(state: TranslationState) -> dict:
    """Detect the language of the input text.

    Args:
        state: Current translation state containing the text to analyze

    Returns:
        Dictionary with detected language
    """
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
