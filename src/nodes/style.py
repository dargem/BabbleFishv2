"""style node to preface the translation workflow, this is only ran if style hasn't been set"""

from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

from ..models import TranslationState
from ..config import config


def style_node(state: TranslationState) -> dict:
    """
    Creates a description of the novels style, genre etc for aiding in translation style.
    Args:
        state: original text

    Returns:
        Dictionary with style guide
    """
    print("Generating style guide...")

    llm = config.get_llm()

    template = """
    You are a highly experienced literary analyst and editor. Your task is to provide a detailed style guide for a fiction text, which will be used to ensure consistency and fidelity during translation.

    Analyze the following text and provide a comprehensive breakdown of its key literary elements. Structure your response in the following sections:

    ## **1. Genre and Subgenre**
    Identify the primary and, if applicable, secondary genres (e.g., science fiction, historical fiction, fantasy, thriller, romance). Specify any subgenres (e.g., cyberpunk, cozy mystery, epic fantasy, psychological thriller) that define the text's specific conventions.

    ## **2. Literary Style and Techniques**
    Describe the author's writing style.
    - **Sentence Structure:** Is it simple and direct, or complex and ornate? Are sentences long and flowing, or short and punchy?
    - **Pacing:** Is the narrative fast-paced and action-driven, or slow and reflective?
    - **Prose Style:** Is the language poetic, academic, minimalist, or conversational? Note any distinctive uses of metaphor, simile, or symbolism.
    - **Narrative Voice:** Is the text written in the first person (I), third person (he/she), or a more unique perspective? Is the narrator reliable or unreliable?
    - **Dialogue:** Is the dialogue realistic and naturalistic, or stylized and formal? Does it reveal character, advance the plot, or both?

    ## **3. Tone and Mood**
    Characterize the overall tone and mood of the text.
    - **Tone:** Is the author's attitude humorous, serious, satirical, suspenseful, or melancholic?
    - **Mood:** What atmosphere does the text evoke for the reader? Is it tense, mysterious, romantic, or nostalgic?

    ## **4. Themes and Motifs**
    Identify the major themes explored in the text (e.g., love and loss, justice and revenge, human connection vs. technology, coming of age). Note any recurring motifs (e.g., a specific color, object, or phrase) that reinforce these themes.

    ## **5. Target Audience**
    Who is the likely target audience for this text (e.g., young adults, general adult fiction readers, fans of a specific genre)?

    ## **6. Style Recommendations for Translation**
    Based on your analysis, provide specific instructions for a translator. For example:
    - **Formal vs. Informal Language:** Should the translation favor a formal or informal register?
    - **Slang and Idioms:** Should regional slang or idiomatic expressions be preserved, adapted, or omitted?
    - **Tone Preservation:** What specific elements of the tone (e.g., dry humor, suspense) must be prioritized?

    ---
    **Text to Analyze:**
    {text}
    """

    prompt = PromptTemplate(input_variables=["text"], template=template)

    message = HumanMessage(content=prompt.format(text=state["text"]))

    style_guide = llm.invoke([message]).strip()
    return {"style_guide": style_guide}
