"""Translation node for the translation workflow."""

# type hints
from __future__ import annotations
from src.providers import LLMProvider

# imports
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from ..states import TranslationState
from textwrap import dedent


class Translator:
    """Translates text from detected language to English"""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def translate(self, state: TranslationState) -> dict:
        """Translate text from detected language to English.

        Args:
            state: Current translation state

        Returns:
            Dictionary with the translation
        """
        print("Translating text...")

        base_template = dedent("""
        You are a professional translator specialising in fiction. 
        You work with {language} to English translations and are highly proficient in localisation.
        Prioritise fluency while maintaining semantic meaning.
        Translate the following {language} text to English.
        Text: {text}
        """)

        # Check if this is a feedback iteration
        if "translation" in state and state.get("translation"):
            template = base_template + dedent("""
            Your prior translation was: 
            {translation}
            Your feedback was: 
            {feedback}
            With this feedback incorporated, create a richer response.
            Your updated translation, incorporating feedback:
            """)

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

        translation = await self.llm_provider.invoke([message])
        return {"translation": translation.strip()}
