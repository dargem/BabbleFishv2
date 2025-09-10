"""Translation node for the translation workflow."""

from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

from ..states import TranslationState
from src.config import config


def translator_node(state: TranslationState) -> dict:
    """Translate text from detected language to English.

    Args:
        state: Current translation state

    Returns:
        Dictionary with the translation
    """
    print("Translating text...")

    llm = config.get_llm()

    base_template = """
    You are a professional translator specialising in fiction. 
    You work with {language} to English translations and are highly proficient in localisation.
    Prioritise fluency while maintaining semantic meaning.
    Translate the following {language} text to English.
    Text: {text}
    """

    # Check if this is a feedback iteration
    if "translation" in state and state.get("translation"):
        template = (
            base_template
            + """
        Your prior translation was: 
        {translation}
        Your feedback was: 
        {feedback}
        With this feedback incorporated, create a richer response.
        Your updated translation, incorporating feedback:
        """
        )

        prompt = PromptTemplate(
            input_variables=["text", "language", "feedback", "translation"],
            template=template,
        )

        message = HumanMessage(
            content=prompt.format(
                language=state["language"],
                text=state["text"],
                feedback=state["feedback"],
                translation=state["translation"],
            )
        )
    else:
        # Initial translation
        template = base_template + "\n\nTranslation:"

        prompt = PromptTemplate(
            input_variables=["text", "language"],
            template=template,
        )

        message = HumanMessage(
            content=prompt.format(
                language=state["language"],
                text=state["text"],
            )
        )

    translation = llm.invoke([message]).strip()
    return {"translation": translation}
