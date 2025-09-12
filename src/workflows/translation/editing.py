"""Editing nodes for the translation workflow."""

# type hints
from __future__ import annotations
from src.providers import LLMProvider

# imports
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from ..states import TranslationState
from src.utils import parse_tagged_content, format_text_with_tags, reconstruct_text


class JuniorEditor:
    """Evaluates and provides feedback on translation quality"""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def review_translation(self, state: TranslationState) -> dict:
        """Evaluate and provide feedback on translation quality.

        Args:
            state: Current translation state

        Returns:
            Dictionary with feedback
        """
        print("Junior editor reviewing...")

        prompt = PromptTemplate(
            input_variables=["text", "translation"],
            template="""
            Evaluate the quality of the following translation for the text.
            Be highly critical in your evaluation, you only want the very best.
            Be harsh but reasonable.
            If it is of high enough quality return the words "approved response accepted", review by the following:
            - readability
            - fluency
            - reading level
            - consistency of terminology
            - semantic accuracy
            Produce a list of specific errors/suggestions with justifications and avoid a general conclusion.
            Original Text: {text}
            Translation for assessment: {translation}
            """,
        )

        message = HumanMessage(
            content=prompt.format(translation=state["translation"], text=state["text"])
        )

        feedback = self.llm_provider.invoke([message]).strip()
        return {"feedback": feedback}


class FluencyEditor:
    """Edits translation for improved fluency and flow"""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def improve_fluency(self, state: TranslationState) -> dict:
        """Edit translation for improved fluency and flow.

        Args:
            state: Current translation state

        Returns:
            Dictionary with fluent translation
        """
        print("Improving fluency...")

        # Split text into paragraphs and create indexed format
        split_text = state["translation"].split("\n\n")
        keyed_text = {edit_index: text for edit_index, text in enumerate(split_text)}
        tag_formatted_input = format_text_with_tags(keyed_text)

        prompt = PromptTemplate(
            template="""
            You are a professional proofreader. 
            Your job is to read for rhythm, voice, and narrative flow.
            You'll focus on the lyrical quality of the prose, ensuring the story unfolds with a natural, compelling pace.
            You will refine sentence structure, word choice, and aesthetics of form to enhance the reader's immersion in the world the author has built.
            You will make sure the author's voice is consistent and strong, and that every word serves the story without disrupting the narrative's pulse.
            Create as many improvements as you can. 
            
            The text is divided into paragraphs inside <index N> ... </index N> tags.  
            For any index where you see room for improvement, output ONLY the improved version inside the same tags.  
            Do not output unchanged indices. Do not add explanations or commentary.  
            It is acceptable to split a long sentence into multiple sentences inside an index if it improves clarity.  
            
            Example:
            Input:
            <index 5>
            He placed the card upon the desk and once again closed his eyes, silently reciting in his heart a prayer.
            </index 5>

            Output:
            <index 5>
            Placing the card upon the desk, he closed his eyes once more, silently reciting a prayer in his heart.
            </index 5>

            
            The input of tagged text for proofreading is below, output in formatting described above:
            {tag_formatted_input}
            """
        )

        message = HumanMessage(
            content=prompt.format(tag_formatted_input=tag_formatted_input)
        )
        unparsed_fluency_fixed_text = self.llm_provider.invoke([message])

        # Parse the improved content and merge with original
        improved_content = parse_tagged_content(unparsed_fluency_fixed_text)

        # Update the keyed_text with improvements
        for idx, content in improved_content.items():
            if idx in keyed_text:
                keyed_text[idx] = content

        # Reconstruct the full text
        fluency_processed_text = reconstruct_text(keyed_text)

        return {"fluent_translation": fluency_processed_text}
