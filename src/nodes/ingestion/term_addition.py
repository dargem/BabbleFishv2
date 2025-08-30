"""entity addition node for the translation workflow, paired with the removal node"""

from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

from ...models import TranslationState
from ...config import config


def term_addition_node(state: TranslationState) -> dict:
    """Recognise entities from original text.

    Args:
        state: Current translation state

    Returns:
        Dictionary with nodes + reasoning
    """
    print("Translating text...")

    llm = config.get_llm()

    template = """
    You are a translator tasked with Named Entity Reconition, identifying named terms in the following text.
    These are terms that are likely recurring and you believe should be *consistently* translated.
    
    These entities include but are not limited to:
        - Characters (Jim, Jack Crowley etc)
        - Places (Saint Theres Church, Hogwarts etc)
        - Items (Wand)
        - Symbols 
        - Motifs
    
    Prioritise finding as many entities as you can.
    Text: {text}
    """

    prompt = PromptTemplate(input_variables=["text"], template=template)

    message = HumanMessage(content=prompt.format(text=state["text"]))

    entities = llm.invoke([message]).strip()
    return {"entities": entities}
